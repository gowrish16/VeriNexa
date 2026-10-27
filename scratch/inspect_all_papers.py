import psycopg2

conn = psycopg2.connect('postgresql://postgres:admin123@127.0.0.1:5433/verilit')
cur = conn.cursor()

cur.execute("SELECT id, title, filename, user_id, uploaded_at FROM papers ORDER BY id;")
papers = cur.fetchall()

print(f"Total papers: {len(papers)}")
for p in papers:
    pid, title, filename, uid, uploaded_at = p
    cur.execute("SELECT count(*) FROM paper_chunks WHERE paper_id = %s;", (pid,))
    chunk_count = cur.fetchone()[0]
    cur.execute("SELECT SUBSTRING(chunk_text FROM 1 FOR 100) FROM paper_chunks WHERE paper_id = %s ORDER BY chunk_index LIMIT 1;", (pid,))
    first_chunk = cur.fetchone()
    first_preview = first_chunk[0] if first_chunk else "NO CHUNKS"
    print(f"ID={pid:2d} | User={uid} | Title='{title}' | File='{filename}' | Chunks={chunk_count} | Preview='{first_preview[:60]}...'")

cur.close()
conn.close()
