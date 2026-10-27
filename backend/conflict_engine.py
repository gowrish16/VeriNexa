import os
import json
from typing import Optional, List, Dict, Tuple
import psycopg2
import requests
from dotenv import load_dotenv
from config import DEFAULT_MODEL, KEEP_ALIVE, NUM_THREAD, NUM_GPU, DEFAULT_TEMPERATURE, OLLAMA_BASE_URL
from sentence_transformers import SentenceTransformer

load_dotenv()
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def get_papers_for_comparison(user_id: Optional[int] = None, paper_ids: Optional[List[int]] = None) -> List[Tuple[int, str, str]]:
    """
    Identifies the exact 2 papers for cross-examination.
    When explicit paper_ids are provided, strictly restricts retrieval to those 2 IDs.
    Preserves the exact requested pair order: [Paper 1, Paper 2].
    Never performs unconstrained global similarity search.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if paper_ids and len(paper_ids) >= 2:
        target_ids = [int(p) for p in paper_ids[:2]]
        cursor.execute(
            """
            SELECT id, COALESCE(detected_title, title), filename
            FROM papers
            WHERE id = ANY(%s);
            """,
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
            """
            SELECT id, COALESCE(detected_title, title), filename
            FROM papers
            WHERE id = ANY(%s);
            """,
            (target_ids,)
        )
        for r in cursor.fetchall():
            papers_dict[r[0]] = r

    if len(papers_dict) < 2 and user_id is not None:
        cursor.execute(
            """
            SELECT id, COALESCE(detected_title, title), filename
            FROM papers
            WHERE user_id = %s
            ORDER BY id;
            """,
            (user_id,)
        )
        for r in cursor.fetchall():
            papers_dict[r[0]] = r

    # Fallback: if fewer than 2 papers found, fetch available distinct papers that have indexed chunks
    if len(papers_dict) < 2:
        cursor.execute("""
            SELECT p.id, COALESCE(p.detected_title, p.title), p.filename
            FROM papers p
            WHERE EXISTS (SELECT 1 FROM paper_chunks c WHERE c.paper_id = p.id)
            ORDER BY p.id DESC
            LIMIT 2;
        """)
        for r in cursor.fetchall():
            papers_dict[r[0]] = r

    cursor.close()
    conn.close()
    return list(papers_dict.values())[:2]


def retrieve_claims_per_paper(
    query: str,
    top_k_per_paper: int = 2,
    user_id: Optional[int] = None,
    paper_ids: Optional[List[int]] = None
) -> Tuple[Dict[int, List[Tuple[int, str, float]]], Dict[int, dict]]:
    """
    Performs per-paper vector similarity search via pgvector.
    Guarantees that each active paper receives top 2 chunks without one paper dominating.
    Includes a fallback so even papers with lower similarity scores have their top chunk included.
    Returns:
      grouped: {paper_id: [(chunk_index, chunk_text, similarity_score), ...]}
      paper_meta: {paper_id: {"title": title, "filename": filename}}
    """
    papers = get_papers_for_comparison(user_id=user_id, paper_ids=paper_ids)
    if len(papers) < 2:
        return {}, {}

    cleaned_query = (query or "").strip()
    query_emb = model.encode(cleaned_query, batch_size=1, normalize_embeddings=True).tolist()

    conn = get_connection()
    cursor = conn.cursor()

    grouped = {}
    paper_meta = {}

    for p in papers:
        pid, ptitle, pfilename = p[0], p[1], p[2]
        paper_meta[pid] = {"title": ptitle, "filename": pfilename}

        # Query pgvector specifically for this paper_id
        cursor.execute(
            """
            SELECT chunk_index, chunk_text, (1.0 - (embedding <=> %s::vector)) AS similarity
            FROM paper_chunks
            WHERE paper_id = %s
            ORDER BY embedding <=> %s::vector ASC
            LIMIT %s;
            """,
            (query_emb, pid, query_emb, top_k_per_paper)
        )
        rows = cursor.fetchall()

        # Fallback: if paper had no vector match or lower similarity, grab top results/findings chunk
        if not rows:
            cursor.execute(
                """
                SELECT chunk_index, chunk_text, 0.50 AS similarity
                FROM paper_chunks
                WHERE paper_id = %s
                ORDER BY chunk_index ASC
                LIMIT 1;
                """,
                (pid,)
            )
            rows = cursor.fetchall()

        if rows:
            grouped[pid] = [(r[0], r[1], float(r[2])) for r in rows]

    cursor.close()
    conn.close()
    return grouped, paper_meta


def query_ollama(prompt: str, model: str = DEFAULT_MODEL, timeout: float = 120.0, num_predict: int = 400) -> str:
    """
    Calls Ollama with keep_alive=KEEP_ALIVE, num_predict=400, num_thread=NUM_THREAD, num_gpu=NUM_GPU.
    Streams packets under the hood to ensure live connection and prevent read timeouts.
    """
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": True,
                "keep_alive": KEEP_ALIVE,
                "options": {
                    "temperature": DEFAULT_TEMPERATURE,
                    "num_predict": num_predict,
                    "num_ctx": 2048,
                    "num_thread": NUM_THREAD,
                    "num_gpu": NUM_GPU,
                }
            },
            stream=True,
            timeout=timeout
        )
        if response.status_code == 200:
            full_response = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    full_response += chunk.get("response", "")
            return full_response.strip()
        return f"VERDICT: UNCLEAR - Local LLM returned status {response.status_code}."
    except Exception as e:
        return f"VERDICT: UNCLEAR - Cross-examination timed out or was unavailable ({str(e)})."


def compare_claims(query: str, grouped_chunks: dict, paper_meta: dict = None) -> str:
    """
    Cross-examines findings between at least 2 distinct papers.
    """
    if len(grouped_chunks) < 2:
        return "VERDICT: UNCLEAR - Not enough papers with relevant content to compare. At least 2 indexed papers are required."

    paper_ids = list(grouped_chunks.keys())
    paper_a_id, paper_b_id = paper_ids[0], paper_ids[1]

    meta_a = (paper_meta or {}).get(paper_a_id, {"title": f"Paper #{paper_a_id}", "filename": ""})
    meta_b = (paper_meta or {}).get(paper_b_id, {"title": f"Paper #{paper_b_id}", "filename": ""})

    paper_a_text = "\n\n".join([f"[Excerpt {idx}]: {text}" for idx, text, _ in grouped_chunks[paper_a_id][:2]])
    paper_b_text = "\n\n".join([f"[Excerpt {idx}]: {text}" for idx, text, _ in grouped_chunks[paper_b_id][:2]])

    prompt = f"""You are a clinical trials research auditor cross-examining findings across two biomedical research papers.

Topic: {query}

--- Paper 1 (ID: #{paper_a_id} | Title: {meta_a['title']} | File: {meta_a['filename']}) ---
{paper_a_text}

--- Paper 2 (ID: #{paper_b_id} | Title: {meta_b['title']} | File: {meta_b['filename']}) ---
{paper_b_text}

TASK:
Directly compare the findings between Paper 1 and Paper 2 on the topic above. Cross-examine reported effects, sample cohorts, dosages, endpoints (e.g. HbA1c, body weight, mortality, adverse events), and clinical outcomes.

Provide exactly 3 concise comparison bullet points, then summarize in one final sentence. Do not exceed 300 words. State the final arbitration verdict once at the very end in the format 'VERDICT: <CONSISTENT | CONFLICT | PARTIAL> - <brief reason>'. Do not repeat the verdict label inline.

Guidelines:
- Use CONSISTENT if both studies report concordant clinical outcomes on the topic.
- Use PARTIAL if the studies agree on the general directional outcome but differ in dosage, cohort demographics, baseline values, or magnitude.
- Use CONFLICT if one study reports an improvement/efficacy and the other reports no effect or opposite effect under comparable conditions.
- Use UNCLEAR only if neither paper provides relevant findings on the topic.
"""
    result = query_ollama(prompt, timeout=120.0, num_predict=400)
    return result


def save_verdict_to_db(grouped_chunks: dict, query: str, verdict_text: str, user_id: Optional[int] = None) -> Optional[int]:
    """
    Saves the comparison result into the contradictions table.
    Links to one representative chunk from each paper (the top-ranked one).
    """
    paper_ids = list(grouped_chunks.keys())
    if len(paper_ids) < 2:
        return None

    paper_a_id, paper_b_id = paper_ids[0], paper_ids[1]
    if not grouped_chunks.get(paper_a_id) or not grouped_chunks.get(paper_b_id):
        return None

    chunk_a_index = grouped_chunks[paper_a_id][0][0]
    chunk_b_index = grouped_chunks[paper_b_id][0][0]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM paper_chunks WHERE paper_id = %s AND chunk_index = %s LIMIT 1;",
        (paper_a_id, chunk_a_index)
    )
    row_a = cursor.fetchone()
    chunk_a_id = row_a[0] if row_a else None

    cursor.execute(
        "SELECT id FROM paper_chunks WHERE paper_id = %s AND chunk_index = %s LIMIT 1;",
        (paper_b_id, chunk_b_index)
    )
    row_b = cursor.fetchone()
    chunk_b_id = row_b[0] if row_b else None

    if not chunk_a_id or not chunk_b_id:
        cursor.close()
        conn.close()
        return None

    cursor.execute(
        """
        INSERT INTO contradictions (chunk_id_a, chunk_id_b, conflict_summary, metric_a, metric_b, user_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (chunk_a_id, chunk_b_id, f"Query: {query}\n{verdict_text}", None, None, user_id)
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return new_id


if __name__ == "__main__":
    test_query = "mechanism by which SGLT2 inhibitors cause weight loss and glycemic control"
    print(f"Query: {test_query}\n")

    grouped, meta = retrieve_claims_per_paper(test_query, user_id=35)
    print(f"Retrieved papers: {list(grouped.keys())}")
    for pid in grouped:
        print(f"Paper {pid} ({meta[pid]['title']}): {len(grouped[pid])} chunks")

    verdict = compare_claims(test_query, grouped, meta)
    print("\n=== Conflict Engine Verdict ===")
    print(verdict)
