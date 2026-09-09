import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def check_connection():
    database_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0]