import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def purge_non_biomedical_pollution():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title, filename FROM papers 
        WHERE title ILIKE '%synopsis%' 
           OR title ILIKE '%cricket%' 
           OR filename ILIKE '%synopsis%' 
           OR filename ILIKE '%cricket%';
    """)
    to_delete = cur.fetchall()
    print(f"Non-biomedical papers to purge: {to_delete}")

    for p in to_delete:
        pid = p[0]
        cur.execute("DELETE FROM paper_chunks WHERE paper_id = %s;", (pid,))
        cur.execute("DELETE FROM papers WHERE id = %s;", (pid,))
        print(f"Purged paper #{pid} ({p[1]}) and its chunks.")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    purge_non_biomedical_pollution()

