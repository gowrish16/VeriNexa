from typing import TypedDict, Dict, List, Optional, Any
from langgraph.graph import StateGraph, START, END
import asyncio
import httpx
import requests
import json
import os
import psycopg2
from dotenv import load_dotenv
from hybrid_search import hybrid_search, async_hybrid_search
from config import DEFAULT_MODEL, KEEP_ALIVE, NUM_THREAD, NUM_GPU, DEFAULT_TEMPERATURE, OLLAMA_BASE_URL

load_dotenv()


class ChatState(TypedDict):
    question: str
    session_id: Optional[int]
    paper_id: Optional[int]
    user_id: int
    raw_results: List[tuple]
    citations: List[Dict[str, Any]]
    context_str: str
    prompt: str
    answer: str
    saved_id: Optional[int]


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def retrieve_node(state: ChatState) -> dict:
    """Retrieves relevant chunks using hybrid search"""
    question = state["question"]
    paper_id = state["paper_id"]
    user_id = state["user_id"]

    # Execute hybrid search with top_k=3
    raw_results = hybrid_search(question, top_k=3, paper_id=paper_id, user_id=user_id)

    # Fetch citation metadata including page_number and bounding boxes
    conn = get_connection()
    cursor = conn.cursor()

    citations = []
    for item in raw_results:
        cid = item[0]
        c_index = item[1]
        c_text = item[2]
        score = item[3]
        page_num = item[4] if len(item) > 4 else 1
        x0 = item[5] if len(item) > 5 else 0.0
        y0 = item[6] if len(item) > 6 else 0.0
        x1 = item[7] if len(item) > 7 else 0.0
        y1 = item[8] if len(item) > 8 else 0.0

        cursor.execute(
            """
            SELECT c.id, c.paper_id, c.chunk_index, c.chunk_text, p.title, p.filename, c.page_number, c.bbox_x0, c.bbox_y0, c.bbox_x1, c.bbox_y1
            FROM paper_chunks c
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
                "page_number": p_row[6] or page_num,
                "page_width": 612.0,
                "page_height": 792.0,
                "bbox_x0": float(p_row[7] if p_row[7] is not None else x0),
                "bbox_y0": float(p_row[8] if p_row[8] is not None else y0),
                "bbox_x1": float(p_row[9] if p_row[9] is not None else x1),
                "bbox_y1": float(p_row[10] if p_row[10] is not None else y1),
                "score": round(float(score), 4)
            })

    cursor.close()
    conn.close()

    # Prepare context for Ollama
    context_blocks = []
    for i, c in enumerate(citations):
        context_blocks.append(f"[Excerpt {i+1} | Source: {c['title']} | File: {c['filename']}]:\n{c['full_text']}")
    context_str = "\n\n".join(context_blocks)

    return {
        "raw_results": raw_results,
        "citations": citations,
        "context_str": context_str
    }


def generate_prompt_node(state: ChatState) -> dict:
    """Generates the prompt for Ollama"""
    question = state["question"]
    context_str = state["context_str"]

    prompt = f"""You are a biomedical research assistant answering questions about a set of uploaded biomedical papers.

Use ONLY the excerpts below to answer the question. If the excerpts don't contain enough information to answer, say so honestly rather than guessing.

--- Excerpts from uploaded papers ---
{context_str}

--- Question ---
{question}

Answer clearly and concisely, referencing specific findings, numbers, or papers where relevant.
"""

    return {"prompt": prompt}


def query_ollama_stream(prompt, model=DEFAULT_MODEL):
    """Generator that yields tokens from Ollama"""
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": True,
            "keep_alive": KEEP_ALIVE,
            "options": {
                "temperature": DEFAULT_TEMPERATURE,
                "num_predict": 250,
                "num_thread": NUM_THREAD,
                "num_gpu": NUM_GPU,
                "num_ctx": 2048
            }
        },
        stream=True
    )

    for line in response.iter_lines():
        if line:
            chunk = json.loads(line.decode("utf-8"))
            token = chunk.get("response", "")
            if token:
                yield token


async def async_query_ollama_stream(prompt, model=DEFAULT_MODEL):
    """Async generator that yields tokens from Ollama using non-blocking httpx"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": True,
                "keep_alive": KEEP_ALIVE,
                "options": {
                    "temperature": DEFAULT_TEMPERATURE,
                    "num_predict": 250,
                    "num_thread": NUM_THREAD,
                    "num_gpu": NUM_GPU,
                    "num_ctx": 2048,
                }
            }
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    if token:
                        yield token


async def async_retrieve_node(state: ChatState) -> dict:
    """Non-blocking async wrapper for retrieve_node"""
    return await asyncio.to_thread(retrieve_node, state)


def generate_answer_node(state: ChatState) -> dict:
    """Generates answer using Ollama (non-streaming version for sync execution)"""
    prompt = state["prompt"]

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": DEFAULT_MODEL,
            "prompt": prompt,
            "stream": False,
            "keep_alive": KEEP_ALIVE,
            "options": {
                "temperature": DEFAULT_TEMPERATURE,
                "num_predict": 250,
                "num_thread": NUM_THREAD,
                "num_gpu": NUM_GPU,
                "num_ctx": 2048
            }
        }
    )

    answer = response.json()["response"]
    return {"answer": answer}


def save_node(state: ChatState) -> dict:
    """Saves the assistant message to database"""
    session_id = state["session_id"]
    answer = state["answer"]
    citations = state["citations"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO audit_messages (session_id, role, content, citations_json)
        VALUES (%s, 'assistant', %s, %s)
        RETURNING id;
        """,
        (session_id, answer, json.dumps(citations))
    )
    saved_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return {"saved_id": saved_id}


def skip_save_node(state: ChatState) -> dict:
    return {"saved_id": None}


# Build the graph
builder = StateGraph(ChatState)
builder.add_node("retrieve_chunks", retrieve_node)
builder.add_node("generate_prompt", generate_prompt_node)
builder.add_node("generate_answer", generate_answer_node)
builder.add_node("save", save_node)
builder.add_node("skip", skip_save_node)

builder.add_edge(START, "retrieve_chunks")
builder.add_edge("retrieve_chunks", "generate_prompt")
builder.add_edge("generate_prompt", "generate_answer")
builder.add_edge("generate_answer", "save")
builder.add_edge("save", END)
builder.add_edge("skip", END)

graph = builder.compile()


if __name__ == "__main__":
    # Test the graph
    result = graph.invoke({
        "question": "What are the main side effects of SGLT2 inhibitors?",
        "session_id": 1,
        "paper_id": None,
        "user_id": 1,
        "raw_results": [],
        "citations": [],
        "context_str": "",
        "prompt": "",
        "answer": "",
        "saved_id": None
    })

    print("=== Chat Graph Result ===")
    print(f"Answer: {result['answer']}")
    print(f"Citations: {len(result['citations'])}")
    print(f"Saved ID: {result['saved_id']}")
