import os

path = r"C:\Projects\VeriNexa\backend\conflict_engine.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = """def get_papers_for_comparison(user_id: Optional[int] = None, paper_ids: Optional[List[int]] = None) -> List[Tuple[int, str, str]]:
    \"\"\"
    Identifies at least 2 distinct papers for cross-examination.
    Prioritizes explicit paper_ids, then user's indexed papers, then available active papers.
    Guarantees no duplicate paper IDs.
    \"\"\"
    conn = get_connection()
    cursor = conn.cursor()
    papers_dict = {}

    if paper_ids:
        cursor.execute(
            \"\"\"
            SELECT id, COALESCE(detected_title, title), filename
            FROM papers
            WHERE id = ANY(%s)
            ORDER BY id;
            \"\"\",
            (list(paper_ids),)
        )
        for r in cursor.fetchall():
            papers_dict[r[0]] = r

    if len(papers_dict) < 2 and user_id is not None:
        cursor.execute(
            \"\"\"
            SELECT id, COALESCE(detected_title, title), filename
            FROM papers
            WHERE user_id = %s
            ORDER BY id;
            \"\"\",
            (user_id,)
        )
        for r in cursor.fetchall():
            papers_dict[r[0]] = r

    # Fallback: if fewer than 2 papers found, fetch available distinct papers that have indexed chunks
    if len(papers_dict) < 2:
        cursor.execute(\"\"\"
            SELECT p.id, COALESCE(p.detected_title, p.title), p.filename
            FROM papers p
            WHERE EXISTS (SELECT 1 FROM paper_chunks c WHERE c.paper_id = p.id)
            ORDER BY p.id DESC
            LIMIT 5;
        \"\"\")
        for r in cursor.fetchall():
            papers_dict[r[0]] = r

    cursor.close()
    conn.close()
    return list(papers_dict.values())"""

replacement = """def get_papers_for_comparison(user_id: Optional[int] = None, paper_ids: Optional[List[int]] = None) -> List[Tuple[int, str, str]]:
    \"\"\"
    Identifies the exact 2 papers for cross-examination.
    When explicit paper_ids are provided, strictly restricts retrieval to those 2 IDs.
    Preserves the exact requested pair order: [Paper 1, Paper 2].
    Never performs unconstrained global similarity search.
    \"\"\"
    conn = get_connection()
    cursor = conn.cursor()

    if paper_ids and len(paper_ids) >= 2:
        target_ids = [int(p) for p in paper_ids[:2]]
        cursor.execute(
            \"\"\"
            SELECT id, COALESCE(detected_title, title), filename
            FROM papers
            WHERE id = ANY(%s);
            \"\"\",
            (target_ids,)
        )
        fetched = {r[0]: r for r in cursor.fetchall()}
        cursor.close()
        conn.close()
        # Return exact target_ids in requested order
        ordered = [fetched[pid] for pid in target_ids if pid in fetched]
        return ordered

    papers_dict = {}
    if paper_ids:
        target_ids = [int(p) for p in paper_ids]
        cursor.execute(
            \"\"\"
            SELECT id, COALESCE(detected_title, title), filename
            FROM papers
            WHERE id = ANY(%s);
            \"\"\",
            (target_ids,)
        )
        for r in cursor.fetchall():
            papers_dict[r[0]] = r

    if len(papers_dict) < 2 and user_id is not None:
        cursor.execute(
            \"\"\"
            SELECT id, COALESCE(detected_title, title), filename
            FROM papers
            WHERE user_id = %s
            ORDER BY id;
            \"\"\",
            (user_id,)
        )
        for r in cursor.fetchall():
            papers_dict[r[0]] = r

    # Fallback: if fewer than 2 papers found, fetch available distinct papers that have indexed chunks
    if len(papers_dict) < 2:
        cursor.execute(\"\"\"
            SELECT p.id, COALESCE(p.detected_title, p.title), p.filename
            FROM papers p
            WHERE EXISTS (SELECT 1 FROM paper_chunks c WHERE c.paper_id = p.id)
            ORDER BY p.id DESC
            LIMIT 2;
        \"\"\")
        for r in cursor.fetchall():
            papers_dict[r[0]] = r

    cursor.close()
    conn.close()
    return list(papers_dict.values())[:2]"""

norm_text = text.replace("\r\n", "\n")
norm_target = target.replace("\r\n", "\n")
norm_replacement = replacement.replace("\r\n", "\n")

assert norm_target in norm_text, "Target not found in conflict_engine.py"
new_text = norm_text.replace(norm_target, norm_replacement)

with open(path, "wb") as f:
    f.write(new_text.replace("\n", "\r\n").encode("utf-8"))
print("Patched conflict_engine.py get_papers_for_comparison safely.")
