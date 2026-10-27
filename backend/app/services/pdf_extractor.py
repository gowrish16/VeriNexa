"""
PDF Extraction and Ingestion Service for VeriNexa Biomedical Audit System
Provides text extraction, bounding box layout preservation, chunking,
embedding generation, and vector database re-indexing.
"""

import os
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from ingest import (
    extract_text_from_pdf,
    chunk_text,
    extract_chunks_with_bboxes,
    check_is_biomedical,
    ingest_pdf,
    get_connection,
    model
)

def purge_chunks_by_pattern(pattern: str = "GLP1"):
    """
    Purges rows from document_chunks and paper_chunks where doc_id matches the pattern.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM document_chunks WHERE doc_id ILIKE %s;", (f"%{pattern}%",))
    cur.execute("DELETE FROM papers WHERE title ILIKE %s OR filename ILIKE %s;", (f"%{pattern}%", f"%{pattern}%"))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Purged records matching pattern: {pattern}")

def reindex_document(pdf_path: str, doc_id: str, user_id=None):
    """
    Ingests and indexes a clean PDF document into pgvector.
    """
    result = ingest_pdf(pdf_path, doc_id, user_id=user_id)
    return result

if __name__ == "__main__":
    sample_pdf = os.path.join(backend_root, "test_pdfs", "GLP1_SGLT2_2025.pdf")
    if os.path.exists(sample_pdf):
        print(f"Ingesting clean clinical trial PDF: {sample_pdf}")
        res = ingest_pdf(sample_pdf, "GLP1_SGLT2_2025")
        print("Ingestion result:", res)
    else:
        print(f"File not found: {sample_pdf}")
