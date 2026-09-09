from typing import TypedDict, Dict, List, Tuple, Optional
from langgraph.graph import StateGraph, START, END
from conflict_engine import retrieve_claims_per_paper, query_ollama, save_verdict_to_db


class ConflictState(TypedDict):
    query: str
    grouped_chunks: Dict[int, List[Tuple[int, str, float]]]
    verdict: str
    saved_id: Optional[int]


def retrieve_node(state: ConflictState) -> dict:
    grouped = retrieve_claims_per_paper(state["query"])
    return {"grouped_chunks": grouped}


def compare_node(state: ConflictState) -> dict:
    grouped_chunks = state["grouped_chunks"]
    query = state["query"]

    if len(grouped_chunks) < 2:
        return {"verdict": "UNCLEAR\nNot enough papers with relevant content to compare."}

    paper_ids = list(grouped_chunks.keys())
    paper_a_id, paper_b_id = paper_ids[0], paper_ids[1]

    paper_a_text = "\n".join([text for _, text, _ in grouped_chunks[paper_a_id]])
    paper_b_text = "\n".join([text for _, text, _ in grouped_chunks[paper_b_id]])

    prompt = f"""You are analyzing two biomedical research paper excerpts to check if they agree or disagree about a specific topic.

Topic: {query}

--- Excerpt from Paper A (id={paper_a_id}) ---
{paper_a_text}

--- Excerpt from Paper B (id={paper_b_id}) ---
{paper_b_text}

Based only on the text above, answer in this exact format:
VERDICT: [AGREE / PARTIAL / CONTRADICT / UNCLEAR]
REASON: [one or two sentences explaining why, citing specific numbers if mentioned]

Use PARTIAL when the papers agree on the overall outcome (e.g., both report weight loss) but disagree on a specific detail such as mechanism, magnitude, or population studied.
"""

    result = query_ollama(prompt)
    return {"verdict": result}


def save_node(state: ConflictState) -> dict:
    saved_id = save_verdict_to_db(state["grouped_chunks"], state["query"], state["verdict"])
    return {"saved_id": saved_id}


def skip_save_node(state: ConflictState) -> dict:
    return {"saved_id": None}


def route_after_compare(state: ConflictState) -> str:
    """
    Only save to the database if the verdict is worth flagging
    (PARTIAL or CONTRADICT) — plain AGREE cases are not persisted.
    """
    verdict_text = state["verdict"]
    if "VERDICT: PARTIAL" in verdict_text or "VERDICT: CONTRADICT" in verdict_text:
        return "save"
    return "skip"


builder = StateGraph(ConflictState)
builder.add_node("retrieve", retrieve_node)
builder.add_node("compare", compare_node)
builder.add_node("save", save_node)
builder.add_node("skip", skip_save_node)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "compare")
builder.add_conditional_edges("compare", route_after_compare, {"save": "save", "skip": "skip"})
builder.add_edge("save", END)
builder.add_edge("skip", END)

graph = builder.compile()


if __name__ == "__main__":
    query = "effect of SGLT2 inhibitor on body weight"
    print(f"Query: {query}\n")

    result = graph.invoke({"query": query})

    print("=== LangGraph Conflict Engine Verdict ===")
    print(result["verdict"])
    print(f"\nSaved to DB: {'Yes, id=' + str(result['saved_id']) if result['saved_id'] else 'No (plain AGREE, not flagged)'}")