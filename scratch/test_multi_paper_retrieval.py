import psycopg2
import os
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
conn = psycopg2.connect("postgresql://postgres:admin123@127.0.0.1:5433/verilit")
cur = conn.cursor()

# Get papers for user 35
cur.execute("SELECT id, title, filename FROM papers WHERE user_id = 35 ORDER BY id;")
papers = cur.fetchall()
print("Papers for user 35:", papers)

query = "effect of SGLT2 inhibitor on body weight and glycemic control"
query_emb = model.encode(query).tolist()

for pid, title, filename in papers:
    cur.execute("""
        SELECT chunk_index, chunk_text, (embedding <=> %s::vector) AS dist
        FROM paper_chunks
        WHERE paper_id = %s
        ORDER BY embedding <=> %s::vector ASC
        LIMIT 3;
    """, (query_emb, pid, query_emb))
    rows = cur.fetchall()
    print(f"\n--- Paper #{pid} ({title} - {filename}): {len(rows)} chunks ---")
    for r in rows:
        print(f"  Chunk {r[0]} (dist: {r[2]:.4f}): {r[1][:120]}...")

cur.close()
conn.close()
