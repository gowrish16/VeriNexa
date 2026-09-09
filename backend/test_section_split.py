import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def search_chunks_for_keyword(paper_id, keyword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT chunk_index, chunk_text FROM chunks WHERE paper_id = %s AND chunk_text ILIKE %s ORDER BY chunk_index;",
        (paper_id, f"%{keyword}%")
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

if __name__ == "__main__":
    for keyword in ["Keywords", "3. Results", "Results", "4. Discussion"]:
        print(f"\n=========== Searching for: '{keyword}' ===========")
        matches = search_chunks_for_keyword(paper_id=1, keyword=keyword)
        for chunk_index, chunk_text in matches:
            print(f"--- Chunk {chunk_index} ---")
            print(chunk_text[:200])
            print()