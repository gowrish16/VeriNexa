from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from integrity_check import (
    get_paper_metadata,
    get_abstract_text,
    search_within_paper,
    query_ollama,
    save_integrity_result,
)


class IntegrityState(TypedDict):
    paper_id: int
    topic_query: str
    paper_title: Optional[str]
    filename: Optional[str]
    abstract_text: str
    supporting_text: str
    verdict: str
    saved_id: Optional[int]


def fetch_node(state: IntegrityState) -> dict:
    paper_id = state["paper_id"]
    topic_query = (state.get("topic_query") or "").strip()

    paper = get_paper_metadata(paper_id)
    if not paper:
        return {
            "paper_title": None,
            "filename": None,
            "abstract_text": "",
            "supporting_text": "",
            "verdict": f"VERDICT: UNCLEAR\nREASON: Paper ID #{paper_id} does not exist in the database.",
        }

    abstract_text = get_abstract_text(paper_id, max_chunks=2)
    if not abstract_text:
        return {
            "paper_title": paper["title"],
            "filename": paper["filename"],
            "abstract_text": "",
            "supporting_text": "",
            "verdict": f"VERDICT: UNCLEAR\nREASON: No text chunks found for paper #{paper_id} ({paper['title']}).",
        }

    supporting_chunks = search_within_paper(paper_id, topic_query, top_k=3, abstract_chunk_count=2)
    if not supporting_chunks:
        return {
            "paper_title": paper["title"],
            "filename": paper["filename"],
            "abstract_text": abstract_text,
            "supporting_text": "",
            "verdict": f"VERDICT: UNCLEAR\nREASON: Insufficient body chunks indexed for paper #{paper_id} ({paper['title']}).",
        }

    supporting_text = "\n\n".join([f"[Body Chunk #{idx}]: {text}" for idx, text in supporting_chunks])

    return {
        "paper_title": paper["title"],
        "filename": paper["filename"],
        "abstract_text": abstract_text,
        "supporting_text": supporting_text,
        "verdict": "",
    }


def check_node(state: IntegrityState) -> dict:
    # If fetch_node already produced an error verdict (e.g. paper not found)
    if state.get("verdict"):
        return {"verdict": state["verdict"]}

    paper_id = state["paper_id"]
    paper_title = state.get("paper_title") or f"Paper #{paper_id}"
    filename = state.get("filename") or "Document"
    topic_label = state.get("topic_query", "").strip() or "Overall Clinical Outcomes"

    prompt = f"""You are checking whether a biomedical research paper's abstract accurately reflects its own detailed raw results and body text.

Paper Title: {paper_title} (File: {filename}, ID: #{paper_id})
Audit Focus: {topic_label}

Important: In medical research, a "reduction" or "decrease" in a value (like body weight, HbA1c, or blood glucose) is often the DESIRED, POSITIVE outcome of a treatment, not a negative one. Do not treat a reported reduction as contradicting a claim of "improvement" unless the abstract explicitly claims an increase.

--- Abstract Excerpt ---
{state["abstract_text"]}

--- Detailed Body & Results Excerpts from Paper #{paper_id} ---
{state["supporting_text"]}

Based ONLY on the text above, answer in this exact format:
VERDICT: [CONSISTENT / INCONSISTENT / UNCLEAR]
REASON: [one or two sentences explaining why, citing specific numbers or endpoints if mentioned]

Use INCONSISTENT only if the abstract makes a claim that is clearly not supported by, or actually contradicts, the detailed results shown — not merely because the wording differs.
"""
    result = query_ollama(prompt)
    return {"verdict": result}


def save_node(state: IntegrityState) -> dict:
    saved_id = save_integrity_result(
        state["paper_id"],
        state.get("topic_query", ""),
        state["verdict"]
    )
    return {"saved_id": saved_id}


def skip_save_node(state: IntegrityState) -> dict:
    return {"saved_id": None}


def route_after_check(state: IntegrityState) -> str:
    """
    Only persist flagged (INCONSISTENT) results, same policy as Layer 2 -
    consistent findings aren't worth cluttering the database with.
    """
    if "VERDICT: INCONSISTENT" in state.get("verdict", ""):
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
    test_paper_id = 32
    test_topic = "SGLT2 inhibitors as metabolic modulators"

    print(f"Checking integrity for paper_id={test_paper_id} on topic: {test_topic}\n")
    result = graph.invoke({"paper_id": test_paper_id, "topic_query": test_topic})

    print("=== Integrity Check Verdict ===")
    print(result["verdict"])
    print(f"\nSaved to DB: {'Yes, id=' + str(result['saved_id']) if result['saved_id'] else 'No (consistent, not flagged)'}")