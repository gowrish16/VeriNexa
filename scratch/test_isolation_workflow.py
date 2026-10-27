import requests
import json
import os
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_workflow():
    print("--- 1. Testing Unauthenticated Access ---")
    for endpoint in ["/documents", "/papers", "/sessions", "/api/history"]:
        r = requests.get(f"{BASE_URL}{endpoint}")
        assert r.status_code == 401, f"Expected 401 for {endpoint}, got {r.status_code}"
        print(f"  [PASS] {endpoint} returned 401 Unauthorized")

    r = requests.post(f"{BASE_URL}/upload")
    assert r.status_code == 401, f"Expected 401 for POST /upload, got {r.status_code}"
    print("  [PASS] POST /upload returned 401 Unauthorized")

    print("\n--- 2. Registering and Authenticating Tenant A and Tenant B ---")
    import random
    suffix = random.randint(10000, 99999)
    email_a = f"clinician_a_{suffix}@hospital.org"
    email_b = f"clinician_b_{suffix}@hospital.org"
    password = "SecurePassword123!"

    # Register A
    r_reg_a = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": email_a,
        "password": password,
        "full_name": f"Dr. Alice {suffix}"
    })
    assert r_reg_a.status_code == 200, f"Failed to register A: {r_reg_a.text}"
    token_a = r_reg_a.json()["access_token"]
    user_a = r_reg_a.json()["user"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print(f"  [PASS] Registered Tenant A (ID: {user_a['id']}, Email: {email_a})")

    # Register B
    r_reg_b = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": email_b,
        "password": password,
        "full_name": f"Dr. Bob {suffix}"
    })
    assert r_reg_b.status_code == 200, f"Failed to register B: {r_reg_b.text}"
    token_b = r_reg_b.json()["access_token"]
    user_b = r_reg_b.json()["user"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print(f"  [PASS] Registered Tenant B (ID: {user_b['id']}, Email: {email_b})")

    print("\n--- 3. Testing Initial Onboarding State for New Tenant B ---")
    r_docs_b = requests.get(f"{BASE_URL}/documents", headers=headers_b)
    assert r_docs_b.status_code == 200
    docs_b = r_docs_b.json().get("documents", [])
    assert len(docs_b) == 0, f"Expected 0 documents for brand new Tenant B, got {len(docs_b)}"
    print(f"  [PASS] Tenant B initial papers count: {len(docs_b)} (Triggers Onboarding Gate -> /upload)")

    print("\n--- 4. Testing Biomedical Domain Gate with Non-Medical Document ---")
    # Generate a dummy non-biomedical PDF
    stream = "BT /F1 12 Tf 50 700 Td (Quarterly Financial Budget Report 2026 Corporate Accounting EBITDA Marketing Cloud Hosting Fees) Tj ET"
    non_med_pdf_str = f"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj
4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
5 0 obj << /Length {len(stream)} >> stream
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
    non_med_pdf_bytes = non_med_pdf_str.encode("latin1")

    r_non_med = requests.post(
        f"{BASE_URL}/upload",
        headers=headers_b,
        data={"title": "Corporate Budget 2026"},
        files={"file": ("corporate_budget.pdf", non_med_pdf_bytes, "application/pdf")}
    )
    assert r_non_med.status_code == 422, f"Expected 422 rejection, got {r_non_med.status_code}: {r_non_med.text}"
    err_json = r_non_med.json()
    print(f"  [PASS] Biomedical validation rejected non-medical document with HTTP 422: {err_json['detail']['message']}")

    print("\n--- 5. Testing Biomedical Upload & Ingestion for Tenant B ---")
    # Find a valid medical PDF from data folder
    sample_pdf_path = None
    for candidate in [
        r"C:\Projects\VeriNexa\data\medi.pdf",
        r"C:\Projects\verilit\data\medi.pdf",
        r"C:\Projects\VeriNexa\backend\uploads\medi.pdf",
    ]:
        if os.path.exists(candidate):
            sample_pdf_path = candidate
            break

    assert sample_pdf_path is not None, "Could not find medi.pdf sample file"
    with open(sample_pdf_path, "rb") as f:
        valid_pdf_bytes = f.read()

    r_upload_b = requests.post(
        f"{BASE_URL}/upload",
        headers=headers_b,
        data={"title": "Pediatric Antimicrobial Inpatient Audit"},
        files={"file": ("pediatric_audit.pdf", valid_pdf_bytes, "application/pdf")}
    )
    assert r_upload_b.status_code == 200, f"Expected 200 for valid upload, got {r_upload_b.status_code}: {r_upload_b.text}"
    upload_res = r_upload_b.json()
    paper_b_id = upload_res["paper_id"]
    print(f"  [PASS] Successfully ingested valid clinical trial PDF. Paper ID: {paper_b_id}")

    print("\n--- 6. Testing Document Isolation Between Tenants ---")
    r_docs_b = requests.get(f"{BASE_URL}/documents", headers=headers_b)
    docs_b = r_docs_b.json().get("documents", [])
    assert len(docs_b) == 1, f"Expected 1 doc for B, got {len(docs_b)}"
    assert docs_b[0]["id"] == paper_b_id
    assert docs_b[0]["user_id"] == user_b["id"]
    print(f"  [PASS] Tenant B sees exactly 1 document (ID: {paper_b_id}, User ID: {docs_b[0]['user_id']})")

    r_docs_a = requests.get(f"{BASE_URL}/documents", headers=headers_a)
    docs_a = r_docs_a.json().get("documents", [])
    doc_ids_a = [d["id"] for d in docs_a]
    assert paper_b_id not in doc_ids_a, f"Leak detected! Tenant B paper {paper_b_id} visible to Tenant A: {doc_ids_a}"
    print(f"  [PASS] Tenant A sees {len(docs_a)} documents, none belonging to Tenant B (Paper {paper_b_id} isolated)")

    print("\n--- 7. Testing Audit Session Isolation Between Tenants ---")
    # Tenant B creates chat message / session
    r_chat_b = requests.post(
        f"{BASE_URL}/api/chat",
        headers=headers_b,
        json={"question": "What is the primary intervention evaluated?", "paper_id": paper_b_id}
    )
    assert r_chat_b.status_code == 200, f"Failed chat query: {r_chat_b.text}"
    session_b_id = r_chat_b.json()["session_id"]
    print(f"  [PASS] Tenant B created audit session #{session_b_id}")

    # Tenant B sees session
    r_sess_b = requests.get(f"{BASE_URL}/api/history", headers=headers_b)
    sess_ids_b = [s["id"] for s in r_sess_b.json().get("sessions", [])]
    assert session_b_id in sess_ids_b
    print(f"  [PASS] Tenant B sees audit session #{session_b_id} in history")

    # Tenant A DOES NOT see session in history
    r_sess_a = requests.get(f"{BASE_URL}/api/history", headers=headers_a)
    sess_ids_a = [s["id"] for s in r_sess_a.json().get("sessions", [])]
    assert session_b_id not in sess_ids_a, f"Leak! Tenant B's session #{session_b_id} visible to Tenant A!"
    print(f"  [PASS] Tenant A history does not include Tenant B session #{session_b_id}")

    # Tenant A attempts direct access to Tenant B session -> 404
    r_direct_a = requests.get(f"{BASE_URL}/api/history/{session_b_id}", headers=headers_a)
    assert r_direct_a.status_code == 404, f"Tenant A accessed Tenant B session: {r_direct_a.status_code}"
    print(f"  [PASS] Tenant A direct access to /api/history/{session_b_id} returned 404 Not Found")

    print("\n========================================================")
    print("ALL MULTI-TENANCY & ONBOARDING WORKFLOW CHECKS PASSED!")
    print("========================================================")

if __name__ == "__main__":
    test_workflow()
