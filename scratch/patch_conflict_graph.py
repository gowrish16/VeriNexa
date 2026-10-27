import os
import sys

path = r"C:\Projects\VeriNexa\backend\conflict_graph.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = """    paper_a_id, paper_b_id = paper_ids[0], paper_ids[1]
    paper_a_text = "\\n".join([text for _, text, _ in grouped_chunks[paper_a_id]])
    paper_b_text = "\\n".join([text for _, text, _ in grouped_chunks[paper_b_id]])"""

replacement = """    paper_a_id, paper_b_id = paper_ids[0], paper_ids[1]
    def _extract_chunk_text(c):
        if isinstance(c, str):
            return c
        for elem in c:
            if isinstance(elem, str):
                return elem
        return str(c)

    paper_a_text = "\\n".join([_extract_chunk_text(item) for item in grouped_chunks[paper_a_id]])
    paper_b_text = "\\n".join([_extract_chunk_text(item) for item in grouped_chunks[paper_b_id]])"""

norm_text = text.replace("\r\n", "\n")
norm_target = target.replace("\r\n", "\n")
norm_replacement = replacement.replace("\r\n", "\n")

assert norm_target in norm_text, "Target not found in conflict_graph.py"
new_text = norm_text.replace(norm_target, norm_replacement)

with open(path, "wb") as f:
    f.write(new_text.replace("\n", "\r\n").encode("utf-8"))
print("Patched conflict_graph.py chunk text extraction safely.")
