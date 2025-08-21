import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API keys from .env
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define checks
VALIDATION_CHECKS = {
    "Front": [
        "Confirm 'Ages 4+' appears at the bottom (except for Bazooka gum).",
        "Confirm Net Weight is at the bottom.",
        "Confirm unit count of products is at the bottom."
    ],
    "Back": [
        "Include manufacturer information after legal IP line: 'Distributed by The Bazooka Companies, LLC, Scranton, PA 18505. For questions, comments, and tracking label information, call 1-888-204-4124 or visit www.bazookacandybrands.com.'",
        "Confirm 'Ages 4+' appears below manufacturer info.",
        "Confirm NFP (Nutrition Facts Panel) is present if not exempt as a small package.",
        "Confirm NFP contains ingredients statements.",
        "Back of package should contain country of origin below manufacturer contact information: 'Made in [country]'."
    ]
}


def validate_text_with_llm(ocr_text: str, selected_group: str = "All"):
    """
    Validate OCR text using Gemini LLM against predefined checks.
    selected_group can be "Front", "Back", "Canada", or "All"
    """

    # Collect relevant checks
    checks_to_run = []
    if selected_group == "All":
        for group_checks in VALIDATION_CHECKS.values():
            checks_to_run.extend(group_checks)
    elif selected_group in ["Front", "Back", "Canada"]:
        checks_to_run = VALIDATION_CHECKS.get(selected_group, [])
    else:
        return {"error": f"Unknown group: {selected_group}"}

    # Build prompt
    prompt = f"""
You are a compliance validator for candy packaging labels. 
You will receive OCR extracted text from an image of a Bazooka candy package. 
Check the text against the following rules:

Rules to check:
{chr(10).join(f"- {c}" for c in checks_to_run)}

OCR text:
\"\"\"
{ocr_text}
\"\"\"

Return a JSON object with each rule, validation result (PASS/FAIL), and reasoning.
Additionally, check the OCR text for spelling, typos, or grammar errors. If found, list corrections.

Format the JSON response exactly like this:

{{
  "checks": [
    {{
      "rule": "Rule description",
      "result": "PASS or FAIL",
      "reason": "Explanation of why it passed or failed"
    }}
  ],
  "spelling_grammar": {{
    "issues": [
      {{
         "ocr_text": "text from OCR",
         "correct_text": "suggested correction"
      }}
    ]
   }}
}}
"""

    # Run Gemini Flash 2.5
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    return response.text
