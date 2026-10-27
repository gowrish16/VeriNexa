import psycopg2

conn = psycopg2.connect('postgresql://postgres:admin123@127.0.0.1:5433/verilit')
cur = conn.cursor()

cur.execute("""
SELECT id, paper_id, doc_id, chunk_index, SUBSTRING(chunk_text FROM 1 FOR 200) 
FROM paper_chunks 
WHERE chunk_text ILIKE '%waste bin%' OR chunk_text ILIKE '%littering%' OR chunk_text ILIKE '%proper disposal%';
""")
rows = cur.fetchall()
print(f"Total matching chunks across DB: {len(rows)}")
paper_ids = set()
for r in rows:
    print(r[0], "Paper ID:", r[1], "Doc ID:", r[2], "Chunk index:", r[3], "Text:", r[4][:120])
    paper_ids.add(r[1])
print("Paper IDs containing waste/litter/disposal:", paper_ids)

cur.close()
conn.close()
