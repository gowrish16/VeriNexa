import psycopg2

conn = psycopg2.connect('postgresql://postgres:admin123@127.0.0.1:5433/verilit')
cur = conn.cursor()

# Check paper 32
cur.execute("SELECT id, title, filename, user_id FROM papers WHERE id = 32;")
row = cur.fetchone()
print("Paper #32 in papers:", row)

# List all papers
cur.execute("SELECT id, title, filename, user_id FROM papers ORDER BY id;")
print("\nAll papers:")
for r in cur.fetchall():
    print(r)

# Check chunks for paper 32 in chunks vs paper_chunks
cur.execute("SELECT id, paper_id, chunk_index, SUBSTRING(chunk_text FROM 1 FOR 150) FROM chunks WHERE paper_id = 32 ORDER BY chunk_index LIMIT 5;")
print("\nFirst 5 chunks in 'chunks' for paper_id=32:")
for r in cur.fetchall():
    print(r)

cur.execute("SELECT id, paper_id, chunk_index, SUBSTRING(chunk_text FROM 1 FOR 150) FROM paper_chunks WHERE paper_id = 32 ORDER BY chunk_index LIMIT 5;")
print("\nFirst 5 chunks in 'paper_chunks' for paper_id=32:")
for r in cur.fetchall():
    print(r)

# Check if there is any chunk containing 'waste bin' or 'litter'
cur.execute("SELECT id, paper_id, chunk_index, SUBSTRING(chunk_text FROM 1 FOR 200) FROM chunks WHERE chunk_text ILIKE '%waste bin%' OR chunk_text ILIKE '%litter%' OR chunk_text ILIKE '%disposal%';")
print("\nChunks matching 'waste bin' / 'litter' / 'disposal':")
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()
