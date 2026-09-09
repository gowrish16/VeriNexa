import os
import psycopg2
import requests
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def get_abstract_text(paper_id, max_chunks=5):
    """
    Returns the first few chunks of a paper, which reliably contain the abstract.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT chunk_text FROM chunks WHERE paper_id = %s ORDER BY chunk_index LIMIT %s;",
        (paper_id, max_chunks)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return "\n".join([r[0] for r in rows])

def search_within_paper(paper_id, query, top_k=5):
    """
    Vector search restricted to chunks belonging to a single paper only.
    """
    query_embedding = model.encode(query).tolist()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT chunk_index, chunk_text
        FROM chunks
        WHERE paper_id = %s
        ORDER BY embedding <=> %s::vector ASC
        LIMIT %s;
        """,
        (paper_id, query_embedding, top_k)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def query_ollama(prompt, model_name="llama3.1:8b"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }
    )
    return response.json()["response"]

def check_integrity(paper_id, topic_query):
    abstract_text = get_abstract_text(paper_id)
    supporting_chunks = search_within_paper(paper_id, topic_query)
    supporting_text = "\n".join([text for _, text in supporting_chunks])

    prompt = f"""You are checking whether a research paper's abstract accurately reflects its own detailed results.

Important: In medical research, a "reduction" or "decrease" in a value (like body weight, HbA1c, or blood glucose) is often the DESIRED, POSITIVE outcome of a treatment, not a negative one. Do not treat a reported reduction as contradicting a claim of "improvement" unless the abstract explicitly claims an increase.

--- Abstract ---
{abstract_text}

--- Detailed results text from the same paper (on the topic: {topic_query}) ---
{supporting_text}

Based only on the text above, answer in this exact format:
VERDICT: [CONSISTENT / INCONSISTENT / UNCLEAR]
REASON: [one or two sentences explaining why, citing specific numbers if mentioned]

Use INCONSISTENT only if the abstract makes a claim that is clearly not supported by, or actually contradicts, the detailed results shown — not merely because the wording differs.
"""
def save_integrity_result(paper_id, topic_query, verdict_text):
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

    result = query_ollama(prompt)
    return result

if __name__ == "__main__":
    paper_id = 1
    topic_query = "SGLT2 inhibitor effect on body weight"

    print(f"Checking integrity for paper_id={paper_id} on topic: {topic_query}\n")
    verdict = check_integrity(paper_id, topic_query)

    print("=== Integrity Check Verdict ===")
    print(verdict)

