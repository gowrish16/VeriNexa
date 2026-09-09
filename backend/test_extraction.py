import pdfplumber

PDF_PATH = "test_pdfs/medi.pdf"

def extract_text():
    with pdfplumber.open(PDF_PATH) as pdf:
        print(f"Number of pages: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            print(f"\n--- Page {i+1} ---")
            print(text[:500] if text else "[No text found on this page]")

if __name__ == "__main__":
    extract_text()