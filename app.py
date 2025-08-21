# import streamlit as st
# from backend.ocr_service import extract_text_aws, pdf_to_image
# from backend.llm_service import validate_text_with_llm
# from backend.db_service import save_results, load_results

# st.title("📄 Bazooka Candy - Packaging Validation App")

# # File upload
# uploaded_file = st.file_uploader("Upload Packaging (PDF/Image)", type=["pdf", "png", "jpg", "jpeg"])

# # Check group selection
# check_group = st.selectbox("Select Check Group", ["Front", "Back", "Canada", "All"])

# if uploaded_file:
#     st.info("File uploaded successfully!")

#     # Save uploaded file locally
#     with open("temp.pdf" if uploaded_file.name.endswith(".pdf") else "temp.png", "wb") as f:
#         f.write(uploaded_file.read())
#     file_path = f.name

#     if st.button("Run OCR & Validation"):
#         # Convert PDF → Image if needed
#         if file_path.endswith(".pdf"):
#             image_path = pdf_to_image(file_path, "temp.png")
#         else:
#             image_path = file_path

#         st.write("🔍 Running OCR with AWS Textract...")
#         ocr_text = extract_text_aws(image_path)
#         st.text_area("OCR Output", ocr_text, height=200)

#         st.write("🤖 Running Validation with Gemini Flash...")
#         validation_result = validate_text_with_llm(ocr_text, check_group)

#         # Save results
#         result_data = {
#             "file": uploaded_file.name,
#             "check_group": check_group,
#             "validation": validation_result,
#         }
#         save_results(result_data)

#         st.success("✅ Validation Complete")
#         st.json(result_data)

# # Load previous results
# if st.checkbox("Show last saved results"):
#     past_results = load_results()
#     if past_results:
#         st.json(past_results)
#     else:
#         st.warning("No saved results found.")


# import streamlit as st
# import json
# from backend.ocr_service import extract_text_aws, pdf_to_image
# from backend.llm_service import validate_text_with_llm
# from backend.db_service import save_results, load_results

# # --------------------------
# # Page Config
# # --------------------------
# st.set_page_config(page_title="Bazooka Candy - Packaging Validation", page_icon="📄", layout="centered")

# st.title("📄 Bazooka Candy - Packaging Validation App")
# st.markdown("Easily validate packaging text with OCR + LLM checks. Upload your file, run OCR, and get instant validation results.")

# # --------------------------
# # File Upload Section
# # --------------------------
# st.header("📂 Upload & Select Check")
# uploaded_file = st.file_uploader("Upload Packaging (PDF/Image)", type=["pdf", "png", "jpg", "jpeg"])

# col1, col2 = st.columns([1, 2])
# with col1:
#     check_group = st.selectbox("Check Group", ["Front", "Back", "Canada", "All"])
# with col2:
#     st.info("Choose which packaging side/group you want to validate.")

# # --------------------------
# # Processing Section
# # --------------------------
# if uploaded_file:
#     st.success(f"✅ File **{uploaded_file.name}** uploaded successfully!")

#     # Save uploaded file locally
#     with open("temp.pdf" if uploaded_file.name.endswith(".pdf") else "temp.png", "wb") as f:
#         f.write(uploaded_file.read())
#     file_path = f.name

#     if st.button("🚀 Run OCR & Validation", use_container_width=True):
#         with st.spinner("🔍 Running OCR with AWS Textract..."):
#             # Convert PDF → Image if needed
#             if file_path.endswith(".pdf"):
#                 image_path = pdf_to_image(file_path, "temp.png")
#             else:
#                 image_path = file_path

#             ocr_text = extract_text_aws(image_path)

#         with st.expander("📝 OCR Extracted Text", expanded=False):
#             st.text_area("OCR Output", ocr_text, height=200)

#         with st.spinner("🤖 Running Validation with Gemini Flash..."):
#             validation_result = validate_text_with_llm(ocr_text, check_group)

#         # Save results
#         result_data = {
#             "file": uploaded_file.name,
#             "check_group": check_group,
#             "validation": validation_result,
#         }
#         save_results(result_data)

#         # --------------------------
#         # Results Section
#         # --------------------------
#         st.subheader("📊 Validation Results")
#         st.json(result_data)

        
#         # Download button
#         st.download_button(
#             label="💾 Download Results as JSON",
#             data=json.dumps(result_data, indent=4),
#             file_name=f"validation_{uploaded_file.name}.json",
#             mime="application/json",
#             use_container_width=True
#         )

#         st.success("✅ Validation Complete!")

# # --------------------------
# # Past Results Section
# # --------------------------
# st.divider()
# if st.checkbox("📜 Show Last Saved Results"):
#     past_results = load_results()
#     if past_results:
#         with st.expander("📂 Previous Validation Result", expanded=True):
#             st.json(past_results)
#     else:
#         st.warning("⚠️ No saved results found.")
import streamlit as st
import json
from backend.ocr_service import extract_text_aws, pdf_to_image
from backend.llm_service import validate_text_with_llm
from backend.db_service import save_results, load_results

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
    /* JSON box */
    .stJson {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.5rem;
        border: 1px solid #ddd;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------
# Header
# --------------------------
with st.container():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.title("📄 Bazooka Candy - Packaging Validation")
    st.markdown(
        "<p style='font-size:15px; color:#555;'>Validate packaging text with AI-powered OCR & Gemini LLM checks. "
        "Upload a file, pick a check group, and get instant validation results.</p>",
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
    check_group = st.selectbox("Check Group", ["Front", "Back", "Canada", "All"])

# --------------------------
# Processing Section
# --------------------------
if uploaded_file:
    st.success(f"✅ File **{uploaded_file.name}** uploaded successfully!")

    # Save uploaded file locally
    with open("temp.pdf" if uploaded_file.name.endswith(".pdf") else "temp.png", "wb") as f:
        f.write(uploaded_file.read())
    file_path = f.name

    if st.button("🚀 Run OCR & Validation", use_container_width=True):
        # OCR
        with st.spinner("🔍 Extracting text using AWS Textract..."):
            if file_path.endswith(".pdf"):
                image_path = pdf_to_image(file_path, "temp.png")
            else:
                image_path = file_path
            ocr_text = extract_text_aws(image_path)

        with st.expander("📝 View OCR Extracted Text"):
            st.text_area("OCR Output", ocr_text, height=180)

        # Validation
        with st.spinner("🤖 Validating extracted text with Gemini Flash..."):
            validation_result = validate_text_with_llm(ocr_text, check_group)

        # Save results
        result_data = {
            "file": uploaded_file.name,
            "check_group": check_group,
            "validation": validation_result,
        }
        save_results(result_data)

        # --------------------------
        # Results Section
        # --------------------------
        st.markdown("<div class='section-title'>📊 Validation Results</div>", unsafe_allow_html=True)

        cols = st.columns(2)
        with cols[0]:
            st.markdown(f"<div class='card'><b>📁 File:</b><br>{uploaded_file.name}</div>", unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"<div class='card'><b>🔎 Check Group:</b><br>{check_group}</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.json(result_data)
        st.markdown("</div>", unsafe_allow_html=True)

        # Download button
        st.download_button(
            label="💾 Download Results as JSON",
            data=json.dumps(result_data, indent=4),
            file_name=f"validation_{uploaded_file.name}.json",
            mime="application/json",
            use_container_width=True
        )

        st.success("✅ Validation Complete!")

# --------------------------
# Past Results Section
# --------------------------
st.markdown("<div class='section-title'>📜 Previous Validations</div>", unsafe_allow_html=True)
if st.checkbox("Show Last Saved Results"):
    past_results = load_results()
    if past_results:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.json(past_results)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ No saved results found.")

st.markdown("</div>", unsafe_allow_html=True)  # close main container
