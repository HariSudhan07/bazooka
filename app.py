# app.py

import streamlit as st
import json
from backend.ocr_service import extract_text_aws, pdf_to_image
from backend.llm_service import validate_text_with_llm
from backend.db_service import save_results, load_results
from backend.image_detecter import detect_kosher_symbol

# --------------------------
# Page Config
# --------------------------
st.set_page_config(
    page_title="Bazooka Candy - Packaging Validation",
    page_icon="📄",
    layout="centered"
)

# --------------------------
# Custom CSS for Compact & Modern UI
# --------------------------
st.markdown(
    """
    <style>
    .main-container {
        max-width: 700px;
        margin: auto;
    }
    /* Upload & input boxes */
    .stFileUploader, .stSelectbox {
        margin-bottom: 0.5rem;
    }
    .stFileUploader div[data-testid="stFileUploaderDropzone"] {
        padding: 0.5rem !important;
    }
    /* Section titles */
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 1.2rem;
        margin-bottom: 0.6rem;
        color: #2c3e50;
    }
    /* Card layout */
    .card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        background: #fdfdfd;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }
    /* Status indicators */
    .status-pass {
        background-color: #d4edda;
        color: #155724;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .status-fail {
        background-color: #f8d7da;
        color: #721c24;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    /* Report styling */
    .report-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .check-item {
        background: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .check-item.fail {
        border-left-color: #dc3545;
        background: #fff5f5;
    }
    .check-item.pass {
        border-left-color: #28a745;
        background: #f8fff8;
    }
    .error-item {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 0.75rem;
        border-radius: 6px;
        margin: 0.25rem 0;
    }
    /* Button styling - transparent pop */
    .stButton button {
        background: rgba(46, 134, 222, 0.85);
        color: white;
        border: none;
        padding: 0.6rem 1rem;
        font-weight: 500;
        border-radius: 8px;
        transition: all 0.2s ease-in-out;
    }
    .stButton button:hover {
        background: rgba(46, 134, 222, 1);
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        transform: scale(1.02);
    }
    .stButton button:active {
        transform: scale(0.98);
        background: rgba(46, 134, 222, 0.75);
    }
    </style>
    """,
    unsafe_allow_html=True
)

def display_validation_report(result_data):
    """Display validation results as a formatted report"""
    
    # Parse validation JSON
    try:
        if isinstance(result_data['validation'], str):
            # If validation is a string, try to extract JSON from it
            validation_text = result_data['validation']
            # Find JSON content between ```json and ```
            start = validation_text.find('```json\n') + 8
            end = validation_text.find('\n```', start)
            if start > 7 and end > start:
                validation_json = validation_text[start:end]
            else:
                validation_json = validation_text
            validation_data = json.loads(validation_json)
        else:
            validation_data = result_data['validation']
    except:
        st.error("❌ Could not parse validation results")
        return
    
    # Report Header
    st.markdown(f"""
    <div class='report-header'>
        <h2>📋 Package Validation Report</h2>
        <p><strong>File:</strong> {result_data['file']}</p>
        <p><strong>Check Group:</strong> {result_data['check_group']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Summary Statistics
    checks = validation_data.get('checks', [])
    passed_checks = [c for c in checks if c.get('result') == 'PASS']
    failed_checks = [c for c in checks if c.get('result') == 'FAIL']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Checks", len(checks))
    with col2:
        st.metric("✅ Passed", len(passed_checks))
    with col3:
        st.metric("❌ Failed", len(failed_checks))
    
    # Overall Status
    if len(failed_checks) == 0:
        st.success("🎉 **ALL CHECKS PASSED** - Package is compliant!")
    else:
        st.error(f"⚠️ **{len(failed_checks)} CHECK(S) FAILED** - Corrections required")
    
    # Failed Requirements Section
    if failed_checks:
        st.markdown("### ❌ Failed Requirements")
        for check in failed_checks:
            st.markdown(f"""
            <div class='check-item fail'>
                <strong>{check.get('rule', 'Unknown Rule')}</strong><br>
                <span class='status-fail'>FAIL</span><br>
                <em>{check.get('reason', 'No reason provided')}</em>
            </div>
            """, unsafe_allow_html=True)
    
    # Passed Requirements Section
    if passed_checks:
        st.markdown("### ✅ Passed Requirements")
        for check in passed_checks:
            st.markdown(f"""
            <div class='check-item pass'>
                <strong>{check.get('rule', 'Unknown Rule')}</strong><br>
                <span class='status-pass'>PASS</span><br>
                <em>{check.get('reason', 'No reason provided')}</em>
            </div>
            """, unsafe_allow_html=True)
    
    # Text Quality Issues Section
    spelling_grammar = validation_data.get('spelling_grammar', {})
    issues = spelling_grammar.get('issues', [])
    
    if issues:
        st.markdown("### 📝 Text Corrections Required")
        for issue in issues:
            st.markdown(f"""
            <div class='error-item'>
                <strong>Error:</strong> "{issue.get('ocr_text', '')}" → <strong>"{issue.get('correct_text', '')}"</strong>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No spelling or grammar issues found")
    
    # Action Items Summary
    if failed_checks or issues:
        st.markdown("### 🔧 Required Actions")
        action_count = 1
        
        for check in failed_checks:
            st.markdown(f"{action_count}. Fix: {check.get('rule', 'Unknown requirement')}")
            action_count += 1
            
        for issue in issues:
            st.markdown(f"{action_count}. Correct: '{issue.get('ocr_text', '')}' to '{issue.get('correct_text', '')}'")
            action_count += 1

# --------------------------
# Header
# --------------------------
with st.container():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.title("📄 Bazooka Candy - Packaging Validation")
    st.markdown(
        "<p style='font-size:15px; color:#555;'>Validate packaging text with AI-powered OCR & LLM checks. "
        "Upload a file, pick a check group, and get instant Summary .</p>",
        unsafe_allow_html=True
    )

# --------------------------
# Upload Section
# --------------------------
st.markdown("<div class='section-title'>📂 Upload & Options</div>", unsafe_allow_html=True)
cols = st.columns([2, 1])
with cols[0]:
    uploaded_file = st.file_uploader(
        "Upload Packaging File", 
        type=["pdf", "png", "jpg", "jpeg"], 
        label_visibility="collapsed"
    )
with cols[1]:
    check_group = st.selectbox("Check Group", ["Front", "Back", "All"])

# --------------------------
# Processing Section
# --------------------------
if uploaded_file:
    st.success(f"✅ File **{uploaded_file.name}** uploaded successfully!")

    # Save uploaded file locally
    with open("temp.pdf" if uploaded_file.name.endswith(".pdf") else "temp.png", "wb") as f:
        f.write(uploaded_file.read())
    file_path = f.name

    if st.button("🚀 Run", use_container_width=True):
        # OCR
        with st.spinner("🔍 Extracting text..."):
            if file_path.endswith(".pdf"):
                image_path = pdf_to_image(file_path, "temp.png")
            else:
                image_path = file_path
            ocr_text = extract_text_aws(image_path)

        with st.expander("📝 View OCR Extracted Text"):
            st.text_area("OCR Output", ocr_text, height=180)

         # ✅ Kosher Symbol Detection
        with st.spinner("🔍 Detecting Kosher Symbols..."):
            symbols_result = detect_kosher_symbol(image_path)
        
        st.subheader("🔯 Kosher Symbol Detection")
        if symbols_result and "symbol" in symbols_result[0]:
            for sym in symbols_result:
                st.success(f"Found: {sym['symbol']} (confidence {sym['confidence']:.2f})")
            # Append detection info to OCR text for AI validation
            ocr_text += "\nKosher symbol detected"
        else:
            st.info("No Kosher symbols detected")    

        # Validation
        with st.spinner("🤖 Validating..."):
            validation_result = validate_text_with_llm(ocr_text, check_group)

        # Save results
        result_data = {
            "file": uploaded_file.name,
            "check_group": check_group,
            "validation": validation_result,
        }
        save_results(result_data)

        # --------------------------
        # Display Report
        # --------------------------
        st.markdown("---")
        display_validation_report(result_data)

        # Download and Raw Data Options
        cols = st.columns(2)
        with cols[0]:
            st.download_button(
                label="💾 Download Results as JSON",
                data=json.dumps(result_data, indent=4),
                file_name=f"validation_{uploaded_file.name}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with cols[1]:
            if st.button("🔍 Show Raw JSON", use_container_width=True):
                with st.expander("Raw JSON Data", expanded=True):
                    st.json(result_data)

# --------------------------
# Past Results Section
# --------------------------
st.markdown("<div class='section-title'>📜 Previous Validations</div>", unsafe_allow_html=True)
if st.checkbox("Show Last Saved Results"):
    past_results = load_results()
    if past_results:
        st.markdown("### Last Validation Report")
        display_validation_report(past_results)
    else:
        st.warning("⚠️ No saved results found.")

st.markdown("</div>", unsafe_allow_html=True)  