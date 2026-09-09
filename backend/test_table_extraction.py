import pdfplumber

PDF_PATH = "test_pdfs/medi.pdf"

table_settings = {
    "vertical_strategy": "text",
    "horizontal_strategy": "text"
}

def extract_tables():
    with open("table_output.txt", "w", encoding="utf-8") as f:
        with pdfplumber.open(PDF_PATH) as pdf:
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables(table_settings)
                if tables:
                    f.write(f"\n=== Page {i+1}: Found {len(tables)} table(s) ===\n")
                    for t_index, table in enumerate(tables):
                        f.write(f"\n--- Table {t_index+1} ---\n")
                        for row in table:
                            f.write(f"{row}\n")
                else:
                    f.write(f"\nPage {i+1}: No table detected\n")

if __name__ == "__main__":
    extract_tables()
    print("Done. Output written to table_output.txt")