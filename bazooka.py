import json
import pprint
import re
import boto3
from pdf2image import convert_from_path
from textractor.entities.document import Document
# from textractor.utils.textract_response_parser import TextractResponseParser

def pdf_2_image():
    images = convert_from_path("bazooka/BCBP08582_BERRYPNCHFROST_10G_WRP v1.pdf", dpi=300)
    images[0].save("bazooka/page_v1.png", "PNG")

    images = convert_from_path("bazooka/BCBP08582_BERRYPNCHFROST_10G_WRP v2.pdf", dpi=300)
    images[0].save("bazooka/page_v2.png", "PNG")

    textract = boto3.client('textract', region_name='us-east-1')
    with open("bazooka/page_v1.png", "rb") as document:
        image_bytes = document.read()
    response = textract.detect_document_text(Document={'Bytes': image_bytes})

    with open('bazooka/v1.json', 'w') as f1:
        json.dump(response,f1)

    pprint.pprint(response)

    with open("bazooka/page_v2.png", "rb") as document:
        image_bytes = document.read()
    response = textract.detect_document_text(Document={'Bytes': image_bytes})
    with open('bazooka/v2.json', 'w') as f2:
        json.dump(response,f2)

    pprint.pprint(response)
# pdf_2_image()

def load_object():
    with open("D:/Bazooka/bazooka/v1.json", "r") as f:
        json_data = f.read()
    document = Document.open("D:/Bazooka/bazooka/v1.json")
    text = document.text
    # text = document.text.replace("\n",r"\n")
    return text

def normalize_newlines(text: str) -> str:
    # Collapse 3+ newlines into 2 (paragraph separation)
    text = re.sub(r'\n{3,}', '\n', text)
    # Collapse multiple spaces/tabs
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

raw_text = load_object()
print(raw_text)
# normalized_text = normalize_newlines(raw_text)
# print(normalized_text)