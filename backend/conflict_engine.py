import os
import psycopg2
import requests
from dotenv import load_dotenv
from hybrid_search import hybrid_search

load_dotenv()


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def retrieve_claims_per_paper(query, top_k_per_paper=3):
    """
    Runs hybrid search, then groups the top results by which paper they came from.
    Returns a dict: {paper_id: [(chunk_index, chunk_text, score), ...]}
    """
    results = hybrid_search(query, top_k=20)  # get a wider pool, then split by paper

    conn = get_connection()
    cursor = conn.cursor()

    grouped = {}
    for chunk_id, chunk_index, chunk_text, score in results:
        cursor.execute("SELECT paper_id FROM chunks WHERE id = %s;", (chunk_id,))
        paper_id = cursor.fetchone()[0]

        if paper_id not in grouped:
            grouped[paper_id] = []

        if len(grouped[paper_id]) < top_k_per_paper:
            grouped[paper_id].append((chunk_index, chunk_text, score))

    cursor.close()
    conn.close()
    return grouped


def query_ollama(prompt, model="llama3.1:8b"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }
    )
    return response.json()["response"]



def compare_claims(query, grouped_chunks):
    """
    Takes the grouped chunks (from retrieve_claims_per_paper) and asks the LLM
    to judge whether the papers agree, disagree, or are unclear on the query topic.
    """
    if len(grouped_chunks) < 2:
        return "Not enough papers with relevant content to compare."

    paper_ids = list(grouped_chunks.keys())
    paper_a_id, paper_b_id = paper_ids[0], paper_ids[1]

    paper_a_text = "\n".join([text for _, text, _ in grouped_chunks[paper_a_id]])
    paper_b_text = "\n".join([text for _, text, _ in grouped_chunks[paper_b_id]])

    prompt = f"""You are analyzing two biomedical research paper excerpts to check if they agree or disagree about a specific topic.

Topic: {query}

--- Excerpt from Paper A (id={paper_a_id}) ---
{paper_a_text}

--- Excerpt from Paper B (id={paper_b_id}) ---
{paper_b_text}

Based only on the text above, answer in this exact format:
VERDICT: [AGREE / PARTIAL / CONTRADICT / UNCLEAR]
REASON: [one or two sentences explaining why, citing specific numbers if mentioned]

Use PARTIAL when the papers agree on the overall outcome (e.g., both report weight loss) but disagree on a specific detail such as mechanism, magnitude, or population studied.
"""

    result = query_ollama(prompt)
    return result

def save_verdict_to_db(grouped_chunks, query, verdict_text):
    """
    Saves the comparison result into the contradictions table.
    Links to one representative chunk from each paper (the top-ranked one).
    """
    paper_ids = list(grouped_chunks.keys())
    if len(paper_ids) < 2:
        return None

    paper_a_id, paper_b_id = paper_ids[0], paper_ids[1]

    # Use thetop chunk from each of the  paper as the representative "chunk_id" pair
    chunk_a_index = grouped_chunks[paper_a_id][0][0]
    chunk_b_index = grouped_chunks[paper_b_id][0][0]

    conn = get_connection()
    cursor = conn.cursor()

    # Look up the actual chunk ids from paper_id + chunk_index
    cursor.execute(
        "SELECT id FROM chunks WHERE paper_id = %s AND chunk_index = %s;",
        (paper_a_id, chunk_a_index)
    )
    chunk_a_id = cursor.fetchone()[0]

    cursor.execute(
        "SELECT id FROM chunks WHERE paper_id = %s AND chunk_index = %s;",
        (paper_b_id, chunk_b_index)
    )
    chunk_b_id = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO contradictions (chunk_id_a, chunk_id_b, conflict_summary, metric_a, metric_b)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (chunk_a_id, chunk_b_id, f"Query: {query}\n{verdict_text}", None, None)
    )
    new_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()
    return new_id

if __name__ == "__main__":
    query = "mechanism by which SGLT2 inhibitors cause weight loss"
    print(f"Query: {query}\n")

    grouped = retrieve_claims_per_paper(query)
    verdict = compare_claims(query, grouped)

    print("=== Conflict Engine Verdict ===")
    print(verdict)

    saved_id = save_verdict_to_db(grouped, query, verdict)
    print(f"\nSaved to contradictions table with id: {saved_id}")
