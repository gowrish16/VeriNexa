import requests
import time

prompt = """You are a strict biomedical classifier. Classify if this paper excerpt belongs to biomedical, clinical trial, pharmacological, or healthcare research.
Excerpt: Safety and efficiency of SGLT2 inhibitor combining with insulin in subjects with diabetes: a randomized double-blind placebo-controlled trial. 400 patients randomized. Primary endpoint was HbA1c reduction (p < 0.001). Hazard ratio 0.72.
Answer with one word: BIOMEDICAL or NON_BIOMEDICAL.
Answer:"""

t0 = time.time()
r = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama3.1:8b",
    "prompt": prompt,
    "stream": False,
    "options": {"num_predict": 10, "temperature": 0.0}
}, timeout=60)
print(f"Time: {time.time() - t0:.2f}s")
print("Response:", r.json()["response"].strip())
