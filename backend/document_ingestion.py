"""
document_ingestion.py - Biomedical Document Ingestion and Verification Gate Interface
Provides three-tier resilient verification logic and PDF ingestion pipeline.
"""
from ingest import (
    clean_and_extract_verification_text,
    check_is_biomedical,
    ingest_pdf,
    extract_chunks_with_bboxes,
    extract_text_from_pdf,
    chunk_text,
    get_connection,
    extract_detected_title,
    BIOMED_KEYWORDS,
    EXPLICIT_NON_SCIENTIFIC,
)

__all__ = [
    "clean_and_extract_verification_text",
    "check_is_biomedical",
    "ingest_pdf",
    "extract_chunks_with_bboxes",
    "extract_text_from_pdf",
    "chunk_text",
    "get_connection",
    "extract_detected_title",
    "BIOMED_KEYWORDS",
    "EXPLICIT_NON_SCIENTIFIC",
]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        pdf = sys.argv[1]
        valid, msg = check_is_biomedical(pdf)
        print(f"Result for {pdf}: valid={valid}, message='{msg}'")
    else:
        print("document_ingestion module ready with three-tier verification gate.")
