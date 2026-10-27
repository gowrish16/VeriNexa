import requests
import json

def test_ollama(text):
    prompt = f"""You are a strict clinical literature verification classifier for a medical research platform.
Examine the following text from the first 2 pages of an uploaded document.
Determine whether it is a genuine biomedical, clinical trial, pharmacological, or medical healthcare paper.

DOCUMENT EXCERPT:
\"\"\"
{text}
\"\"\"

CLASSIFICATION RULES:
1. ACCEPT if and only if the paper describes genuine medical, clinical trial, pharmacological, epidemiological, or biological healthcare research (e.g. studying patients, diseases, medications, clinical trials, or physiological endpoints).
2. REJECT if the paper is from a non-medical field:
   - College project reports, college synopses, student thesis proposals, coursework, or syllabi (e.g., computer science, IT, mechanical, civil).
   - Software engineering, web applications, programming, cloud computing, or computer science machine learning projects.
   - Sports analytics, athlete tracking, gaming, or entertainment studies.
   - Finance, business, economics, accounting, or corporate budgets.
   - General non-medical topics.

Respond ONLY with valid JSON in this exact structure:
{{
  "is_biomedical": true,
  "confidence": 0.95,
  "reason": "short explanation"
}}
"""
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3.1:8b",
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.0, "num_predict": 100}
    }, timeout=30)
    print(r.json()["response"])

print("--- Test 1: Sports Analytics College Report ---")
test_ollama("Final Year Project Report: Player Performance Analytics in IPL Cricket Using Random Forest. Submitted by Dept of Computer Science & Engineering. Abstract: Sports analytics has emerged as a key domain. In this project, we predict match outcomes and player batting averages using machine learning.")

print("\n--- Test 2: Medical Paper ---")
test_ollama("Safety and efficiency of SGLT2 inhibitor combining with insulin in subjects with diabetes: a randomized double-blind placebo-controlled trial. Abstract: Objective: To assess the clinical efficacy and adverse events of empagliflozin in patients with type 2 diabetes. Methods: 400 patients were randomized to receive 10mg or placebo. Primary endpoint was HbA1c reduction (p < 0.001). Hazard ratio was 0.72.")
