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
        ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;
    """)

    # Create password_reset_tokens table for secure email recovery
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            email VARCHAR(255) NOT NULL,
            token VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
            used BOOLEAN DEFAULT FALSE
        );
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
        ALTER TABLE papers ADD COLUMN IF NOT EXISTS detected_title TEXT;
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
        ALTER TABLE paper_chunks ADD COLUMN IF NOT EXISTS doc_id VARCHAR(128);
    """)

    # Populate doc_id from papers table for any existing paper_chunks where doc_id is null
    cursor.execute("""
        UPDATE paper_chunks c
        SET doc_id = p.title
        FROM papers p
        WHERE c.paper_id = p.id AND c.doc_id IS NULL;
    """)

    # Ensure all existing paper_chunks bounding boxes are normalized (0.0 to 1.0)
    cursor.execute("""
        UPDATE paper_chunks 
        SET bbox_x0 = ROUND((bbox_x0 / 612.0)::numeric, 4),
            bbox_y0 = ROUND((bbox_y0 / 792.0)::numeric, 4),
            bbox_x1 = ROUND((bbox_x1 / 612.0)::numeric, 4),
            bbox_y1 = ROUND((bbox_y1 / 792.0)::numeric, 4)
        WHERE bbox_x1 > 1.0;
    """)

    # Create indices for fast scoped retrieval
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_paper_chunks_user_id ON paper_chunks(user_id);
        CREATE INDEX IF NOT EXISTS idx_paper_chunks_paper_id ON paper_chunks(paper_id);
        CREATE INDEX IF NOT EXISTS idx_paper_chunks_doc_id ON paper_chunks(doc_id);
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
    cursor.execute("DROP VIEW IF EXISTS chunks CASCADE;")
    cursor.execute("""
        CREATE OR REPLACE VIEW chunks AS
        SELECT id, paper_id, user_id, doc_id, chunk_text, chunk_index, page_number, bbox_x0, bbox_y0, bbox_x1, bbox_y1, embedding
        FROM paper_chunks;
    """)

    # Create view alias 'document_chunks' with full SRS compliance and updatable triggers
    cursor.execute("DROP VIEW IF EXISTS document_chunks CASCADE;")
    cursor.execute("""
        CREATE OR REPLACE VIEW document_chunks AS
        SELECT 
            c.id,
            COALESCE(c.doc_id, p.title, p.filename, c.paper_id::text) AS doc_id,
            c.paper_id,
            c.user_id,
            COALESCE(c.user_id::text, 'default') AS tenant_id,
            c.page_number AS page_num,
            c.page_number,
            c.chunk_text,
            c.chunk_index,
            c.bbox_x0,
            c.bbox_y0,
            c.bbox_x1,
            c.bbox_y1,
            612.0::numeric(8,2) AS page_width,
            792.0::numeric(8,2) AS page_height,
            c.embedding
        FROM paper_chunks c
        LEFT JOIN papers p ON c.paper_id = p.id;

        CREATE OR REPLACE FUNCTION delete_document_chunk() RETURNS trigger AS $$
        BEGIN
            DELETE FROM paper_chunks WHERE id = OLD.id;
            RETURN OLD;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS trg_delete_document_chunk ON document_chunks;
        CREATE TRIGGER trg_delete_document_chunk
        INSTEAD OF DELETE ON document_chunks
        FOR EACH ROW EXECUTE FUNCTION delete_document_chunk();

        CREATE OR REPLACE FUNCTION insert_document_chunk() RETURNS trigger AS $$
        DECLARE
            target_paper_id INTEGER;
        BEGIN
            SELECT id INTO target_paper_id FROM papers WHERE title = NEW.doc_id OR filename = NEW.doc_id LIMIT 1;
            IF target_paper_id IS NULL THEN
                INSERT INTO papers (title, filename) VALUES (NEW.doc_id, NEW.doc_id) RETURNING id INTO target_paper_id;
            END IF;
            INSERT INTO paper_chunks (
                paper_id, doc_id, chunk_text, chunk_index, page_number,
                bbox_x0, bbox_y0, bbox_x1, bbox_y1, embedding
            ) VALUES (
                target_paper_id, NEW.doc_id, NEW.chunk_text, COALESCE(NEW.chunk_index, 0),
                COALESCE(NEW.page_num, NEW.page_number, 1),
                COALESCE(NEW.bbox_x0, 0.0), COALESCE(NEW.bbox_y0, 0.0),
                COALESCE(NEW.bbox_x1, 0.0), COALESCE(NEW.bbox_y1, 0.0),
                NEW.embedding
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS trg_insert_document_chunk ON document_chunks;
        CREATE TRIGGER trg_insert_document_chunk
        INSTEAD OF INSERT ON document_chunks
        FOR EACH ROW EXECUTE FUNCTION insert_document_chunk();
    """)

    # 4. Create view alias 'documents' pointing to 'papers'
    cursor.execute("DROP VIEW IF EXISTS documents CASCADE;")
    cursor.execute("""
        CREATE OR REPLACE VIEW documents AS
        SELECT id, title, filename, user_id, uploaded_at
        FROM papers;
    """)

    # 5. Create audit_sessions table strictly scoped by user_id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL DEFAULT 'Biomedical Audit Session',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        ALTER TABLE audit_sessions ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
    """)

    # Create view aliases 'chat_sessions' and 'audit_threads' pointing to 'audit_sessions'
    cursor.execute("DROP VIEW IF EXISTS chat_sessions CASCADE;")
    cursor.execute("""
        CREATE OR REPLACE VIEW chat_sessions AS
        SELECT id, user_id, title, created_at
        FROM audit_sessions;
    """)

    cursor.execute("DROP VIEW IF EXISTS audit_threads CASCADE;")
    cursor.execute("""
        CREATE OR REPLACE VIEW audit_threads AS
        SELECT id, user_id, title, created_at
        FROM audit_sessions;
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

    # 6. Seed dedicated administrator account with pre-set email and hashed password
    admin_email = os.getenv("ADMIN_EMAIL", "admin@verinexa.ai").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "Admin@VeriNexa2026!")
    cursor.execute("SELECT id, email, is_admin FROM users WHERE LOWER(email) = LOWER(%s);", (admin_email,))
    existing_admin = cursor.fetchone()

    import bcrypt
    salt = bcrypt.gensalt()
    hashed_admin_pw = bcrypt.hashpw(admin_password.encode("utf-8"), salt).decode("utf-8")

    if not existing_admin:
        cursor.execute(
            """
            INSERT INTO users (email, hashed_password, password_hash, full_name, is_admin)
            VALUES (%s, %s, %s, %s, TRUE);
            """,
            (admin_email, hashed_admin_pw, hashed_admin_pw, "VeriNexa System Administrator")
        )
        print(f"[init_db] Dedicated admin account created: {admin_email}")
    else:
        # Ensure is_admin is TRUE and password matches pre-set admin credentials
        cursor.execute(
            """
            UPDATE users
            SET is_admin = TRUE, hashed_password = %s, password_hash = %s
            WHERE LOWER(email) = LOWER(%s);
            """,
            (hashed_admin_pw, hashed_admin_pw, admin_email)
        )
        print(f"[init_db] Dedicated admin account verified & updated: {admin_email}")

    # 7. Clean up dummy seeded accounts and ensure only genuine active accounts exist
    cursor.execute("""
        UPDATE papers
        SET user_id = (SELECT id FROM users WHERE LOWER(email) = 'gowrish05@gmail.com' LIMIT 1)
        WHERE user_id IN (
            SELECT id FROM users
            WHERE LOWER(email) IN (
                'researcher_test_final@hospital.org',
                'clinical_user_99@hospital.org',
                'test@example.com',
                'test_reject_user@verinexa.ai',
                'researcher_41856e@verinexa.ai'
            )
            OR email ~* '^(test|dummy|clinician_[ab]_[0-9]+|doctor_[ab]_[0-9]+|researcher_[0-9]+|dr_researcher_[0-9]+|user[ab]_[0-9]+)@'
        );

        UPDATE paper_chunks
        SET user_id = (SELECT id FROM users WHERE LOWER(email) = 'gowrish05@gmail.com' LIMIT 1)
        WHERE user_id IN (
            SELECT id FROM users
            WHERE LOWER(email) IN (
                'researcher_test_final@hospital.org',
                'clinical_user_99@hospital.org',
                'test@example.com',
                'test_reject_user@verinexa.ai',
                'researcher_41856e@verinexa.ai'
            )
            OR email ~* '^(test|dummy|clinician_[ab]_[0-9]+|doctor_[ab]_[0-9]+|researcher_[0-9]+|dr_researcher_[0-9]+|user[ab]_[0-9]+)@'
        );

        DELETE FROM users
        WHERE LOWER(email) IN (
            'researcher_test_final@hospital.org',
            'clinical_user_99@hospital.org',
            'test@example.com',
            'test_reject_user@verinexa.ai',
            'researcher_41856e@verinexa.ai'
        )
        OR email ~* '^(test|dummy|clinician_[ab]_[0-9]+|doctor_[ab]_[0-9]+|researcher_[0-9]+|dr_researcher_[0-9]+|user[ab]_[0-9]+)@';
    """)
    print("[init_db] Cleaned up dummy seeded accounts. Genuine accounts and uploaded papers preserved.")

    # 8. Synchronize primary key sequences for all tables to prevent UniqueViolation collisions
    cursor.execute("""
        SELECT setval(pg_get_serial_sequence('paper_chunks', 'id'), COALESCE((SELECT MAX(id) FROM paper_chunks), 1));
        SELECT setval(pg_get_serial_sequence('papers', 'id'), COALESCE((SELECT MAX(id) FROM papers), 1));
        SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE((SELECT MAX(id) FROM users), 1));
        SELECT setval(pg_get_serial_sequence('audit_sessions', 'id'), COALESCE((SELECT MAX(id) FROM audit_sessions), 1));
        SELECT setval(pg_get_serial_sequence('audit_messages', 'id'), COALESCE((SELECT MAX(id) FROM audit_messages), 1));
        SELECT setval(pg_get_serial_sequence('password_reset_tokens', 'id'), COALESCE((SELECT MAX(id) FROM password_reset_tokens), 1));
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("[init_db] Database tables, sequences, dedicated admin, and paper_chunks schema verified successfully.")

if __name__ == "__main__":
    init_database()
