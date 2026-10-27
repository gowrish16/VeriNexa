import asyncio
import json
import time
import httpx
from main import app
from auth import create_access_token

async def test_streaming():
    print("=== Testing FastAPI SSE Streaming Endpoint ===")
    token = create_access_token({"sub": "20", "id": 20})

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Check health
        health = await client.get("/health")
        print("Health check:", health.status_code, health.json())

        # Test streaming chat
        payload = {
            "question": "What are the effects of SGLT2 inhibitors and GLP-1 on diabetes?",
            "session_id": None
        }

        print("\nSending request to /api/chat/stream...")
        t0 = time.time()
        first_token_time = None
        tokens_received = 0
        full_text = ""
        citations_received = []

        async with client.stream(
            "POST",
            "/api/chat/stream",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=180.0
        ) as response:
            print("Response status:", response.status_code)
            print("Content-Type:", response.headers.get("content-type"))
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if data.get("type") == "node_lifecycle":
                        print(f"  [Lifecycle] {data.get('node')}: {data.get('status')}")
                    elif data.get("token") and not data.get("done"):
                        if first_token_time is None:
                            first_token_time = time.time() - t0
                            print(f"\n  First token received in: {first_token_time:.2f}s!")
                        tokens_received += 1
                        full_text += data["token"]
                        # Print every 20 tokens
                        if tokens_received % 20 == 0:
                            print(f"  ...streamed {tokens_received} tokens...")
                    elif data.get("done"):
                        citations_received = data.get("citations", [])
                        print(f"\n  [Done] Stream completed. Citations: {len(citations_received)}")

        total_time = time.time() - t0
        print(f"\nTotal streaming time: {total_time:.2f}s")
        print(f"Total tokens received: {tokens_received}")
        print(f"First token latency: {first_token_time:.2f}s")
        print(f"Generated text excerpt:\n{full_text[:300]}...")

        print("\nCitations verification:")
        for c in citations_received:
            print(f"  - Source: {c.get('title')} (Doc: {c.get('filename')}), Page: {c.get('page_number')}")
            print(f"    Bbox: ({c.get('bbox_x0')}, {c.get('bbox_y0')}, {c.get('bbox_x1')}, {c.get('bbox_y1')})")
            print(f"    Score: {c.get('score')}")

        assert tokens_received > 0, "No tokens received"
        assert len(citations_received) <= 3, f"Expected top_k<=3 citations, got {len(citations_received)}"
        print("\nALL STREAMING ASSERTIONS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_streaming())
