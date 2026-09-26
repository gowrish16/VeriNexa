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

    # 2. Ensure pgvector extension and papers table has user_id column
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            filename VARCHAR(255) NOT NULL,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        ALTER TABLE papers ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
    """)

    # 3. Create paper_chunks table strictly scoped by user_id with bounding boxes and pgvector(384)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_chunks (
            id SERIAL PRIMARY KEY,
            paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            chunk_text TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            page_number INTEGER DEFAULT 1,
            bbox_x0 FLOAT DEFAULT 0.0,
            bbox_y0 FLOAT DEFAULT 0.0,
            bbox_x1 FLOAT DEFAULT 0.0,
            bbox_y1 FLOAT DEFAULT 0.0,
            embedding vector(384)
        );
    """)

    # Migrations for paper_chunks columns if table existed
    cursor.execute("""
        ALTER TABLE paper_chunks ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
        ALTER TABLE paper_chunks ADD COLUMN IF NOT EXISTS page_number INTEGER DEFAULT 1;
        ALTER TABLE paper_chunks ADD COLUMN IF NOT EXISTS bbox_x0 FLOAT DEFAULT 0.0;
        ALTER TABLE paper_chunks ADD COLUMN IF NOT EXISTS bbox_y0 FLOAT DEFAULT 0.0;
        ALTER TABLE paper_chunks ADD COLUMN IF NOT EXISTS bbox_x1 FLOAT DEFAULT 0.0;
        ALTER TABLE paper_chunks ADD COLUMN IF NOT EXISTS bbox_y1 FLOAT DEFAULT 0.0;
    """)

    # Create indices for fast scoped retrieval
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_paper_chunks_user_id ON paper_chunks(user_id);
        CREATE INDEX IF NOT EXISTS idx_paper_chunks_paper_id ON paper_chunks(paper_id);
        CREATE INDEX IF NOT EXISTS idx_paper_chunks_user_paper ON paper_chunks(user_id, paper_id);
    """)

    # Safely handle transition from legacy BASE TABLE 'chunks' to 'paper_chunks' + VIEW 'chunks'
    cursor.execute("""
        SELECT table_type FROM information_schema.tables WHERE table_name = 'chunks';
    """)
    table_type_row = cursor.fetchone()
    if table_type_row and table_type_row[0] == 'BASE TABLE':
        cursor.execute("""
            INSERT INTO paper_chunks (id, paper_id, chunk_text, chunk_index, embedding)
            SELECT id, paper_id, chunk_text, chunk_index, embedding FROM chunks
            ON CONFLICT (id) DO NOTHING;
        """)
        cursor.execute("DROP TABLE chunks CASCADE;")

    # Create view alias 'chunks' pointing to 'paper_chunks' for backward compatibility
    cursor.execute("""
        CREATE OR REPLACE VIEW chunks AS
        SELECT id, paper_id, user_id, chunk_text, chunk_index, page_number, bbox_x0, bbox_y0, bbox_x1, bbox_y1, embedding
        FROM paper_chunks;
    """)

    # 4. Create audit_sessions table strictly scoped by user_id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL DEFAULT 'Biomedical Audit Session',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        ALTER TABLE audit_sessions ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
    """)

    # 5. Create audit_messages table
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

    # 6. Synchronize primary key sequences for all tables to prevent UniqueViolation collisions
    cursor.execute("""
        SELECT setval(pg_get_serial_sequence('paper_chunks', 'id'), COALESCE((SELECT MAX(id) FROM paper_chunks), 1));
        SELECT setval(pg_get_serial_sequence('papers', 'id'), COALESCE((SELECT MAX(id) FROM papers), 1));
        SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE((SELECT MAX(id) FROM users), 1));
        SELECT setval(pg_get_serial_sequence('audit_sessions', 'id'), COALESCE((SELECT MAX(id) FROM audit_sessions), 1));
        SELECT setval(pg_get_serial_sequence('audit_messages', 'id'), COALESCE((SELECT MAX(id) FROM audit_messages), 1));
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("[init_db] Database tables, sequences, and paper_chunks schema verified and synchronized successfully.")

if __name__ == "__main__":
    init_database()
