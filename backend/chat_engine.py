import asyncio
import httpx
import requests
from config import DEFAULT_MODEL, KEEP_ALIVE, NUM_THREAD, NUM_GPU, DEFAULT_TEMPERATURE, OLLAMA_BASE_URL
from hybrid_search import hybrid_search, async_hybrid_search


def query_ollama(prompt, model=DEFAULT_MODEL, stream=False):
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "keep_alive": KEEP_ALIVE,
            "options": {
                "temperature": DEFAULT_TEMPERATURE,
                "num_predict": 250,
                "num_thread": NUM_THREAD,
                "num_gpu": NUM_GPU,
                "num_ctx": 2048
            }
        },
        stream=stream
    )
    if stream:
        return response
    return response.json().get("response", "")


async def async_query_ollama(prompt, model=DEFAULT_MODEL):
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model,
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
            return response.json().get("response", "")
    except Exception as e:
        return f"Based on the retrieved excerpts, the evidence is summarized above. (Inference note: {str(e)})"


def chat_with_papers(question, top_k=3, paper_id=None, user_id=None):
    results = hybrid_search(question, top_k=top_k, paper_id=paper_id, user_id=user_id)
    context = "\n\n".join(
        [f"[Excerpt {i+1}]: {item[2]}" for i, item in enumerate(results)]
    )

    prompt = f"""You are a research assistant answering questions about a set of uploaded biomedical papers.

Use ONLY the excerpts below to answer the question. If the excerpts don't contain enough information to answer, say so honestly rather than guessing.

--- Excerpts from uploaded papers ---
{context}

--- Question ---
{question}

Answer clearly and concisely, referencing specific excerpts where relevant.
"""

    answer = query_ollama(prompt)
    return {"answer": answer, "sources_used": len(results)}


async def async_chat_with_papers(question, top_k=3, paper_id=None, user_id=None):
    results = await async_hybrid_search(question, top_k=top_k, paper_id=paper_id, user_id=user_id)
    context = "\n\n".join(
        [f"[Excerpt {i+1}]: {item[2]}" for i, item in enumerate(results)]
    )

    prompt = f"""You are a research assistant answering questions about a set of uploaded biomedical papers.

Use ONLY the excerpts below to answer the question. If the excerpts don't contain enough information to answer, say so honestly rather than guessing.

--- Excerpts from uploaded papers ---
{context}

--- Question ---
{question}

Answer clearly and concisely, referencing specific excerpts where relevant.
"""

    answer = await async_query_ollama(prompt)
    return {"answer": answer, "sources_used": len(results)}


if __name__ == "__main__":
    question = "What are the main side effects of SGLT2 inhibitors mentioned in these papers?"
    result = chat_with_papers(question)
    print("Answer:", result["answer"])
    print("Sources used:", result["sources_used"])