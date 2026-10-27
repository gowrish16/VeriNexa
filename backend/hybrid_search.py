import os
import re
import asyncio
from typing import Optional, List, Tuple
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import hashlib
import time

load_dotenv()
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Simple in-memory cache for search results
SEARCH_CACHE = {}
CACHE_TTL = 300  # 5 minutes

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


def generate_cache_key(query: str, top_k: int, paper_id: Optional[int], user_id: Optional[int]) -> str:
    """Generate a unique cache key for search parameters"""
    key_str = f"{query}|{top_k}|{paper_id}|{user_id}"
    return hashlib.md5(key_str.encode()).hexdigest()


def get_cached_result(cache_key: str):
    """Retrieve cached result if valid"""
    if cache_key in SEARCH_CACHE:
        cached_data, timestamp = SEARCH_CACHE[cache_key]
        if time.time() - timestamp < CACHE_TTL:
            return cached_data
        else:
            del SEARCH_CACHE[cache_key]
    return None


def set_cached_result(cache_key: str, result):
    """Store result in cache"""
    SEARCH_CACHE[cache_key] = (result, time.time())


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


def load_all_chunks(paper_id: Optional[int] = None, user_id: Optional[int] = None):
    conn = get_connection()
    cursor = conn.cursor()
    conditions = []
    params = []

    if paper_id is not None:
        try:
            pid = int(paper_id)
            conditions.append("paper_id = %s")
            params.append(pid)
        except (ValueError, TypeError):
            pass
    if user_id is not None:
        conditions.append("user_id = %s")
        params.append(user_id)
    else:
        conditions.append("1=0")

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query_str = f"""
        SELECT id, chunk_index, chunk_text, page_number, bbox_x0, bbox_y0, bbox_x1, bbox_y1
        FROM paper_chunks
        {where_clause}
        ORDER BY chunk_index;
    """
    cursor.execute(query_str, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_vector_ranking(query: str, paper_id: Optional[int] = None, user_id: Optional[int] = None, limit: int = 4):
    safe_limit = max(1, min(int(limit), 100)) if limit is not None else 4
    query_embedding = model.encode(query, batch_size=1, normalize_embeddings=True).tolist()
    conn = get_connection()
    cursor = conn.cursor()

    conditions = []
    params = []
    if paper_id is not None:
        try:
            pid = int(paper_id)
            conditions.append("paper_id = %s")
            params.append(pid)
        except (ValueError, TypeError):
            pass
    if user_id is not None:
        conditions.append("user_id = %s")
        params.append(user_id)
    else:
        conditions.append("1=0")

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    params.append(query_embedding)
    params.append(safe_limit)

    query_str = f"""
        SELECT id
        FROM paper_chunks
        {where_clause}
        ORDER BY embedding <=> %s::vector ASC
        LIMIT %s;
    """
    cursor.execute(query_str, params)
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


def hybrid_search(query: str, top_k: int = 4, paper_id: Optional[int] = None, user_id: Optional[int] = None):
    safe_top_k = max(1, min(int(top_k), 100)) if top_k is not None else 4
    search_query = denoise_query(query)

    # Check cache first
    cache_key = generate_cache_key(search_query, safe_top_k, paper_id, user_id)
    cached_result = get_cached_result(cache_key)
    if cached_result is not None:
        return cached_result

    chunks = load_all_chunks(paper_id=paper_id, user_id=user_id)
    if not chunks:
        return []

    chunk_ids = [c[0] for c in chunks]
    chunk_indexes = {c[0]: c[1] for c in chunks}
    chunk_texts_map = {c[0]: c[2] for c in chunks}
    chunk_meta_map = {
        c[0]: {
            "page_number": c[3] if len(c) > 3 else 1,
            "bbox_x0": c[4] if len(c) > 4 else 0.0,
            "bbox_y0": c[5] if len(c) > 5 else 0.0,
            "bbox_x1": c[6] if len(c) > 6 else 0.0,
            "bbox_y1": c[7] if len(c) > 7 else 0.0,
        }
        for c in chunks
    }
    chunk_texts = [c[2] for c in chunks]

    vector_ranking = get_vector_ranking(search_query, paper_id=paper_id, user_id=user_id, limit=safe_top_k)
    bm25_ranking = get_bm25_ranking(search_query, chunk_ids, chunk_texts)

    fused_scores = reciprocal_rank_fusion([vector_ranking, bm25_ranking])

    boosted_results = []
    for cid, score in fused_scores.items():
        if cid in chunk_texts_map:
            boosted_score = apply_section_boost(chunk_texts_map[cid], score)
            meta = chunk_meta_map.get(cid, {})
            boosted_results.append((
                cid,
                chunk_indexes[cid],
                chunk_texts_map[cid],
                boosted_score,
                meta.get("page_number", 1),
                meta.get("bbox_x0", 0.0),
                meta.get("bbox_y0", 0.0),
                meta.get("bbox_x1", 0.0),
                meta.get("bbox_y1", 0.0)
            ))

    boosted_results.sort(key=lambda x: x[3], reverse=True)
    result = boosted_results[:safe_top_k]

    # Cache the result
    set_cached_result(cache_key, result)

    return result


async def async_get_vector_ranking(query: str, paper_id: Optional[int] = None, user_id: Optional[int] = None, limit: int = 4):
    """Non-blocking async wrapper for get_vector_ranking"""
    return await asyncio.to_thread(get_vector_ranking, query, paper_id=paper_id, user_id=user_id, limit=limit)


async def async_hybrid_search(query: str, top_k: int = 4, paper_id: Optional[int] = None, user_id: Optional[int] = None):
    """Non-blocking async wrapper for hybrid_search"""
    return await asyncio.to_thread(hybrid_search, query, top_k=top_k, paper_id=paper_id, user_id=user_id)


if __name__ == "__main__":
    query = "effect of SGLT2 inhibitor on body weight"
    print(f"Query: {query}\n")

    results = hybrid_search(query)
    for chunk_id, chunk_index, chunk_text, score in results:
        print(f"--- Chunk {chunk_index} (RRF score: {score:.4f}) ---")
        print(chunk_text[:150])
        print()