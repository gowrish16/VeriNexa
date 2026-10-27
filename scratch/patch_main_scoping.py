import os

path = r"C:\Projects\VeriNexa\backend\main.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update /compare endpoint
target_compare = """@app.get("/compare")
def compare_papers(
    query: str,
    paper_ids: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    effective_user_id = current_user["id"] if current_user else user_id
    parsed_paper_ids = None
    if paper_ids:
        try:
            parsed_paper_ids = [int(p.strip()) for p in paper_ids.split(",") if p.strip()]
        except Exception:
            parsed_paper_ids = None

    result = conflict_graph.invoke({
        "query": query,
        "user_id": effective_user_id,
        "paper_ids": parsed_paper_ids
    })"""

replacement_compare = """@app.get("/compare")
def compare_papers(
    query: str,
    paper_ids: Optional[str] = Query(None),
    paper_id_1: Optional[int] = Query(None),
    paper_id_2: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    effective_user_id = current_user["id"] if current_user else user_id
    parsed_paper_ids = None

    if paper_id_1 is not None and paper_id_2 is not None:
        parsed_paper_ids = [int(paper_id_1), int(paper_id_2)]
    elif paper_ids:
        try:
            parsed_paper_ids = [int(p.strip()) for p in paper_ids.split(",") if p.strip()]
        except Exception:
            parsed_paper_ids = None

    if parsed_paper_ids and len(parsed_paper_ids) >= 2:
        parsed_paper_ids = parsed_paper_ids[:2]

    result = conflict_graph.invoke({
        "query": query,
        "user_id": effective_user_id,
        "paper_ids": parsed_paper_ids
    })"""

# 2. Update chat_audit_stream target_paper_id and fetch_citations
target_stream = """            # Multi-Paper Workspace Corpus Mode vs Single Paper Mode
            is_corpus_mode = (payload.paper_id is None or payload.paper_id <= 0)
            target_top_k = 4 if is_corpus_mode else 3
            target_paper_id = None if is_corpus_mode else payload.paper_id

            # Execute top relevant hybrid search asynchronously
            raw_results = await async_hybrid_search(
                question, top_k=target_top_k, paper_id=target_paper_id, user_id=current_user["id"]
            )

            # Fetch citation details including layout bboxes in thread
            def fetch_citations():
                conn = get_connection()
                cursor = conn.cursor()
                citations_list = []
                for item in raw_results:
                    cid = item[0]
                    c_index = item[1]
                    score = item[3]
                    page_num = item[4] if len(item) > 4 else 1
                    x0 = item[5] if len(item) > 5 else 0.0
                    y0 = item[6] if len(item) > 6 else 0.0
                    x1 = item[7] if len(item) > 7 else 0.0
                    y1 = item[8] if len(item) > 8 else 0.0

                    cursor.execute(
                        \"\"\"
                        SELECT c.id, c.paper_id, c.chunk_index, c.chunk_text, p.title, p.filename, c.page_number, c.bbox_x0, c.bbox_y0, c.bbox_x1, c.bbox_y1, p.detected_title
                        FROM paper_chunks c
                        JOIN papers p ON c.paper_id = p.id
                        WHERE c.id = %s AND (c.user_id = %s OR p.user_id = %s);
                        \"\"\",
                        (cid, current_user["id"], current_user["id"])
                    )"""

replacement_stream = """            # Strict Single Paper Mode vs Multi-Paper Corpus Mode
            target_paper_id = None
            if payload.paper_id is not None:
                try:
                    pid = int(payload.paper_id)
                    if pid > 0:
                        target_paper_id = pid
                except (ValueError, TypeError):
                    target_paper_id = None

            target_top_k = 3 if target_paper_id is not None else 4

            # Execute top relevant hybrid search asynchronously strictly scoped by paper_id
            raw_results = await async_hybrid_search(
                question, top_k=target_top_k, paper_id=target_paper_id, user_id=current_user["id"]
            )

            # Fetch citation details including layout bboxes in thread
            def fetch_citations():
                conn = get_connection()
                cursor = conn.cursor()
                citations_list = []
                for item in raw_results:
                    cid = item[0]
                    c_index = item[1]
                    score = item[3]
                    page_num = item[4] if len(item) > 4 else 1
                    x0 = item[5] if len(item) > 5 else 0.0
                    y0 = item[6] if len(item) > 6 else 0.0
                    x1 = item[7] if len(item) > 7 else 0.0
                    y1 = item[8] if len(item) > 8 else 0.0

                    if target_paper_id is not None:
                        cursor.execute(
                            \"\"\"
                            SELECT c.id, c.paper_id, c.chunk_index, c.chunk_text, p.title, p.filename, c.page_number, c.bbox_x0, c.bbox_y0, c.bbox_x1, c.bbox_y1, p.detected_title
                            FROM paper_chunks c
                            JOIN papers p ON c.paper_id = p.id
                            WHERE c.id = %s AND c.paper_id = %s AND (c.user_id = %s OR p.user_id = %s);
                            \"\"\",
                            (cid, target_paper_id, current_user["id"], current_user["id"])
                        )
                    else:
                        cursor.execute(
                            \"\"\"
                            SELECT c.id, c.paper_id, c.chunk_index, c.chunk_text, p.title, p.filename, c.page_number, c.bbox_x0, c.bbox_y0, c.bbox_x1, c.bbox_y1, p.detected_title
                            FROM paper_chunks c
                            JOIN papers p ON c.paper_id = p.id
                            WHERE c.id = %s AND (c.user_id = %s OR p.user_id = %s);
                            \"\"\",
                            (cid, current_user["id"], current_user["id"])
                        )"""

# 3. Update chat_audit target_paper_id and fetch_citations
target_chat = """    # Multi-Paper Workspace Corpus Mode vs Single Paper Mode
    is_corpus_mode = (payload.paper_id is None or payload.paper_id <= 0)
    target_top_k = 4 if is_corpus_mode else 3
    target_paper_id = None if is_corpus_mode else payload.paper_id

    raw_results = await async_hybrid_search(
        question, top_k=target_top_k, paper_id=target_paper_id, user_id=current_user["id"]
    )

    def fetch_citations():
        conn = get_connection()
        cursor = conn.cursor()
        citations_list = []
        for item in raw_results:
            cid, c_index, c_text, score = item[0], item[1], item[2], item[3]
            page_num = item[4] if len(item) > 4 else 1
            x0 = item[5] if len(item) > 5 else 0.0
            y0 = item[6] if len(item) > 6 else 0.0
            x1 = item[7] if len(item) > 7 else 0.0
            y1 = item[8] if len(item) > 8 else 0.0

            cursor.execute(
                \"\"\"
                SELECT c.id, c.paper_id, c.chunk_index, c.chunk_text, p.title, p.filename, c.page_number, c.bbox_x0, c.bbox_y0, c.bbox_x1, c.bbox_y1, p.detected_title
                FROM paper_chunks c
                JOIN papers p ON c.paper_id = p.id
                WHERE c.id = %s AND (c.user_id = %s OR p.user_id = %s);
                \"\"\",
                (cid, current_user["id"], current_user["id"])
            )"""

replacement_chat = """    # Strict Single Paper Mode vs Multi-Paper Corpus Mode
    target_paper_id = None
    if payload.paper_id is not None:
        try:
            pid = int(payload.paper_id)
            if pid > 0:
                target_paper_id = pid
        except (ValueError, TypeError):
            target_paper_id = None

    target_top_k = 3 if target_paper_id is not None else 4

    raw_results = await async_hybrid_search(
        question, top_k=target_top_k, paper_id=target_paper_id, user_id=current_user["id"]
    )

    def fetch_citations():
        conn = get_connection()
        cursor = conn.cursor()
        citations_list = []
        for item in raw_results:
            cid, c_index, c_text, score = item[0], item[1], item[2], item[3]
            page_num = item[4] if len(item) > 4 else 1
            x0 = item[5] if len(item) > 5 else 0.0
            y0 = item[6] if len(item) > 6 else 0.0
            x1 = item[7] if len(item) > 7 else 0.0
            y1 = item[8] if len(item) > 8 else 0.0

            if target_paper_id is not None:
                cursor.execute(
                    \"\"\"
                    SELECT c.id, c.paper_id, c.chunk_index, c.chunk_text, p.title, p.filename, c.page_number, c.bbox_x0, c.bbox_y0, c.bbox_x1, c.bbox_y1, p.detected_title
                    FROM paper_chunks c
                    JOIN papers p ON c.paper_id = p.id
                    WHERE c.id = %s AND c.paper_id = %s AND (c.user_id = %s OR p.user_id = %s);
                    \"\"\",
                    (cid, target_paper_id, current_user["id"], current_user["id"])
                )
            else:
                cursor.execute(
                    \"\"\"
                    SELECT c.id, c.paper_id, c.chunk_index, c.chunk_text, p.title, p.filename, c.page_number, c.bbox_x0, c.bbox_y0, c.bbox_x1, c.bbox_y1, p.detected_title
                    FROM paper_chunks c
                    JOIN papers p ON c.paper_id = p.id
                    WHERE c.id = %s AND (c.user_id = %s OR p.user_id = %s);
                    \"\"\",
                    (cid, current_user["id"], current_user["id"])
                )"""

norm_text = text.replace("\r\n", "\n")

for t, r, name in [
    (target_compare, replacement_compare, "/compare"),
    (target_stream, replacement_stream, "chat_audit_stream"),
    (target_chat, replacement_chat, "chat_audit")
]:
    nt = t.replace("\r\n", "\n")
    nr = r.replace("\r\n", "\n")
    assert nt in norm_text, f"Target {name} not found in main.py"
    norm_text = norm_text.replace(nt, nr)

with open(path, "wb") as f:
    f.write(norm_text.replace("\n", "\r\n").encode("utf-8"))
print("Patched main.py compare and chat endpoints safely.")
