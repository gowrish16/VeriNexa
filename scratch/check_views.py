import psycopg2

conn = psycopg2.connect('postgresql://postgres:admin123@127.0.0.1:5433/verilit')
cur = conn.cursor()

cur.execute("SELECT table_name, table_type FROM information_schema.tables WHERE table_name IN ('chunks', 'paper_chunks', 'document_chunks');")
print("Table types:", cur.fetchall())

# Check view definitions if view
cur.execute("SELECT table_name, view_definition FROM information_schema.views WHERE table_name IN ('chunks', 'paper_chunks', 'document_chunks');")
for r in cur.fetchall():
    print("View definition for", r[0], ":\n", r[1])

cur.close()
conn.close()
