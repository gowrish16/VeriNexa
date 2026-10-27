import psycopg2

conn = psycopg2.connect('postgresql://postgres:admin123@127.0.0.1:5433/verilit')
cur = conn.cursor()

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
print("Tables:", cur.fetchall())

for table in ['papers', 'chunks', 'paper_chunks', 'document_chunks', 'documents']:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        count = cur.fetchone()[0]
        print(f"Table '{table}': {count} rows")
    except Exception as e:
        conn.rollback()
        print(f"Table '{table}': error {e}")

cur.close()
conn.close()
