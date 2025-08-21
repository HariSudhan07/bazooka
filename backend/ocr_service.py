import boto3
import json
from pdf2image import convert_from_path
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

def pdf_to_image(pdf_path, output_path="page.png"):
    """
    Convert the first page of a PDF to an image (PNG).
    """
    images = convert_from_path(pdf_path, dpi=300)
    images[0].save(output_path, "PNG")
    return output_path


def extract_text_aws(image_path, region=None):
    """
    Extract text from an image using AWS Textract.
    Credentials are loaded from .env or AWS CLI config.
    """

    # Default to env variable or fallback region
    region_name = region or os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    # Initialize Textract client with credentials
    textract = boto3.client(
        "textract",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=region_name,
    )

    with open(image_path, "rb") as document:
        image_bytes = document.read()

    response = textract.detect_document_text(Document={"Bytes": image_bytes})

    # Extract only text lines
    text = "\n".join(
        [block["Text"] for block in response["Blocks"] if block["BlockType"] == "LINE"]
    )

    # Save raw response as JSON file
    json_path = image_path.replace(".png", ".json")
    with open(json_path, "w") as f:
        json.dump(response, f, indent=2)

    return text
