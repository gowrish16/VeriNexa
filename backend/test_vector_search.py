import os
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def vector_search(query, top_k=5):
    query_embedding = model.encode(query).tolist()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, chunk_index, chunk_text, embedding <=> %s::vector AS distance
        FROM chunks
        ORDER BY distance ASC
        LIMIT %s;
        """,
        (query_embedding, top_k)
    )
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return results

if __name__ == "__main__":
    query = "effect of SGLT2 inhibitor on body weight"
    print(f"Query: {query}\n")

    results = vector_search(query)
    for row in results:
        chunk_id, chunk_index, chunk_text, distance = row
        print(f"--- Chunk {chunk_index} (distance: {distance:.4f}) ---")
        print(chunk_text[:150])
        print()