from sentence_transformers import SentenceTransformer

def test_embedding():
    print("Loading model... (this may take a moment the first time)")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    sample_text = "SGLT2 inhibitors reduced HbA1c levels in patients with type 2 diabetes."
    embedding = model.encode(sample_text)

    print(f"\nEmbedding generated successfully.")
    print(f"Embedding length: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")

if __name__ == "__main__":
    test_embedding()