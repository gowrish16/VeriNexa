import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

from integrity_graph import graph as integrity_graph
from integrity_check import get_abstract_text, search_within_paper

paper_id = 32
topic_query = "SGLT2 inhibitors as metabolic modulators"

print("--- Testing get_abstract_text(32) ---")
abstract = get_abstract_text(paper_id)
print(f"Abstract length: {len(abstract)}")
print(f"Abstract preview: {abstract[:300]}")

print("\n--- Testing search_within_paper(32, topic_query) ---")
chunks = search_within_paper(paper_id, topic_query)
print(f"Chunks returned: {len(chunks)}")
for idx, chunk in chunks:
    print(f"  Chunk {idx}: {chunk[:100]}...")

print("\n--- Testing integrity_graph.invoke ---")
# But don't call ollama yet, let's inspect the prompt
from integrity_graph import fetch_node
state = {"paper_id": paper_id, "topic_query": topic_query}
fetched = fetch_node(state)
print("Fetched abstract preview:", fetched["abstract_text"][:200])
print("Fetched supporting text preview:", fetched["supporting_text"][:200])
