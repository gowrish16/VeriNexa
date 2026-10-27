import os
import json
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


def get_paper_metadata(paper_id: int):
    """
    Verifies that paper_id exists in the papers table and returns its metadata.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, filename, user_id, detected_title FROM papers WHERE id = %s;",
        (paper_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None
    disp_title = row[4] or row[1]
    return {
        "id": row[0],
        "title": disp_title,
        "raw_title": row[1],
        "detected_title": disp_title,
        "filename": row[2],
        "user_id": row[3]
    }


def get_abstract_text(paper_id: int, max_chunks: int = 3) -> str:
    """
    Returns the opening chunks of a paper from PostgreSQL (paper_chunks),
    which reliably contain the title, abstract, and study objectives.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT chunk_index, chunk_text
        FROM paper_chunks
        WHERE paper_id = %s
        ORDER BY chunk_index ASC
        LIMIT %s;
        """,
        (paper_id, max_chunks)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if not rows:
        return ""
    return "\n\n".join([r[1] for r in rows])


def search_within_paper(paper_id: int, query: str = "", top_k: int = 5, abstract_chunk_count: int = 3):
    """
    Vector/semantic search strictly restricted to the body and detailed results chunks
    belonging to the specific paper_id (excluding abstract chunks to guarantee distinct comparison).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cleaned_query = (query or "").strip()
    if cleaned_query and cleaned_query.lower() not in ["all", "none", "integrity", "audit"]:
        query_embedding = model.encode(cleaned_query, batch_size=1, normalize_embeddings=True).tolist()
        cursor.execute(
            """
            SELECT chunk_index, chunk_text
            FROM paper_chunks
            WHERE paper_id = %s AND chunk_index >= %s
            ORDER BY embedding <=> %s::vector ASC
            LIMIT %s;
            """,
            (paper_id, abstract_chunk_count, query_embedding, top_k)
        )
        rows = cursor.fetchall()
    else:
        # Extract representative clinical results, endpoints, and statistical tables from body
        cursor.execute(
            """
            SELECT chunk_index, chunk_text
            FROM paper_chunks
            WHERE paper_id = %s AND chunk_index >= %s
              AND (chunk_text ILIKE '%%result%%'
                OR chunk_text ILIKE '%%trial%%'
                OR chunk_text ILIKE '%%endpoint%%'
                OR chunk_text ILIKE '%%reduction%%'
                OR chunk_text ILIKE '%%statistically significant%%'
                OR chunk_text ILIKE '%%table%%'
                OR chunk_text ILIKE '%%patient%%')
            ORDER BY chunk_index ASC
            LIMIT %s;
            """,
            (paper_id, abstract_chunk_count, top_k)
        )
        rows = cursor.fetchall()

    if not rows:
        # Fallback: take subsequent body chunks
        cursor.execute(
            """
            SELECT chunk_index, chunk_text
            FROM paper_chunks
            WHERE paper_id = %s AND chunk_index >= %s
            ORDER BY chunk_index ASC
            LIMIT %s;
            """,
            (paper_id, abstract_chunk_count, top_k)
        )
        rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows


def query_ollama(prompt: str, model_name: str = DEFAULT_MODEL, timeout: float = 120.0) -> str:
    """
    Executes a deterministic LLM query against Ollama with error handling and timeout.
    Streams packets under the hood to prevent HTTP socket read timeouts.
    """
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": True,
                "keep_alive": KEEP_ALIVE,
                "options": {
                    "temperature": DEFAULT_TEMPERATURE,
                    "num_predict": 180,
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
        return f"VERDICT: UNCLEAR\nREASON: Local LLM returned HTTP status {response.status_code}."
    except Exception as e:
        return f"VERDICT: UNCLEAR\nREASON: Local LLM inference failed or timed out ({str(e)})."


def save_integrity_result(paper_id: int, topic_query: str, verdict_text: str) -> int:
    """
    Persists flagged or evaluated integrity audit results to integrity_flags.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO integrity_flags (paper_id, topic_query, verdict_summary)
        VALUES (%s, %s, %s)
        RETURNING id;
        """,
        (paper_id, topic_query, verdict_text)
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return new_id


def check_integrity(paper_id: int, topic_query: str = "") -> str:
    """
    Performs an abstract spin audit on a paper:
    extracts the opening abstract chunks and body chunks for paper_id,
    and asks Ollama to verify consistency.
    """
    paper = get_paper_metadata(paper_id)
    if not paper:
        return f"VERDICT: UNCLEAR\nREASON: Paper ID #{paper_id} does not exist in the database."

    abstract_text = get_abstract_text(paper_id, max_chunks=3)
    if not abstract_text:
        return f"VERDICT: UNCLEAR\nREASON: No abstract or text chunks found for paper #{paper_id} ({paper['title']})."

    supporting_chunks = search_within_paper(paper_id, topic_query, top_k=5, abstract_chunk_count=3)
    if not supporting_chunks:
        return f"VERDICT: UNCLEAR\nREASON: Insufficient body text chunks indexed for paper #{paper_id}."

    supporting_text = "\n\n".join([f"[Body Chunk #{idx}]: {text}" for idx, text in supporting_chunks])

    topic_label = topic_query.strip() if topic_query and topic_query.strip() else "Overall Clinical Outcomes"

    prompt = f"""You are checking whether a biomedical research paper's abstract accurately reflects its own detailed raw results and body text.

Paper Title: {paper['title']} (File: {paper['filename']}, ID: #{paper_id})
Audit Focus: {topic_label}

Important: In medical research, a "reduction" or "decrease" in a value (like body weight, HbA1c, or blood glucose) is often the DESIRED, POSITIVE outcome of a treatment, not a negative one. Do not treat a reported reduction as contradicting a claim of "improvement" unless the abstract explicitly claims an increase.

--- Abstract Excerpt ---
{abstract_text}

--- Detailed Body & Results Excerpts from Paper #{paper_id} ---
{supporting_text}

Based ONLY on the text above, answer in this exact format:
VERDICT: [CONSISTENT / INCONSISTENT / UNCLEAR]
REASON: [one or two sentences explaining why, citing specific numbers or endpoints if mentioned]

Use INCONSISTENT only if the abstract makes a claim that is clearly not supported by, or actually contradicts, the detailed results shown — not merely because the wording differs.
"""
    result = query_ollama(prompt)
    return result


if __name__ == "__main__":
    test_pid = 32
    test_topic = "SGLT2 inhibitors as metabolic modulators"
    print(f"Testing check_integrity for paper_id={test_pid} on '{test_topic}'...\n")
    verdict = check_integrity(test_pid, test_topic)
    print("=== Integrity Check Verdict ===")
    print(verdict)
