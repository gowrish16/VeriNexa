from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from integrity_check import get_abstract_text, search_within_paper, query_ollama, save_integrity_result


class IntegrityState(TypedDict):
    paper_id: int
    topic_query: str
    abstract_text: str
    supporting_text: str
    verdict: str
    saved_id: Optional[int]


def fetch_node(state: IntegrityState) -> dict:
    abstract_text = get_abstract_text(state["paper_id"])
    supporting_chunks = search_within_paper(state["paper_id"], state["topic_query"])
    supporting_text = "\n".join([text for _, text in supporting_chunks])
    return {"abstract_text": abstract_text, "supporting_text": supporting_text}


def check_node(state: IntegrityState) -> dict:
    prompt = f"""You are checking whether a research paper's abstract accurately reflects its own detailed results.

Important: In medical research, a "reduction" or "decrease" in a value (like body weight, HbA1c, or blood glucose) is often the DESIRED, POSITIVE outcome of a treatment, not a negative one. Do not treat a reported reduction as contradicting a claim of "improvement" unless the abstract explicitly claims an increase.

--- Abstract ---
{state["abstract_text"]}

--- Detailed results text from the same paper (on the topic: {state["topic_query"]}) ---
{state["supporting_text"]}

Based only on the text above, answer in this exact format:
VERDICT: [CONSISTENT / INCONSISTENT / UNCLEAR]
REASON: [one or two sentences explaining why, citing specific numbers if mentioned]

Use INCONSISTENT only if the abstract makes a claim that is clearly not supported by, or actually contradicts, the detailed results shown — not merely because the wording differs.
"""
    result = query_ollama(prompt)
    return {"verdict": result}


def save_node(state: IntegrityState) -> dict:
    saved_id = save_integrity_result(state["paper_id"], state["topic_query"], state["verdict"])
    return {"saved_id": saved_id}


def skip_save_node(state: IntegrityState) -> dict:
    return {"saved_id": None}


def route_after_check(state: IntegrityState) -> str:
    """
    Only persist flagged (INCONSISTENT) results, same policy as Layer 2 -
    consistent findings aren't worth cluttering the database with.
    """
    if "VERDICT: INCONSISTENT" in state["verdict"]:
        return "save"
    return "skip"


builder = StateGraph(IntegrityState)
builder.add_node("fetch", fetch_node)
builder.add_node("check", check_node)
builder.add_node("save", save_node)
builder.add_node("skip", skip_save_node)

builder.add_edge(START, "fetch")
builder.add_edge("fetch", "check")
builder.add_conditional_edges("check", route_after_check, {"save": "save", "skip": "skip"})
builder.add_edge("save", END)
builder.add_edge("skip", END)

graph = builder.compile()


if __name__ == "__main__":
    paper_id = 1
    topic_query = "SGLT2 inhibitor effect on body weight"

    print(f"Checking integrity for paper_id={paper_id} on topic: {topic_query}\n")
    result = graph.invoke({"paper_id": paper_id, "topic_query": topic_query})

    print("=== Integrity Check Verdict ===")
    print(result["verdict"])
    print(f"\nSaved to DB: {'Yes, id=' + str(result['saved_id']) if result['saved_id'] else 'No (consistent, not flagged)'}")