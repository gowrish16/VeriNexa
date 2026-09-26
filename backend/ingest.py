import os
import json
import psycopg2
import psycopg2.extras
import requests
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import pdfplumber

load_dotenv()

CHUNK_SIZE = 500

model = SentenceTransformer("all-MiniLM-L6-v2")


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def check_is_biomedical(pdf_path):
    extracted_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        # Extract from the first 2 pages (or all available if fewer)
        for page in pdf.pages[:2]:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n"

    # Up to 2500 characters so model sees Introduction, Methods, and Study Characteristics
    extracted_sample_text = extracted_text[:2500].strip()

    # 3. FAST-PATH HEURISTIC FALLBACK:
    # High-confidence medical terms to automatically accept and prevent false-negative 422 errors
    high_confidence_terms = [
        "clinical trial",
        "randomized controlled trial",
        "randomised controlled trial",
        "meta-analysis",
        "meta analysis",
        "systematic review",
        "sglt2",
        "hba1c",
        "placebo-controlled",
        "placebo controlled",
        "pubmed",
        "prospero",
    ]
    text_lower = extracted_sample_text.lower()
    matched_heuristics = [term for term in high_confidence_terms if term in text_lower]

    # Fast-path heuristic check before calling LLM
    if matched_heuristics:
        matched_str = ", ".join(matched_heuristics[:3])
        return True, f"High-confidence biomedical terms detected ({matched_str}). Verified clinical research."

    prompt = f"""You are an expert biomedical document classifier.
Analyze the following text extracted from a research document and determine if it belongs to biomedical, clinical, pharmacological, or healthcare literature (including clinical trials, randomized controlled trials, systematic reviews, meta-analyses, observational studies, or medical reviews).

Text snippet:
{extracted_sample_text}

Criteria for ACCEPTANCE:
- Discusses medical conditions, patients, pharmacology, clinical treatments, drug mechanisms (e.g., SGLT2, insulin, diabetes, cardiovascular endpoints), or healthcare interventions.
- Includes empirical clinical trials, systematic reviews, meta-analyses, or clinical cohort studies.

Criteria for REJECTION:
- Non-medical fields (e.g., pure computer science, economics, civil engineering, fiction, general non-fiction, legal briefs).

Respond strictly in the following JSON format:
{{
    "is_biomedical": true or false,
    "reason": "Brief explanation"
}}"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1}
            },
            timeout=30
        )
        result_text = response.json()["response"]
        data = json.loads(result_text)
        is_biomedical = bool(data.get("is_biomedical", False))
        reason = data.get("reason", "Biomedical classification completed.")

        # Fallback check after calling LLM
        if not is_biomedical and matched_heuristics:
            return True, f"Verified via biomedical heuristic fallback ({', '.join(matched_heuristics[:3])})."

        return is_biomedical, reason
    except Exception as e:
        if matched_heuristics:
            return True, f"High-confidence biomedical terms verified ({', '.join(matched_heuristics[:3])})."
        return False, f"Biomedical classification failed or rejected: {str(e)}"


def extract_text_from_pdf(pdf_path):
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text


def chunk_text(text, chunk_size=CHUNK_SIZE):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def extract_chunks_with_bboxes(pdf_path, chunk_size=CHUNK_SIZE):
    chunks_with_meta = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_number = page_idx + 1
            page_w = float(page.width or 612.0)
            page_h = float(page.height or 792.0)
            words = page.extract_words()
            if not words:
                text = page.extract_text()
                if text:
                    for i in range(0, len(text), chunk_size):
                        chunk = text[i:i + chunk_size].strip()
                        if chunk:
                            chunks_with_meta.append({
                                "text": chunk,
                                "page_number": page_number,
                                "bbox_x0": 0.0,
                                "bbox_y0": 0.0,
                                "bbox_x1": 0.0,
                                "bbox_y1": 0.0
                            })
                continue

            current_words = []
            current_len = 0
            for w in words:
                current_words.append(w)
                current_len += len(w["text"]) + 1
                if current_len >= chunk_size:
                    chunk_text = " ".join([w["text"] for w in current_words]).strip()
                    if chunk_text:
                        x0 = min(w["x0"] for w in current_words)
                        y0 = min(w["top"] for w in current_words)
                        x1 = max(w["x1"] for w in current_words)
                        y1 = max(w["bottom"] for w in current_words)
                        chunks_with_meta.append({
                            "text": chunk_text,
                            "page_number": page_number,
                            "bbox_x0": round(float(x0 / page_w), 4),
                            "bbox_y0": round(float(y0 / page_h), 4),
                            "bbox_x1": round(float(x1 / page_w), 4),
                            "bbox_y1": round(float(y1 / page_h), 4)
                        })
                    current_words = []
                    current_len = 0

            if current_words:
                chunk_text = " ".join([w["text"] for w in current_words]).strip()
                if chunk_text:
                    x0 = min(w["x0"] for w in current_words)
                    y0 = min(w["top"] for w in current_words)
                    x1 = max(w["x1"] for w in current_words)
                    y1 = max(w["bottom"] for w in current_words)
                    chunks_with_meta.append({
                        "text": chunk_text,
                        "page_number": page_number,
                        "bbox_x0": round(float(x0 / page_w), 4),
                        "bbox_y0": round(float(y0 / page_h), 4),
                        "bbox_x1": round(float(x1 / page_w), 4),
                        "bbox_y1": round(float(y1 / page_h), 4)
                    })

    return chunks_with_meta


def ingest_pdf(pdf_path, title, user_id=None):
    print(f"Checking document type for {pdf_path}...")
    is_biomedical, classification_result = check_is_biomedical(pdf_path)

    if not is_biomedical:
        print("Rejected: not a biomedical research paper.")
        return {"rejected": True, "reason": classification_result}

    print(f"Extracting text and bounding boxes from {pdf_path}...")
    chunks_meta = extract_chunks_with_bboxes(pdf_path)
    if not chunks_meta:
        text = extract_text_from_pdf(pdf_path)
        raw_chunks = chunk_text(text)
        chunks_meta = [
            {"text": c, "page_number": 1, "bbox_x0": 0.0, "bbox_y0": 0.0, "bbox_x1": 0.0, "bbox_y1": 0.0}
            for c in raw_chunks
        ]

    print(f"Created {len(chunks_meta)} chunks with layout metadata.")

    conn = get_connection()
    cursor = conn.cursor()

    filename = os.path.basename(pdf_path)
    if user_id:
        cursor.execute(
            "INSERT INTO papers (title, filename, user_id) VALUES (%s, %s, %s) RETURNING id;",
            (title, filename, user_id)
        )
    else:
        cursor.execute(
            "INSERT INTO papers (title, filename) VALUES (%s, %s) RETURNING id;",
            (title, filename)
        )
    paper_id = cursor.fetchone()[0]
    print(f"Inserted paper record with id: {paper_id}")

    print("Generating embeddings in batch...")
    chunk_texts = [item["text"] for item in chunks_meta]
    embeddings = model.encode(chunk_texts).tolist()

    insert_records = [
        (
            paper_id, user_id, item["text"], index, item["page_number"],
            item["bbox_x0"], item["bbox_y0"], item["bbox_x1"], item["bbox_y1"],
            embedding
        )
        for index, (item, embedding) in enumerate(zip(chunks_meta, embeddings))
    ]

    psycopg2.extras.execute_batch(
        cursor,
        """
        INSERT INTO paper_chunks (
            paper_id, user_id, chunk_text, chunk_index, page_number,
            bbox_x0, bbox_y0, bbox_x1, bbox_y1, embedding
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """,
        insert_records
    )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Successfully ingested {len(chunks_meta)} chunks for paper_id {paper_id} (user_id: {user_id}).")
    return {"rejected": False, "paper_id": paper_id}


if __name__ == "__main__":
    result = ingest_pdf("test_pdfs/medi.pdf", "Safety and efficiency of SGLT2 inhibitor combining with insulin in subjects with diabetes")
    print(result)