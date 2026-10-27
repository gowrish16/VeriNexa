import requests
import pdfplumber
import time
import re

def clean_extracted_text(pdf_path):
    raw_pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages[:2]:
            t = p.extract_text()
            if t:
                raw_pages.append(t)
    full_raw = "\n".join(raw_pages)
    
    cleaned_lines = []
    for line in full_raw.splitlines():
        l_str = line.strip()
        l_lower = l_str.lower()
        if not l_str:
            continue
        # Strip metadata, copyright, author blocks
        if any(l_lower.startswith(prefix) for prefix in [
            "doi", "published", "editedby", "edited by", "reviewedby", "reviewed by",
            "correspondence", "*correspondence", "openaccess", "open access", "copyright",
            "all rights reserved", "received", "accepted", "citation"
        ]):
            continue
        if "@" in l_str or re.search(r"^\d\s*(department|school|graduate|faculty|university|hospital|institute)", l_lower):
            continue
        if re.search(r"^(dr\.|prof\.|mr\.|ms\.)", l_lower):
            continue
        cleaned_lines.append(l_str)
        
    cleaned_text = "\n".join(cleaned_lines)
    return cleaned_text

cleaned = clean_extracted_text(r"C:\Projects\VeriNexa\backend\test_pdfs\SGLT2.pdf")
words = cleaned.split()
sample_text = " ".join(words[:450])

prompt = f"""You are an expert biomedical and scientific document classifier.
Analyze the following document text:

\"\"\"
{sample_text}
\"\"\"

TASK:
Determine if this document is biomedical literature.
- Answer YES if the text discusses biomedical, healthcare, clinical, or pharmacological topics (such as clinical trials, disease mechanisms, pharmacology, patient cohorts, therapies, or medical studies).
- Answer NO only if it is completely non-biomedical (e.g. computer science, engineering, sports, business, finance, resumes, college reports, or software manuals).

Output strictly YES or NO.
Answer:"""

print(f"Testing with {len(sample_text.split())} words...")
t0 = time.time()
r = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama3.1:8b",
    "prompt": prompt,
    "stream": False,
    "options": {"num_predict": 5, "temperature": 0.0}
}, timeout=30)
print(f"Time: {time.time() - t0:.2f}s")
print("Response:", r.json()["response"].strip())
