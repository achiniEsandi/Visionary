# utils.py
import pdfplumber

def extract_text_from_pdf(path):
    text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or '')
    return '\n'.join(text)

def summarize_cv_text(text, max_len=800):
    # crude summarizer: take first N characters / lines
    return text[:max_len]
