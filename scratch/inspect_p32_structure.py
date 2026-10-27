import psycopg2

conn = psycopg2.connect('postgresql://postgres:admin123@127.0.0.1:5433/verilit')
cur = conn.cursor()

cur.execute("""
    SELECT chunk_index, page_number, SUBSTRING(chunk_text FROM 1 FOR 120)
    FROM paper_chunks
    WHERE paper_id = 32
    ORDER BY chunk_index ASC
    LIMIT 20;
""")
print("Paper 32 Chunks (first 20):")
for r in cur.fetchall():
    print(f"Index {r[0]:2d} | Page {r[1]} | {r[2]}")

cur.execute("""
    SELECT count(*)
    FROM paper_chunks
    WHERE paper_id = 32;
""")
print("\nTotal chunks for Paper 32:", cur.fetchone()[0])

cur.close()
conn.close()
