import os
import psycopg2
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi

load_dotenv()

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def load_all_chunks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, chunk_index, chunk_text FROM chunks ORDER BY chunk_index;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def bm25_search(query, top_k=5):
    chunks = load_all_chunks()
    tokenized_corpus = [chunk_text.lower().split() for (_, _, chunk_text) in chunks]

    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()

    scores = bm25.get_scores(tokenized_query)

    scored_chunks = list(zip(chunks, scores))
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    return scored_chunks[:top_k]

if __name__ == "__main__":
    query = "effect of SGLT2 inhibitor on body weight"
    print(f"Query: {query}\n")

    results = bm25_search(query)
    for (chunk_id, chunk_index, chunk_text), score in results:
        print(f"--- Chunk {chunk_index} (BM25 score: {score:.4f}) ---")
        print(chunk_text[:150])
        print()