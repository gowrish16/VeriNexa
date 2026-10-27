from typing import TypedDict, Dict, List, Tuple, Optional
from langgraph.graph import StateGraph, START, END
from conflict_engine import retrieve_claims_per_paper, query_ollama, save_verdict_to_db, compare_claims
from config import DEFAULT_MODEL


class ConflictState(TypedDict):
    query: str
    user_id: Optional[int]
    paper_ids: Optional[List[int]]
    grouped_chunks: Dict[int, List[Tuple[int, str, float]]]
    paper_meta: Optional[Dict[int, dict]]
    verdict: str
    saved_id: Optional[int]


def retrieve_node(state: ConflictState) -> dict:
    grouped, paper_meta = retrieve_claims_per_paper(
        query=state["query"],
        user_id=state.get("user_id"),
        paper_ids=state.get("paper_ids")
    )
    return {"grouped_chunks": grouped, "paper_meta": paper_meta}


def compare_node(state: ConflictState) -> dict:
    grouped_chunks = state.get("grouped_chunks", {})
    paper_meta = state.get("paper_meta", {})
    query = state.get("query", "")

    if len(grouped_chunks) < 2:
        return {"verdict": "VERDICT: UNCLEAR - Not enough papers with relevant content to compare. At least 2 indexed papers are required."}

    result = compare_claims(query, grouped_chunks, paper_meta)
    return {"verdict": result}


def adversarial_critic_node(state: ConflictState) -> dict:
    verdict_text = state.get("verdict", "")
    if "CONFLICT" not in verdict_text.upper() and "CONTRADICT" not in verdict_text.upper():
        return {}

    grouped_chunks = state.get("grouped_chunks", {})
    query = state.get("query", "")
    paper_ids = list(grouped_chunks.keys())
    if len(paper_ids) < 2:
        return {}

    paper_a_id, paper_b_id = paper_ids[0], paper_ids[1]
    def _extract_chunk_text(c):
        if isinstance(c, str):
            return c
        for elem in c:
            if isinstance(elem, str):
                return elem
        return str(c)

    paper_a_text = "\n".join([_extract_chunk_text(item) for item in grouped_chunks[paper_a_id]])
    paper_b_text = "\n".join([_extract_chunk_text(item) for item in grouped_chunks[paper_b_id]])

    prompt = f"""You are a senior clinical trials adversarial critic evaluating potential false positive contradiction alarms.
The primary auditor flagged a CONFLICT between two biomedical papers on the topic: {query}.

Primary Auditor Assessment:
{verdict_text}

--- Paper A Excerpt (id={paper_a_id}) ---
{paper_a_text}

--- Paper B Excerpt (id={paper_b_id}) ---
{paper_b_text}

Evaluate whether this apparent conflict is a GENUINE conflict on primary endpoints, or if it is EXPLAINABLE by confounding trial design factors such as:
1. Dosage or regimen differences
2. Patient cohort demographics (e.g., Type 1 vs Type 2 diabetes, baseline HbA1c, baseline renal function)
3. Trial duration or background co-medications (e.g., insulin combination vs monotherapy)

Respond in this exact format:
EXPLAINABLE: [YES or NO]
REASONING: [Brief 1-2 sentence explanation of confounding factors if YES, or confirmation of direct conflict if NO]
FINAL VERDICT: [PARTIALLY CONSISTENT or CONFLICT]
"""

    try:
        critic_response = query_ollama(prompt, model=DEFAULT_MODEL, timeout=60.0, num_predict=150)
        if "EXPLAINABLE: YES" in critic_response.upper() or "PARTIALLY CONSISTENT" in critic_response.upper():
            import re
            clean_bullets = re.sub(r"\n*VERDICT:.*", "", verdict_text, flags=re.DOTALL).strip()
            new_verdict = f"{clean_bullets}\n\nVERDICT: PARTIALLY CONSISTENT - Apparent conflict is explainable by confounding trial design factors."
            return {"verdict": new_verdict}
    except Exception as e:
        print(f"[Warning] Adversarial critic pass failed: {e}")

    return {}


def save_node(state: ConflictState) -> dict:
    saved_id = save_verdict_to_db(
        state["grouped_chunks"],
        state["query"],
        state["verdict"],
        user_id=state.get("user_id")
    )
    return {"saved_id": saved_id}


def skip_save_node(state: ConflictState) -> dict:
    return {"saved_id": None}


def route_after_compare(state: ConflictState) -> str:
    verdict_text = state.get("verdict", "").upper()
    if "CONFLICT" in verdict_text or "CONTRADICT" in verdict_text:
        return "adversarial_critic"
    elif "PARTIAL" in verdict_text or "CONSISTENT" in verdict_text:
        return "save"
    return "skip"


def route_after_critic(state: ConflictState) -> str:
    verdict_text = state.get("verdict", "").upper()
    if (
        "PARTIAL" in verdict_text
        or "CONFLICT" in verdict_text
        or "CONTRADICT" in verdict_text
        or "PARTIALLY CONSISTENT" in verdict_text
        or "CONSISTENT" in verdict_text
    ):
        return "save"
    return "skip"


builder = StateGraph(ConflictState)
builder.add_node("retrieve", retrieve_node)
builder.add_node("compare", compare_node)
builder.add_node("adversarial_critic", adversarial_critic_node)
builder.add_node("save", save_node)
builder.add_node("skip", skip_save_node)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "compare")
builder.add_conditional_edges(
    "compare",
    route_after_compare,
    {
        "adversarial_critic": "adversarial_critic",
        "save": "save",
        "skip": "skip"
    }
)
builder.add_conditional_edges(
    "adversarial_critic",
    route_after_critic,
    {
        "save": "save",
        "skip": "skip"
    }
)
builder.add_edge("save", END)
builder.add_edge("skip", END)

graph = builder.compile()
audit_graph = graph


if __name__ == "__main__":
    query = "effect of SGLT2 inhibitor on body weight"
    print(f"Query: {query}\n")

    result = graph.invoke({"query": query})

    print("=== LangGraph Conflict Engine Verdict ===")
    print(result["verdict"])
    print(f"\nSaved to DB: {'Yes, id=' + str(result['saved_id']) if result['saved_id'] else 'No (plain AGREE, not flagged)'}")