import os
import shutil
import json
import requests
from typing import Optional, List
from dotenv import load_dotenv
import psycopg2
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import check_connection
from init_db import init_database
from auth import router as auth_router, get_current_user, get_optional_user
from conflict_graph import graph as conflict_graph
from integrity_graph import graph as integrity_graph
from ingest import ingest_pdf
from hybrid_search import hybrid_search
from chat_engine import query_ollama, chat_with_papers

load_dotenv()

# Initialize database tables on startup
try:
    init_database()
except Exception as e:
    print(f"[Warning] DB initialization error: {e}")

app = FastAPI(
    title="VeriNexa Biomedical Audit API",
    description="Cross-Document Contradiction Detection and Integrity Verification System for Clinical Literature",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/files", StaticFiles(directory="uploaded_pdfs"), name="files")

# Mount authentication router
app.include_router(auth_router)


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


# ---------------- Health & Diagnostics ----------------
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}


@app.get("/db-check")
def db_check():
    version = check_connection()
    return {"status": "ok", "postgres_version": version}


# ---------------- Literature Endpoints ----------------
@app.get("/papers")
def list_papers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, filename, uploaded_at, user_id FROM papers ORDER BY id;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    papers = [
        {"id": r[0], "title": r[1], "filename": r[2], "uploaded_at": str(r[3]), "user_id": r[4]}
        for r in rows
    ]
    return {"papers": papers}


# ---------------- Upload with Auth & Gate ----------------
@app.post("/upload")
def upload_paper(
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    save_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ingestion_result = ingest_pdf(save_path, title, user_id=current_user["id"])

    if ingestion_result.get("rejected"):
        if os.path.exists(save_path):
            os.remove(save_path)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "status": "rejected",
                "message": "This document does not appear to be a biomedical research paper. VeriNexa only accepts biomedical or medical research papers, such as clinical studies, systematic reviews, or meta-analyses.",
                "details": ingestion_result.get("reason", "Non-biomedical content detected")
            }
        )

    return {
        "status": "ok",
        "paper_id": ingestion_result["paper_id"],
        "filename": file.filename,
        "title": title,
        "user_id": current_user["id"]
    }


# ---------------- Audit & Analysis Endpoints ----------------
@app.get("/compare")
def compare_papers(query: str, current_user: Optional[dict] = Depends(get_optional_user)):
    result = conflict_graph.invoke({"query": query})
    return {
        "query": query,
        "verdict": result["verdict"],
        "saved_id": result.get("saved_id"),
        "user_id": current_user["id"] if current_user else None
    }


@app.get("/integrity-check")
def check_paper_integrity(
    paper_id: int,
    topic_query: str,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    result = integrity_graph.invoke({"paper_id": paper_id, "topic_query": topic_query})
    return {
        "paper_id": paper_id,
        "topic_query": topic_query,
        "verdict": result["verdict"],
        "saved_id": result.get("saved_id"),
        "user_id": current_user["id"] if current_user else None
    }


# ---------------- Persistent Audit History & Chat ----------------
class ChatPayload(BaseModel):
    question: str
    session_id: Optional[int] = None
    paper_id: Optional[int] = None


@app.get("/api/history")
def get_audit_history(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.id, s.title, s.created_at, COUNT(m.id) as message_count
        FROM audit_sessions s
        LEFT JOIN audit_messages m ON s.id = m.session_id
        WHERE s.user_id = %s
        GROUP BY s.id, s.title, s.created_at
        ORDER BY s.created_at DESC;
        """,
        (current_user["id"],)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    sessions = [
        {
            "id": r[0],
            "title": r[1],
            "created_at": str(r[2]),
            "message_count": r[3]
        }
        for r in rows
    ]
    return {"sessions": sessions}


@app.get("/api/history/{session_id}")
def get_session_messages(session_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    # Verify session ownership
    cursor.execute(
        "SELECT id, title, created_at FROM audit_sessions WHERE id = %s AND user_id = %s;",
        (session_id, current_user["id"])
    )
    session_row = cursor.fetchone()
    if not session_row:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Audit session not found")

    cursor.execute(
        """
        SELECT id, role, content, citations_json, timestamp
        FROM audit_messages
        WHERE session_id = %s
        ORDER BY timestamp ASC, id ASC;
        """,
        (session_id,)
    )
    msg_rows = cursor.fetchall()
    cursor.close()
    conn.close()

    messages = []
    for r in msg_rows:
        citations = r[3]
        if isinstance(citations, str):
            try:
                citations = json.loads(citations)
            except Exception:
                citations = []
        messages.append({
            "id": r[0],
            "role": r[1],
            "content": r[2],
            "citations": citations or [],
            "timestamp": str(r[4])
        })

    return {
        "session_id": session_row[0],
        "title": session_row[1],
        "created_at": str(session_row[2]),
        "messages": messages
    }


@app.post("/api/chat")
def chat_audit(payload: ChatPayload, current_user: dict = Depends(get_current_user)):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    session_id = payload.session_id
    conn = get_connection()
    cursor = conn.cursor()

    # Verify or create session
    if session_id:
        cursor.execute(
            "SELECT id, title FROM audit_sessions WHERE id = %s AND user_id = %s;",
            (session_id, current_user["id"])
        )
        existing = cursor.fetchone()
        if not existing:
            session_id = None

    if not session_id:
        session_title = question[:50] + ("..." if len(question) > 50 else "")
        cursor.execute(
            "INSERT INTO audit_sessions (user_id, title) VALUES (%s, %s) RETURNING id;",
            (current_user["id"], session_title)
        )
        session_id = cursor.fetchone()[0]

    # Save user message
    cursor.execute(
        "INSERT INTO audit_messages (session_id, role, content, citations_json) VALUES (%s, 'user', %s, '[]') RETURNING id;",
        (session_id, question)
    )
    user_msg_id = cursor.fetchone()[0]
    conn.commit()

    # Execute hybrid search with top_k=3 to reduce token context overhead
    raw_results = hybrid_search(question, top_k=3, paper_id=payload.paper_id)

    # Fetch citation metadata
    citations = []
    for cid, c_index, c_text, score in raw_results:
        cursor.execute(
            """
            SELECT c.id, c.paper_id, c.chunk_index, c.chunk_text, p.title, p.filename
            FROM chunks c
            JOIN papers p ON c.paper_id = p.id
            WHERE c.id = %s;
            """,
            (cid,)
        )
        p_row = cursor.fetchone()
        if p_row:
            citations.append({
                "chunk_id": p_row[0],
                "paper_id": p_row[1],
                "chunk_index": p_row[2],
                "snippet": p_row[3][:280] + ("..." if len(p_row[3]) > 280 else ""),
                "full_text": p_row[3],
                "title": p_row[4],
                "filename": p_row[5],
                "score": round(float(score), 4)
            })

    # Prepare context for Ollama
    context_blocks = []
    for i, c in enumerate(citations):
        context_blocks.append(f"[Excerpt {i+1} | Source: {c['title']} | File: {c['filename']}]:\n{c['full_text']}")
    context_str = "\n\n".join(context_blocks)

    prompt = f"""You are a biomedical research assistant answering questions about a set of uploaded biomedical papers.

Use ONLY the excerpts below to answer the question. If the excerpts don't contain enough information to answer, say so honestly rather than guessing.

--- Excerpts from uploaded papers ---
{context_str}

--- Question ---
{question}

Answer clearly and concisely, referencing specific findings, numbers, or papers where relevant.
"""

    answer = query_ollama(prompt)

    # Save assistant message with citations
    cursor.execute(
        """
        INSERT INTO audit_messages (session_id, role, content, citations_json)
        VALUES (%s, 'assistant', %s, %s)
        RETURNING id;
        """,
        (session_id, answer, json.dumps(citations))
    )
    asst_msg_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "session_id": session_id,
        "question": question,
        "answer": answer,
        "sources_used": len(citations),
        "citations": citations
    }


@app.post("/api/chat/stream")
def chat_audit_stream(payload: ChatPayload, current_user: dict = Depends(get_current_user)):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    session_id = payload.session_id
    conn = get_connection()
    cursor = conn.cursor()

    if session_id:
        cursor.execute(
            "SELECT id, title FROM audit_sessions WHERE id = %s AND user_id = %s;",
            (session_id, current_user["id"])
        )
        existing = cursor.fetchone()
        if not existing:
            session_id = None

    if not session_id:
        session_title = question[:50] + ("..." if len(question) > 50 else "")
        cursor.execute(
            "INSERT INTO audit_sessions (user_id, title) VALUES (%s, %s) RETURNING id;",
            (current_user["id"], session_title)
        )
        session_id = cursor.fetchone()[0]

    # Save user message
    cursor.execute(
        "INSERT INTO audit_messages (session_id, role, content, citations_json) VALUES (%s, 'user', %s, '[]') RETURNING id;",
        (session_id, question)
    )
    conn.commit()

    # Reduced top_k = 3 context overhead
    raw_results = hybrid_search(question, top_k=3, paper_id=payload.paper_id)

    citations = []
    for cid, c_index, c_text, score in raw_results:
        cursor.execute(
            """
            SELECT c.id, c.paper_id, c.chunk_index, c.chunk_text, p.title, p.filename
            FROM chunks c
            JOIN papers p ON c.paper_id = p.id
            WHERE c.id = %s;
            """,
            (cid,)
        )
        p_row = cursor.fetchone()
        if p_row:
            citations.append({
                "chunk_id": p_row[0],
                "paper_id": p_row[1],
                "chunk_index": p_row[2],
                "snippet": p_row[3][:280] + ("..." if len(p_row[3]) > 280 else ""),
                "full_text": p_row[3],
                "title": p_row[4],
                "filename": p_row[5],
                "score": round(float(score), 4)
            })

    cursor.close()
    conn.close()

    context_blocks = [
        f"[Excerpt {i+1} | Source: {c['title']} | File: {c['filename']}]:\n{c['full_text']}"
        for i, c in enumerate(citations)
    ]
    context_str = "\n\n".join(context_blocks)

    prompt = f"""You are a biomedical research assistant answering questions about a set of uploaded biomedical papers.

Use ONLY the excerpts below to answer the question. If the excerpts don't contain enough information to answer, say so honestly rather than guessing.

--- Excerpts from uploaded papers ---
{context_str}

--- Question ---
{question}

Answer clearly and concisely, referencing specific findings, numbers, or papers where relevant.
"""

    def generate_tokens():
        try:
            res = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.1:8b",
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 300
                    }
                },
                stream=True
            )

            full_answer = ""
            for line in res.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    token = chunk.get("response", "")
                    full_answer += token
                    event_data = json.dumps({"token": token, "done": False})
                    yield f"data: {event_data}\n\n"

            # Save assistant message upon completion
            db_conn = get_connection()
            db_cursor = db_conn.cursor()
            db_cursor.execute(
                """
                INSERT INTO audit_messages (session_id, role, content, citations_json)
                VALUES (%s, 'assistant', %s, %s);
                """,
                (session_id, full_answer, json.dumps(citations))
            )
            db_conn.commit()
            db_cursor.close()
            db_conn.close()

            done_event = json.dumps({
                "token": "",
                "done": True,
                "session_id": session_id,
                "citations": citations,
                "sources_used": len(citations)
            })
            yield f"data: {done_event}\n\n"
        except Exception as e:
            err_event = json.dumps({"error": str(e), "done": True})
            yield f"data: {err_event}\n\n"

    return StreamingResponse(generate_tokens(), media_type="text/event-stream")


# Backwards-compatible GET /chat endpoint
@app.get("/chat")
def chat(question: str, paper_id: Optional[int] = Query(None)):
    result = chat_with_papers(question, paper_id=paper_id)
    return {
        "question": question,
        "answer": result["answer"],
        "sources_used": result["sources_used"]
    }