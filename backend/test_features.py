import json
import os
import io
import requests
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def run_tests():
    print("=== STARTING COMPREHENSIVE VERIFICATION ===")

    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[PASS] GET /health -> 200 OK")

    # 2. Test User Registration
    test_email = f"researcher_{os.getpid()}@lab.org"
    test_password = "SecureResearchPass2026!"
    test_name = "Dr. Elena Vance"

    reg_payload = {
        "email": test_email,
        "password": test_password,
        "full_name": test_name
    }
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 200, f"Register failed: {res.text}"
    data = res.json()
    assert "access_token" in data, "access_token missing in register response"
    assert data["user"]["email"] == test_email
    token = data["access_token"]
    print(f"[PASS] POST /api/auth/register -> 200 OK (User ID: {data['user']['id']})")

    # Test Duplicate Registration Prevention
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 400, "Duplicate registration should return 400"
    print("[PASS] Duplicate registration rejected -> 400 Bad Request")

    # 3. Test User Login
    login_payload = {
        "email": test_email,
        "password": test_password
    }
    res = client.post("/api/auth/login", json=login_payload)
    assert res.status_code == 200, f"Login failed: {res.text}"
    login_data = res.json()
    assert "access_token" in login_data
    token = login_data["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] POST /api/auth/login -> 200 OK")

    # Test Bad Password
    res = client.post("/api/auth/login", json={"email": test_email, "password": "WrongPassword"})
    assert res.status_code == 401, "Bad password should return 401"
    print("[PASS] Incorrect password rejected -> 401 Unauthorized")

    # 4. Test User Profile (GET /api/auth/me)
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200, f"GET /api/auth/me failed: {res.text}"
    profile = res.json()
    assert profile["email"] == test_email
    assert profile["full_name"] == test_name
    print(f"[PASS] GET /api/auth/me -> 200 OK ({profile['full_name']})")

    # 5. Test Unauthenticated Access to Upload
    dummy_pdf_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    res = client.post(
        "/upload",
        data={"title": "Test Paper"},
        files={"file": ("test.pdf", io.BytesIO(dummy_pdf_content), "application/pdf")}
    )
    assert res.status_code == 401, f"Unauthenticated upload should be 401, got {res.status_code}"
    print("[PASS] Unauthenticated POST /upload -> 401 Unauthorized")

    # 6. Test Biomedical Ingestion Gate Rejection (HTTP 422)
    # Using a non-biomedical text file disguised as PDF or with financial text
    financial_pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj\n"
        b"4 0 obj << /Length 120 >> stream\n"
        b"BT /F1 12 Tf 100 700 Td (Quarterly Financial Report Q3: Revenue growth in SaaS enterprise software and stock dividends.) Tj ET\n"
        b"endstream endobj\n"
        b"xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000214 00000 n \n"
        b"trailer << /Size 5 /Root 1 0 R >>\nstartxref\n386\n%%EOF\n"
    )
    res = client.post(
        "/upload",
        headers=auth_headers,
        data={"title": "Q3 SaaS Earnings Analysis"},
        files={"file": ("financial_earnings.pdf", io.BytesIO(financial_pdf_content), "application/pdf")}
    )
    print(f"Biomedical Gate Test Status: {res.status_code}, Response: {res.text[:150]}")
    assert res.status_code == 422, f"Non-biomedical upload should return 422, got {res.status_code}"
    detail = res.json()["detail"]
    assert detail["status"] == "rejected"
    print("[PASS] Non-biomedical upload strictly rejected -> HTTP 422 Unprocessable Entity")

    # 7. Test Audit Sessions & RAG Chat with Citations
    chat_payload = {
        "question": "What is the clinical effect of SGLT2 inhibitors on blood glucose?"
    }
    res = client.post("/api/chat", headers=auth_headers, json=chat_payload)
    assert res.status_code == 200, f"POST /api/chat failed: {res.text}"
    chat_resp = res.json()
    assert "session_id" in chat_resp, "session_id missing in chat response"
    assert "answer" in chat_resp, "answer missing in chat response"
    assert "citations" in chat_resp, "citations missing in chat response"
    session_id = chat_resp["session_id"]
    print(f"[PASS] POST /api/chat -> 200 OK (Session #{session_id}, Sources: {chat_resp['sources_used']})")
    print(f"       Answer snippet: {chat_resp['answer'][:120]}...")

    # 8. Test Fetching Audit History (GET /api/history)
    res = client.get("/api/history", headers=auth_headers)
    assert res.status_code == 200, f"GET /api/history failed: {res.text}"
    history = res.json()
    assert len(history["sessions"]) > 0, "Expected at least 1 session in history"
    matching = [s for s in history["sessions"] if s["id"] == session_id]
    assert len(matching) == 1, f"Session {session_id} not found in history"
    print(f"[PASS] GET /api/history -> 200 OK ({len(history['sessions'])} sessions found)")

    # 9. Test Fetching Specific Session Messages (GET /api/history/{session_id})
    res = client.get(f"/api/history/{session_id}", headers=auth_headers)
    assert res.status_code == 200, f"GET /api/history/{session_id} failed: {res.text}"
    session_detail = res.json()
    assert session_detail["session_id"] == session_id
    assert len(session_detail["messages"]) >= 2, "Expected at least user and assistant turns"
    user_msg = session_detail["messages"][0]
    asst_msg = session_detail["messages"][1]
    assert user_msg["role"] == "user"
    assert asst_msg["role"] == "assistant"
    print(f"[PASS] GET /api/history/{session_id} -> 200 OK ({len(session_detail['messages'])} persisted messages)")

    # 10. Test Multi-Turn in Same Session
    followup_payload = {
        "question": "What are the common adverse reactions?",
        "session_id": session_id
    }
    res = client.post("/api/chat", headers=auth_headers, json=followup_payload)
    assert res.status_code == 200
    followup_resp = res.json()
    assert followup_resp["session_id"] == session_id
    print(f"[PASS] Multi-turn POST /api/chat within existing Session #{session_id} -> 200 OK")

    # Verify session now has 4 messages
    res = client.get(f"/api/history/{session_id}", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()["messages"]) >= 4
    print("[PASS] Verified session message count updated to 4 turns")

    print("\n=============================================")
    print("ALL 10 COMPREHENSIVE TESTS PASSED SUCCESSFULLY!")
    print("=============================================")

if __name__ == "__main__":
    run_tests()
