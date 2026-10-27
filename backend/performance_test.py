import time
from hybrid_search import hybrid_search

# Test search performance with caching
def test_search_performance():
    test_queries = [
        "What are the main side effects of SGLT2 inhibitors?",
        "effect of SGLT2 inhibitor on body weight",
        "What are the main side effects of SGLT2 inhibitors?"  # Duplicate to test cache
    ]

    print("=== Performance Test: Hybrid Search with Caching ===\n")

    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        start = time.time()
        results = hybrid_search(query, top_k=3)
        end = time.time()
        duration = end - start
        print(f"  Results: {len(results)} chunks")
        print(f"  Duration: {duration:.3f}s")
        print(f"  Status: {'CACHED' if i == 3 else 'FRESH'}")
        print()

if __name__ == "__main__":
    test_search_performance()
