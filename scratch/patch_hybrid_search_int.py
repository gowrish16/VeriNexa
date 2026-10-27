import os

path = r"C:\Projects\VeriNexa\backend\hybrid_search.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target1 = """    if paper_id is not None:
        conditions.append("paper_id = %s")
        params.append(paper_id)"""

replacement1 = """    if paper_id is not None:
        try:
            pid = int(paper_id)
            conditions.append("paper_id = %s")
            params.append(pid)
        except (ValueError, TypeError):
            pass"""

norm_text = text.replace("\r\n", "\n")
norm_t1 = target1.replace("\r\n", "\n")
norm_r1 = replacement1.replace("\r\n", "\n")

# Replaces both in load_all_chunks and in get_vector_ranking
count = norm_text.count(norm_t1)
assert count == 2, f"Expected 2 occurrences, found {count}"
new_text = norm_text.replace(norm_t1, norm_r1)

with open(path, "wb") as f:
    f.write(new_text.replace("\n", "\r\n").encode("utf-8"))
print("Patched hybrid_search.py paper_id casting safely.")
