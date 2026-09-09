import os
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

load_dotenv()
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def load_all_chunks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, chunk_index, chunk_text FROM chunks ORDER BY chunk_index;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_vector_ranking(query, chunk_ids):
    query_embedding = model.encode(query).tolist()
    conn = get_connection()
    cursor = conn.cursor()
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

def get_bm25_ranking(query, chunk_ids, chunk_texts):
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

def hybrid_search(query, top_k=5):
    chunks = load_all_chunks()
    chunk_ids = [c[0] for c in chunks]
    chunk_indexes = {c[0]: c[1] for c in chunks}
    chunk_texts_map = {c[0]: c[2] for c in chunks}
    chunk_texts = [c[2] for c in chunks]

    vector_ranking = get_vector_ranking(query, chunk_ids)
    bm25_ranking = get_bm25_ranking(query, chunk_ids, chunk_texts)

    fused_scores = reciprocal_rank_fusion([vector_ranking, bm25_ranking])

    results = [
        (cid, chunk_indexes[cid], chunk_texts_map[cid], score)
        for cid, score in fused_scores.items()
    ]
    results.sort(key=lambda x: x[3], reverse=True)

    return results[:top_k]

if __name__ == "__main__":
    query = "effect of SGLT2 inhibitor on body weight"
    print(f"Query: {query}\n")

    results = hybrid_search(query)
    for chunk_id, chunk_index, chunk_text, score in results:
        print(f"--- Chunk {chunk_index} (RRF score: {score:.4f}) ---")
        print(chunk_text[:150])
        print()