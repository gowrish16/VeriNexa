import requests
import json
import os
import psycopg2
from dotenv import load_dotenv

BASE_URL = "http://127.0.0.1:8000"

def make_pdf(text_lines):
    # Construct a valid standard PDF stream
    text_commands = []
    y = 720
    for line in text_lines:
        clean = line.replace("(", "\\(").replace(")", "\\)")
        text_commands.append(f"1 0 0 1 50 {y} Tm ({clean}) Tj")
        y -= 25

    stream = "BT /F1 11 Tf " + " ".join(text_commands) + " ET"
    stream_bytes = stream.encode("latin1")
    pdf_str = f"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj
4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
5 0 obj << /Length {len(stream_bytes)} >> stream
{stream}
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000227 00000 n 
0000000296 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
400
%%EOF"""
    return pdf_str.encode("latin1")

def test_gate():
    print("=================================================================")
    print("BIOMEDICAL DOMAIN VERIFICATION GATE - END-TO-END TEST SUITE")
    print("=================================================================")

    # 1. Register test user
    import random
    uid = random.randint(10000, 99999)
    email = f"dr_researcher_{uid}@hospital.org"
    pwd = "SecurePass123!"

    r_reg = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": email,
        "password": pwd,
        "full_name": f"Dr. Validation {uid}"
    })
    assert r_reg.status_code == 200, f"Register failed: {r_reg.text}"
    token = r_reg.json()["access_token"]
    user = r_reg.json()["user"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Registered test user #{user['id']} ({email})")

    # Connect to DB to verify chunks table before and after
    conn = psycopg2.connect("postgresql://postgres:admin123@127.0.0.1:5433/verilit")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM paper_chunks WHERE user_id = %s;", (user["id"],))
    initial_chunks = cur.fetchone()[0]
    assert initial_chunks == 0, f"Expected 0 initial chunks for user, got {initial_chunks}"
    print(f"Initial DB paper_chunks for user: {initial_chunks}")

    expected_rejection = "Document rejected: Not a recognized biomedical or clinical trial paper. Please upload clinical research literature."

    # Test cases: Non-medical documents that MUST be rejected
    rejection_cases = [
        {
            "name": "College Final Year Project Report",
            "filename": "college_project_report.pdf",
            "lines": [
                "FINAL YEAR PROJECT REPORT",
                "Submitted in partial fulfillment of the requirements for Bachelor of Technology",
                "Department of Computer Science and Engineering",
                "Roll No: 2021-CS-042, Academic Year 2025-2026",
                "Project Guide: Prof. K. Sharma",
                "Abstract: In this project, we built a React.js and Node.js web application",
                "using MongoDB database management and GitHub version control."
            ]
        },
        {
            "name": "Sports Analytics IPL Cricket",
            "filename": "ipl_sports_analytics.pdf",
            "lines": [
                "IPL Cricket Match Outcome and Player Performance Sports Analytics",
                "Abstract: Sports analytics has revolutionized team selection in cricket.",
                "In this research, we evaluate batsman batting average and strike rate",
                "across 500 IPL matches using Random Forest and XGBoost classifiers.",
                "Results show 78% accuracy in predicting match outcomes."
            ]
        },
        {
            "name": "Computer Science Course Syllabus",
            "filename": "cs401_syllabus.pdf",
            "lines": [
                "Course Syllabus: CS401 Advanced Software Engineering",
                "Semester VII, Department of Information Technology",
                "Prerequisites: Data Structures, Database Systems",
                "Topics covered: Agile software development, CI/CD pipelines, Docker containers,",
                "Frontend component lifecycle, and Microservices REST APIs.",
                "Grading: Midterm 30%, Final Exam 50%, Lab Assignments 20%."
            ]
        },
        {
            "name": "Corporate Financial Budget",
            "filename": "corporate_budget.pdf",
            "lines": [
                "Q3 2026 Corporate Financial Budget and Revenue Report",
                "Enterprise Cloud Infrastructure and EBITDA Analysis",
                "Gross profit margins increased by 18% quarter-over-quarter.",
                "Marketing expenditures and stock buyback capital allocation.",
                "Consolidated balance sheet statement and dividend distribution."
            ]
        }
    ]

    print("\n--- Testing Non-Biomedical Documents (Must be Rejected with HTTP 422) ---")
    for tc in rejection_cases:
        pdf_bytes = make_pdf(tc["lines"])
        r = requests.post(
            f"{BASE_URL}/upload",
            headers=headers,
            data={"title": tc["name"]},
            files={"file": (tc["filename"], pdf_bytes, "application/pdf")}
        )
        assert r.status_code == 422, f"Expected 422 for '{tc['name']}', got {r.status_code}: {r.text}"
        detail = r.json().get("detail")
        assert detail == expected_rejection, f"Expected rejection detail '{expected_rejection}', got: {detail}"
        print(f"  [PASS] Rejected '{tc['name']}' with HTTP 422:")
        print(f"         Detail: \"{detail}\"")

    # Verify that NO chunks were inserted for rejected documents
    cur.execute("SELECT COUNT(*) FROM paper_chunks WHERE user_id = %s;", (user["id"],))
    chunks_after_rejections = cur.fetchone()[0]
    assert chunks_after_rejections == 0, f"Pollution detected! Expected 0 chunks, got {chunks_after_rejections}"
    print(f"\n[PASS] Database check: Zero chunks inserted for rejected non-medical documents.")

    # Check documents list: must be empty
    r_docs = requests.get(f"{BASE_URL}/documents", headers=headers)
    docs = r_docs.json().get("documents", [])
    assert len(docs) == 0, f"Expected 0 documents in library, got {len(docs)}"
    print(f"[PASS] User document library is completely clean: {len(docs)} documents.")

    print("\n--- Testing Genuine Clinical Trial PDF Ingestion ---")
    valid_pdf_path = None
    for cand in [
        r"C:\Projects\VeriNexa\data\medi.pdf",
        r"C:\Projects\verilit\data\medi.pdf",
        r"C:\Projects\VeriNexa\backend\uploads\medi.pdf"
    ]:
        if os.path.exists(cand):
            valid_pdf_path = cand
            break

    assert valid_pdf_path is not None, "Sample medi.pdf not found"
    with open(valid_pdf_path, "rb") as f:
        valid_pdf_bytes = f.read()

    r_valid = requests.post(
        f"{BASE_URL}/upload",
        headers=headers,
        data={"title": "Pediatric Inpatient Antimicrobial Audit RCT"},
        files={"file": ("clinical_trial_medi.pdf", valid_pdf_bytes, "application/pdf")}
    )
    assert r_valid.status_code == 200, f"Expected 200 for valid clinical trial, got {r_valid.status_code}: {r_valid.text}"
    paper_id = r_valid.json()["paper_id"]
    print(f"  [PASS] Successfully ingested valid biomedical clinical trial PDF. Paper ID: {paper_id}")

    # Verify DB chunks were populated for the valid paper
    cur.execute("SELECT COUNT(*) FROM paper_chunks WHERE user_id = %s AND paper_id = %s;", (user["id"], paper_id))
    valid_chunks_count = cur.fetchone()[0]
    assert valid_chunks_count > 0, f"Expected chunks for paper #{paper_id}, got {valid_chunks_count}"
    print(f"  [PASS] Verified {valid_chunks_count} chunks embedded and indexed in pgvector under user #{user['id']}.")

    # Verify documents list contains exactly 1 paper
    r_docs_final = requests.get(f"{BASE_URL}/documents", headers=headers)
    final_docs = r_docs_final.json().get("documents", [])
    assert len(final_docs) == 1, f"Expected 1 document, got {len(final_docs)}"
    assert final_docs[0]["id"] == paper_id
    print(f"  [PASS] Section 2 /documents contains exactly the verified paper #{paper_id}.")

    cur.close()
    conn.close()

    print("\n=================================================================")
    print("ALL BIOMEDICAL DOMAIN GATE VERIFICATION CHECKS PASSED!")
    print("=================================================================")

if __name__ == "__main__":
    test_gate()
