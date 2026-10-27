import requests
import psycopg2

BASE_URL = "http://127.0.0.1:8000"

# 1. Login with test user
login_res = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "sarah@clinic.org", "password": "password123"}
)
if login_res.status_code != 200:
    login_res = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"email": "sarah@clinic.org", "password": "password123", "full_name": "Dr. Sarah Jenkins"}
    )

print("Login status:", login_res.status_code)
token_data = login_res.json()
token = token_data.get("access_token")
headers = {"Authorization": f"Bearer {token}"}
print(f"Logged in, token received: {bool(token)}")

# 2. Check current papers for this user
papers_res = requests.get(f"{BASE_URL}/papers", headers=headers)
print("Current papers:", papers_res.json())

# 3. Test upload with non-medical PDF (cricket / sports analytics or college project)
# Create a dummy non-medical PDF or test with an existing one if available
print("\n--- Testing Non-Biomedical Upload Rejection ---")
import reportlab.platypus as plat
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

non_bio_pdf = "scratch/test_cricket_analytics.pdf"
doc = SimpleDocTemplate(non_bio_pdf, pagesize=letter)
styles = getSampleStyleSheet()
story = [
    Paragraph("Department of Computer Science - Project Synopsis", styles["Title"]),
    Spacer(1, 12),
    Paragraph("IPL Cricket Match Outcome Prediction and Batting Average Analytics using Machine Learning", styles["Heading2"]),
    Spacer(1, 12),
    Paragraph("Submitted in partial fulfillment of Bachelor of Technology (B.Tech) in Information Technology.", styles["Normal"]),
    Paragraph("Faculty Guide: Prof. John Doe. Roll No: CS-2024-042.", styles["Normal"]),
    Spacer(1, 12),
    Paragraph("Abstract: This software engineering project introduces a machine learning web application using React.js frontend and Node.js backend. We evaluate bowling performance and player performance stats from IPL seasons 2008-2023. Source code is published on GitHub repository.", styles["Normal"])
]
doc.build(story)

with open(non_bio_pdf, "rb") as f:
    upload_non_bio = requests.post(
        f"{BASE_URL}/upload",
        headers=headers,
        data={"title": "Cricket Match Analytics"},
        files={"file": ("test_cricket_analytics.pdf", f, "application/pdf")}
    )

print("Non-biomedical upload status code:", upload_non_bio.status_code)
print("Non-biomedical upload response:", upload_non_bio.text)

# 4. Test upload with SGLT2.pdf
print("\n--- Testing SGLT2.pdf Upload Verification ---")
sglt2_path = r"backend\test_pdfs\SGLT2.pdf"
with open(sglt2_path, "rb") as f:
    upload_sglt2 = requests.post(
        f"{BASE_URL}/upload",
        headers=headers,
        data={"title": "SGLT2 inhibitors as metabolic modulators in type 2 diabetes"},
        files={"file": ("SGLT2.pdf", f, "application/pdf")}
    )

print("SGLT2 upload status code:", upload_sglt2.status_code)
print("SGLT2 upload response:", upload_sglt2.json() if upload_sglt2.status_code == 200 else upload_sglt2.text)

# 5. Check papers list again
papers_res_after = requests.get(f"{BASE_URL}/papers", headers=headers)
print("\nPapers after upload:", papers_res_after.json())
