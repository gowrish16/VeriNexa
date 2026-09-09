import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Ensure users table exists with required schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255),
            full_name VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # In case users table already existed with different columns, add missing columns
    cursor.execute("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255);
        ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);
        ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
    """)

    # Relax not-null on legacy password_hash if present
    cursor.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'password_hash') THEN
                ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;
                UPDATE users SET hashed_password = password_hash WHERE hashed_password IS NULL;
            END IF;
        END $$;
    """)

    # 2. Ensure papers table has user_id column
    cursor.execute("""
        ALTER TABLE papers ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
    """)

    # 3. Create audit_sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL DEFAULT 'Biomedical Audit Session',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 4. Create audit_messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_messages (
            id SERIAL PRIMARY KEY,
            session_id INTEGER REFERENCES audit_sessions(id) ON DELETE CASCADE,
            role VARCHAR(32) NOT NULL,
            content TEXT NOT NULL,
            citations_json JSONB DEFAULT '[]'::jsonb,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("[init_db] Database tables verified and migrated successfully.")

if __name__ == "__main__":
    init_database()
