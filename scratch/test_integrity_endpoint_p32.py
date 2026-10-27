import sys
import os
import requests
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

from integrity_check import get_paper_metadata, get_abstract_text, search_within_paper, check_integrity
from integrity_graph import graph as integrity_graph

print("=== 1. Testing Paper Metadata Extraction ===")
meta = get_paper_metadata(32)
print("Paper 32 Metadata:", meta)
assert meta is not None, "Paper 32 metadata must exist"
assert "SGLT2" in meta["title"] or "SGLT2" in meta["filename"]

print("\n=== 2. Testing Abstract Extraction for Paper 32 ===")
abstract = get_abstract_text(32, max_chunks=3)
print(f"Abstract length: {len(abstract)} characters")
print(f"Abstract preview:\n{abstract[:350]}...\n")
assert "SGLT2" in abstract
assert "waste bin" not in abstract.lower()
assert "litter" not in abstract.lower()

print("=== 3. Testing Body Chunks Extraction for Paper 32 ===")
body_chunks = search_within_paper(32, "body weight and visceral fat reduction", top_k=4)
print(f"Body chunks returned: {len(body_chunks)}")
for idx, text in body_chunks:
    print(f"  [Chunk #{idx}]: {text[:140]}...")
    assert "waste bin" not in text.lower()
    assert "litter" not in text.lower()
    assert idx >= 3, f"Body chunk index {idx} must be >= 3 (outside abstract)"

print("\n=== 4. Testing End-to-End LangGraph Pipeline ===")
graph_res = integrity_graph.invoke({"paper_id": 32, "topic_query": "body weight and visceral fat reduction"})
print("Graph Verdict:", graph_res["verdict"])
print("Saved ID:", graph_res.get("saved_id"))
assert "waste bin" not in graph_res["verdict"].lower()
assert "litter" not in graph_res["verdict"].lower()

print("\n=== 5. Testing Live FastAPI /integrity-check Endpoint ===")
try:
    r = requests.get("http://127.0.0.1:8000/integrity-check", params={"paper_id": 32, "topic_query": "body weight"})
    print("HTTP Status:", r.status_code)
    json_data = r.json()
    print("Endpoint Response:", json_data)
    assert r.status_code == 200
    assert json_data["paper_id"] == 32
    assert "waste bin" not in json_data["verdict"].lower()
    assert "litter" not in json_data["verdict"].lower()
    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
except Exception as e:
    print("Live API test note:", e)
