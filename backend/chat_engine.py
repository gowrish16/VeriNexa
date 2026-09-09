import requests
from hybrid_search import hybrid_search


def query_ollama(prompt, model="llama3.1:8b"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2}
        }
    )
    return response.json()["response"]


def chat_with_papers(question, top_k=6):
    results = hybrid_search(question, top_k=top_k)
    context = "\n\n".join(
        [f"[Excerpt {i+1}]: {text}" for i, (_, _, text, _) in enumerate(results)]
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


if __name__ == "__main__":
    question = "What are the main side effects of SGLT2 inhibitors mentioned in these papers?"
    result = chat_with_papers(question)
    print("Answer:", result["answer"])
    print("Sources used:", result["sources_used"])