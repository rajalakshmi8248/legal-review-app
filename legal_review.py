# legal_review.py
import streamlit as st
import PyPDF2
import pdfplumber
import pytesseract
from PIL import Image
import spacy

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

# Tesseract config
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_scanned_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            image = page.to_image().original
            page_text = pytesseract.image_to_string(image)
            text += page_text
    return text

def extract_clauses(document_text):
    clauses = {
        "Confidentiality": None,
        "Termination": None,
        "Indemnity": None
    }
    if "confidentiality" in document_text.lower():
        clauses["Confidentiality"] = "Found"
    if "termination" in document_text.lower():
        clauses["Termination"] = "Found"
    if "indemnity" in document_text.lower():
        clauses["Indemnity"] = "Found"
    return clauses

def check_compliance(clauses):
    missing = [k for k, v in clauses.items() if v is None]
    if missing:
        return f"❌ Missing clauses: {', '.join(missing)}"
    else:
        return "✅ Document is compliant with all key clauses."

# Streamlit app
st.title("📑 Legal Document Compliance Checker")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
is_scanned = st.checkbox("Is this a scanned PDF?", value=False)

if uploaded_file:
    st.info("Processing file...")

    if is_scanned:
        text = extract_text_from_scanned_pdf(uploaded_file)
    else:
        text = extract_text_from_pdf(uploaded_file)

    st.subheader("Extracted Text (first 500 chars):")
    st.write(text[:500] + "...")

    clauses = extract_clauses(text)
    st.subheader("Clauses Found:")
    st.write(clauses)

    compliance_result = check_compliance(clauses)
    st.success(compliance_result)
