import os
import re
from typing import Optional, List, Tuple
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

load_dotenv()
model = SentenceTransformer("all-MiniLM-L6-v2")

STOP_PATTERNS = [
    r"\bexplain\s+in\s+simple\s+terms\b",
    r"\bexplain\s+simply\b",
    r"\bexplain\b",
    r"\bfor\b\s+beginners\b",
    r"\bgive\s+examples?\b",
    r"\bin\s+detail\b",
    r"\bplease\b",
    r"\bcan\s+you\b",
    r"\bwhat\s+is\b",
    r"\bwhat\s+are\b",
    r"\bhow\s+does\b",
    r"\bhow\s+do\b",
    r"\bdescribe\b",
    r"\bsummarize\b",
    r"\btell\s+me\s+about\b",
]

BOOST_TERMS = [
    "abstract", "results", "findings", "outcomes", "primary endpoint",
    "secondary endpoint", "table", "mean", "baseline", "p=", "p <", "p<",
    "confidence interval", "ci", "statistically significant", "randomized"
]


def denoise_query(query: str) -> str:
    cleaned = query.strip()
    for pattern in STOP_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if cleaned else query.strip()


def apply_section_boost(chunk_text: str, score: float) -> float:
    text_lower = chunk_text.lower()
    matches = sum(1 for term in BOOST_TERMS if term in text_lower)
    boost_factor = 1.0 + min(matches * 0.04, 0.30)
    return score * boost_factor


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def load_all_chunks(paper_id: Optional[int] = None):
    conn = get_connection()
    cursor = conn.cursor()
    if paper_id is not None:
        cursor.execute(
            "SELECT id, chunk_index, chunk_text FROM chunks WHERE paper_id = %s ORDER BY chunk_index;",
            (paper_id,)
        )
    else:
        cursor.execute("SELECT id, chunk_index, chunk_text FROM chunks ORDER BY chunk_index;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_vector_ranking(query: str, paper_id: Optional[int] = None):
    query_embedding = model.encode(query).tolist()
    conn = get_connection()
    cursor = conn.cursor()
    if paper_id is not None:
        cursor.execute(
            """
            SELECT id
            FROM chunks
            WHERE paper_id = %s
            ORDER BY embedding <=> %s::vector ASC;
            """,
            (paper_id, query_embedding)
        )
    else:
        cursor.execute(
            """
            SELECT id
            FROM chunks
            ORDER BY embedding <=> %s::vector ASC;
            """,
            (query_embedding,)
        )
    ranked_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return ranked_ids


def get_bm25_ranking(query: str, chunk_ids: List[int], chunk_texts: List[str]):
    if not chunk_ids or not chunk_texts:
        return []
    tokenized_corpus = [text.lower().split() for text in chunk_texts]
    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(query.lower().split())
    scored = list(zip(chunk_ids, scores))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [cid for cid, _ in scored]


def reciprocal_rank_fusion(rankings, k=60):
    rrf_scores = {}
    for ranking in rankings:
        for rank, chunk_id in enumerate(ranking):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (k + rank + 1)
    return rrf_scores


def hybrid_search(query: str, top_k: int = 5, paper_id: Optional[int] = None):
    search_query = denoise_query(query)

    chunks = load_all_chunks(paper_id=paper_id)
    if not chunks:
        return []

    chunk_ids = [c[0] for c in chunks]
    chunk_indexes = {c[0]: c[1] for c in chunks}
    chunk_texts_map = {c[0]: c[2] for c in chunks}
    chunk_texts = [c[2] for c in chunks]

    vector_ranking = get_vector_ranking(search_query, paper_id=paper_id)
    bm25_ranking = get_bm25_ranking(search_query, chunk_ids, chunk_texts)

    fused_scores = reciprocal_rank_fusion([vector_ranking, bm25_ranking])

    boosted_results = []
    for cid, score in fused_scores.items():
        if cid in chunk_texts_map:
            boosted_score = apply_section_boost(chunk_texts_map[cid], score)
            boosted_results.append((cid, chunk_indexes[cid], chunk_texts_map[cid], boosted_score))

    boosted_results.sort(key=lambda x: x[3], reverse=True)
    return boosted_results[:top_k]


if __name__ == "__main__":
    query = "effect of SGLT2 inhibitor on body weight"
    print(f"Query: {query}\n")

    results = hybrid_search(query)
    for chunk_id, chunk_index, chunk_text, score in results:
        print(f"--- Chunk {chunk_index} (RRF score: {score:.4f}) ---")
        print(chunk_text[:150])
        print()