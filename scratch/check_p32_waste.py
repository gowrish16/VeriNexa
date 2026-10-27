import psycopg2

conn = psycopg2.connect('postgresql://postgres:admin123@127.0.0.1:5433/verilit')
cur = conn.cursor()

cur.execute("""
SELECT id, paper_id, doc_id, SUBSTRING(chunk_text FROM 1 FOR 100) 
FROM paper_chunks 
WHERE paper_id = 32 AND (
    chunk_text ILIKE '%bin%' OR 
    chunk_text ILIKE '%litter%' OR 
    chunk_text ILIKE '%waste%' OR 
    chunk_text ILIKE '%disposal%'
);
""")
rows = cur.fetchall()
print(f"Paper 32 matching waste/bin/litter/disposal: {len(rows)} chunks")
for r in rows:
    print(r)

cur.close()
conn.close()
