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


def adversarial_critic_node(state: ConflictState) -> dict:
    verdict_text = state.get("verdict", "")
    if "CONTRADICT" not in verdict_text.upper():
        return {}

    grouped_chunks = state.get("grouped_chunks", {})
    query = state.get("query", "")
    paper_ids = list(grouped_chunks.keys())
    if len(paper_ids) < 2:
        return {}

    paper_a_id, paper_b_id = paper_ids[0], paper_ids[1]
    paper_a_text = "\n".join([text for _, text, _ in grouped_chunks[paper_a_id]])
    paper_b_text = "\n".join([text for _, text, _ in grouped_chunks[paper_b_id]])

    prompt = f"""You are a senior clinical trials adversarial critic evaluating potential false positive contradiction alarms.
The primary auditor flagged a CONTRADICTION between two biomedical papers on the topic: {query}.

Primary Auditor Verdict:
{verdict_text}

--- Paper A Excerpt (id={paper_a_id}) ---
{paper_a_text}

--- Paper B Excerpt (id={paper_b_id}) ---
{paper_b_text}

Evaluate whether this apparent contradiction is a GENUINE conflict on primary endpoints, or if it is EXPLAINABLE by confounding trial design factors such as:
1. Dosage or regimen differences
2. Patient cohort demographics (e.g., Type 1 vs Type 2 diabetes, baseline HbA1c, baseline renal function)
3. Trial duration or background co-medications (e.g., insulin combination vs monotherapy)

Respond in this exact format:
EXPLAINABLE: [YES or NO]
REASONING: [Brief 1-2 sentence explanation of confounding factors if YES, or confirmation of direct contradiction if NO]
FINAL VERDICT: [PARTIALLY CONSISTENT or CONTRADICT]
"""

    try:
        critic_response = query_ollama(prompt, model="llama3.1:8b")
        if "EXPLAINABLE: YES" in critic_response.upper() or "PARTIALLY CONSISTENT" in critic_response.upper():
            new_verdict = f"VERDICT: PARTIALLY CONSISTENT\nREASON: [Adversarial Review] Apparent contradiction is explainable by confounding trial design factors.\n{critic_response.strip()}"
            return {"verdict": new_verdict}
    except Exception as e:
        print(f"[Warning] Adversarial critic pass failed: {e}")

    return {}


def save_node(state: ConflictState) -> dict:
    saved_id = save_verdict_to_db(state["grouped_chunks"], state["query"], state["verdict"])
    return {"saved_id": saved_id}


def skip_save_node(state: ConflictState) -> dict:
    return {"saved_id": None}


def route_after_compare(state: ConflictState) -> str:
    verdict_text = state.get("verdict", "").upper()
    if "CONTRADICT" in verdict_text:
        return "adversarial_critic"
    elif "PARTIAL" in verdict_text:
        return "save"
    return "skip"


def route_after_critic(state: ConflictState) -> str:
    verdict_text = state.get("verdict", "").upper()
    if "PARTIAL" in verdict_text or "CONTRADICT" in verdict_text or "PARTIALLY CONSISTENT" in verdict_text:
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