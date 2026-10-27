import os
import re
import json
import psycopg2
import psycopg2.extras
import requests
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import pdfplumber

load_dotenv()
from config import DEFAULT_MODEL, KEEP_ALIVE, NUM_THREAD, NUM_GPU, OLLAMA_BASE_URL
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

CHUNK_SIZE = 500

model = SentenceTransformer("all-MiniLM-L6-v2")


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


# ---------------- Three-Tier Biomedical Verification Gate ----------------
BIOMED_KEYWORDS = [
    'abstract', 'introduction', 'methods', 'results', 'conclusion', 'discussion',
    'references', 'clinical', 'trial', 'patient', 'patients', 'treatment', 'disease',
    'therapy', 'cohort', 'diagnosis', 'syndrome', 'cellular', 'molecular', 'protein',
    'gene', 'drug', 'dose', 'hazard', 'placebo', 'in vitro', 'in vivo', 'pathology',
    'survival', 'safety', 'efficacy', 'adverse', 'hospital', 'biomarker', 'plasma',
    'serum', 'sample', 'assay', 'p-value', 'sd', 'ci', 'medicine', 'medical', 'health',
    'biology', 'biological', 'doi', 'pmid', 'pmc'
]

EXPLICIT_NON_SCIENTIFIC = [
    # Resumes / CVs
    r"\bcurriculum\s+vitae\b",
    r"\bresume\b",
    r"\bwork\s+experience\b",
    r"\bemployment\s+history\b",
    r"\beducation\s+history\b",
    r"\bskills\s*&\s*certifications\b",
    # Invoices / Financial Statements / Tax Forms
    r"\binvoice\s+number\b",
    r"\btax\s+return\b",
    r"\bw-2\b",
    r"\b1099-misc\b",
    r"\bbalance\s+sheet\b",
    r"\bpurchase\s+order\b",
    r"\bbilling\s+address\b",
    r"\bamount\s+due\b",
    # Raw programming source code files
    r"\bimport\s+react\s+from\b",
    r"\bconst\s+\w+\s*=\s*require\(",
    r"\bdef\s+__init__\s*\(self\b",
    r"\bpackage\.json\b",
    r"\bnpm\s+install\b"
]


def clean_and_extract_verification_text(pdf_path, max_words=1500, return_raw=False):
    """
    Tier 1 Text Extraction:
    Extracts text from the first 3 full pages (not just page 1 or 2).
    Strips leading copyright, DOI metadata, and author address/affiliation headers.
    """
    raw_pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:3]:
                text = page.extract_text()
                if text:
                    raw_pages.append(text)
    except Exception as e:
        print(f"Error extracting pages from {pdf_path}: {e}")
        return ("", "") if return_raw else ""

    if not raw_pages:
        return ("", "") if return_raw else ""

    full_raw = "\n".join(raw_pages)

    cleaned_lines = []
    for line in full_raw.splitlines():
        l_str = line.strip()
        l_lower = l_str.lower()
        if not l_str:
            continue

        # Strip leading publisher metadata, DOI, copyright, and author headers
        if any(l_lower.startswith(prefix) for prefix in [
            "doi", "published", "editedby", "edited by", "reviewedby", "reviewed by",
            "correspondence", "*correspondence", "openaccess", "open access", "copyright",
            "all rights reserved", "received", "accepted", "citation", "orcid"
        ]):
            continue

        # Strip email addresses or pure university/hospital address listings
        if "@" in l_str or re.search(r"^\d\s*(department|school|graduate|faculty|university|hospital|institute)", l_lower):
            continue
        if re.search(r"^(dr\.|prof\.|mr\.|ms\.)", l_lower):
            continue

        cleaned_lines.append(l_str)

    cleaned_text = "\n".join(cleaned_lines)
    words = cleaned_text.split()
    truncated_cleaned = " ".join(words[:max_words])
    if return_raw:
        return truncated_cleaned, full_raw
    return truncated_cleaned


def check_is_biomedical(pdf_path):
    """
    Three-Tier Biomedical Verification Gate for Live Demonstrations:

    Tier 1 (Text Extraction Resilience):
      - Extracts text from the first 3 pages.
      - If extracted text across the first 3 pages is under 150 characters (e.g. scanned PDF
        or image-based title page), skips text rejection and allows ingestion with a warning:
        'Scanned or low-text PDF detected: permitted for processing.'

    Tier 2 (Multi-tier Check):
      - Primary: Checks for biomedical/scientific indicators:
        ['abstract', 'introduction', 'methods', 'results', 'conclusion', 'discussion',
         'references', 'clinical', 'trial', 'patient', 'patients', 'treatment', 'disease',
         'therapy', 'cohort', 'diagnosis', 'syndrome', 'cellular', 'molecular', 'protein',
         'gene', 'drug', 'dose', 'hazard', 'placebo', 'in vitro', 'in vivo', 'pathology',
         'survival', 'safety', 'efficacy', 'adverse', 'hospital', 'biomarker', 'plasma',
         'serum', 'sample', 'assay', 'p-value', 'sd', 'ci', 'medicine', 'medical', 'health',
         'biology', 'biological', 'doi', 'pmid', 'pmc'].
        If at least 2 of these terms appear anywhere in the first 3 pages, accepts immediately as VALID.
      - Secondary (LLM semantic check):
        If fewer than 2 keywords match, queries Ollama with a 50-word excerpt:
        "Determine if this document could be an academic, scientific, medical, biological, or healthcare paper.
         If it is NOT an obvious resume, balance sheet, or programming script, answer 'VALID'. Otherwise answer 'INVALID'."
        If the model returns VALID, accept it.

    Tier 3 (Fail-Safe Default):
      - Only returns HTTP 422 if the document is explicitly detected as non-scientific
        (e.g. text contains explicit markers of resumes, invoices, tax forms, or raw python/javascript source files).
      - If uncertain, defaults to ACCEPTING the file so valid biomedical papers brought by examiners are never blocked.
    """
    cleaned_text, raw_text = clean_and_extract_verification_text(pdf_path, max_words=1500, return_raw=True)

    # 1. Text Extraction Resilience (< 150 characters check across first 3 pages)
    combined_len = max(len(raw_text.strip()), len(cleaned_text.strip()))
    if combined_len < 150:
        warning_msg = "Scanned or low-text PDF detected: permitted for processing."
        print(f"[Verification Gate] {warning_msg} (length: {combined_len} chars)")
        return True, warning_msg

    text_to_check = (cleaned_text + " " + raw_text).lower()

    # 2. Primary Check: Biomedical / Scientific Indicators (>= 2 terms)
    matched_biomed = []
    for kw in BIOMED_KEYWORDS:
        if " " in kw or "-" in kw:
            if kw in text_to_check:
                matched_biomed.append(kw)
        else:
            if re.search(r"\b" + re.escape(kw) + r"\b", text_to_check):
                matched_biomed.append(kw)

    if len(matched_biomed) >= 2:
        msg = f"Verified biomedical/scientific literature (matched indicators: {', '.join(matched_biomed[:5])})."
        print(f"[Verification Gate] {msg}")
        return True, msg

    # Identify explicit non-scientific markers (resumes, invoices, code)
    matched_non_scientific = [p for p in EXPLICIT_NON_SCIENTIFIC if re.search(p, text_to_check)]

    # 3. Secondary Check: LLM Semantic Check with 50-word excerpt
    words = (cleaned_text or raw_text).split()
    excerpt_50 = " ".join(words[:50])

    prompt = f"""Determine if this document could be an academic, scientific, medical, biological, or healthcare paper. If it is NOT an obvious resume, balance sheet, or programming script, answer 'VALID'. Otherwise answer 'INVALID'.

Document excerpt:
\"\"\"
{excerpt_50}
\"\"\"

Answer strictly VALID or INVALID:"""

    llm_valid = False
    llm_evaluated = False
    try:
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": DEFAULT_MODEL,
                "prompt": prompt,
                "stream": False,
                "keep_alive": KEEP_ALIVE, "options": {"num_predict": 10, "temperature": 0.0, "num_thread": NUM_THREAD, "num_gpu": NUM_GPU}
            },
            timeout=20
        )
        if r.status_code == 200:
            llm_evaluated = True
            resp = r.json().get("response", "").strip().upper()
            if "VALID" in resp and "INVALID" not in resp:
                llm_valid = True
            elif "INVALID" in resp:
                llm_valid = False
    except Exception as e:
        print(f"[Verification Gate] Ollama semantic check note: {e}")

    if llm_valid:
        msg = "Verified academic/scientific literature via LLM semantic check (VALID)."
        print(f"[Verification Gate] {msg}")
        return True, msg

    # 4. Fail-Safe Default:
    # Only return rejection if explicitly detected as non-scientific
    if matched_non_scientific and (not llm_valid or (llm_evaluated and not llm_valid)):
        rejection_msg = "Document rejected: Not a recognized biomedical or clinical trial paper. Please upload clinical research literature."
        print(f"[Verification Gate] {rejection_msg} (explicit non-scientific marker detected: {matched_non_scientific[0]})")
        return False, rejection_msg

    # Default to ACCEPTING the file so live presentations and examiner papers are never blocked
    default_msg = "Permitted for processing (fail-safe default: no explicit non-scientific markers detected)."
    print(f"[Verification Gate] {default_msg}")
    return True, default_msg


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


def get_word_top(w, page_h):
    if "top" in w and w["top"] is not None:
        return float(w["top"])
    if "y1" in w and w["y1"] is not None:
        return float(page_h - w["y1"])
    return 0.0


def get_word_bottom(w, page_h):
    if "bottom" in w and w["bottom"] is not None:
        return float(w["bottom"])
    if "y0" in w and w["y0"] is not None:
        return float(page_h - w["y0"])
    return float(page_h)


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
                                "bbox_top": 0.0,
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
                        top_y = min(get_word_top(w, page_h) for w in current_words)
                        x1 = max(w["x1"] for w in current_words)
                        bottom_y = max(get_word_bottom(w, page_h) for w in current_words)

                        norm_x0 = max(0.0, min(1.0, round(float(x0 / page_w), 4)))
                        norm_top = max(0.0, min(1.0, round(float(top_y / page_h), 4)))
                        norm_x1 = max(0.0, min(1.0, round(float(x1 / page_w), 4)))
                        norm_bottom = max(0.0, min(1.0, round(float(bottom_y / page_h), 4)))

                        chunks_with_meta.append({
                            "text": chunk_text,
                            "page_number": page_number,
                            "bbox_x0": norm_x0,
                            "bbox_y0": norm_top,
                            "bbox_top": norm_top,
                            "bbox_x1": norm_x1,
                            "bbox_y1": norm_bottom
                        })
                    current_words = []
                    current_len = 0

            if current_words:
                chunk_text = " ".join([w["text"] for w in current_words]).strip()
                if chunk_text:
                    x0 = min(w["x0"] for w in current_words)
                    top_y = min(get_word_top(w, page_h) for w in current_words)
                    x1 = max(w["x1"] for w in current_words)
                    bottom_y = max(get_word_bottom(w, page_h) for w in current_words)

                    norm_x0 = max(0.0, min(1.0, round(float(x0 / page_w), 4)))
                    norm_top = max(0.0, min(1.0, round(float(top_y / page_h), 4)))
                    norm_x1 = max(0.0, min(1.0, round(float(x1 / page_w), 4)))
                    norm_bottom = max(0.0, min(1.0, round(float(bottom_y / page_h), 4)))

                    chunks_with_meta.append({
                        "text": chunk_text,
                        "page_number": page_number,
                        "bbox_x0": norm_x0,
                        "bbox_y0": norm_top,
                        "bbox_top": norm_top,
                        "bbox_x1": norm_x1,
                        "bbox_y1": norm_bottom
                    })

    return chunks_with_meta


def extract_detected_title(pdf_path):
    """
    Extracts the actual scientific paper title from PDF metadata or page 1 prominent text.
    """
    try:
        with pdfplumber.open(pdf_path) as doc:
            meta = doc.metadata or {}
            m_title = (meta.get('Title') or meta.get('title') or '').strip()

            # Check if meta title is valid scientific title (not publisher internal code or filename)
            is_valid_meta = False
            if m_title and len(m_title) > 8:
                if not re.search(r'^\w+\s+\d+\.\.\d+$', m_title) and not m_title.lower().endswith(('.pdf', '.docx', '.tex', '.indd')):
                    if not any(k in m_title.lower() for k in ['untitled', 'microsoft word', 'template', 'arxiv', '11_ctj']):
                        if len(m_title.split()) >= 2:
                            is_valid_meta = True

            if is_valid_meta:
                return m_title

            # Fallback to page 1 prominent text
            if doc.pages:
                p0 = doc.pages[0]
                words = p0.extract_words(extra_attrs=['size'])
                if words:
                    top_words = [w for w in words if w.get('top', 0) < (p0.height or 792) * 0.65]
                    ignore_patterns = [
                        r'^this article is licensed', r'^http', r'^doi:', r'^contents lists',
                        r'^original research', r'^originalinvestigation', r'^review', r'^typereview',
                        r'^systematic review', r'^medicine', r'^open', r'^published', r'^editedby',
                        r'^letters', r'^food chemistry', r'^journal', r'^access', r'^american journal'
                    ]
                    # Filter out giant journal logo words (>35pt single words like "Medicine")
                    candidate_words = [w for w in top_words if not (w.get('size', 0) > 35 and len(w['text']) < 15)]
                    if candidate_words:
                        max_size = max(w.get('size', 0) for w in candidate_words)
                        prominent_threshold = max(max_size * 0.70, 13.0)
                        title_words = [w for w in candidate_words if w.get('size', 0) >= prominent_threshold]
                        
                        lines = []
                        curr_line = []
                        last_top = None
                        for w in title_words:
                            w_top = w.get('top', 0)
                            if last_top is None or abs(w_top - last_top) < 8:
                                curr_line.append(w['text'])
                                last_top = w_top
                            else:
                                if curr_line:
                                    lines.append(' '.join(curr_line))
                                curr_line = [w['text']]
                                last_top = w_top
                        if curr_line:
                            lines.append(' '.join(curr_line))

                        cleaned_lines = []
                        for l in lines:
                            l_clean = l.strip()
                            if any(re.search(pat, l_clean.lower()) for pat in ignore_patterns):
                                continue
                            if re.search(r'\bdepartment\b|\buniversity\b|\bhospital\b|@|\bph\.?d\b|\bcorrespondence\b', l_clean.lower()):
                                break
                            if len(l_clean) > 3 and not re.match(r'^[0-9\W]+$', l_clean):
                                cleaned_lines.append(l_clean)

                        if cleaned_lines:
                            if len(cleaned_lines) > 1 and cleaned_lines[0].lower() in ['systematic review and meta-analysis', 'systematic review', 'meta-analysis', 'clinical trial', 'review', 'research article']:
                                cleaned_lines = cleaned_lines[1:]
                            detected = ' '.join(cleaned_lines[:3]).strip()
                            detected = re.sub(r'^(fi|fl)\s+', '', detected, flags=re.IGNORECASE)
                            detected = re.sub(r'\s+ACCESS$', '', detected, flags=re.IGNORECASE)
                            detected = re.sub(r'\s+\d+\s+Introduction$', '', detected, flags=re.IGNORECASE)
                            detected = re.sub(r'ef\s+ciency', 'efficiency', detected, flags=re.IGNORECASE)
                            if len(detected) > 6:
                                return detected

                p1_text = doc.pages[0].extract_text() or ''
                for line in p1_text.splitlines()[:15]:
                    l = line.strip()
                    if len(l) > 15 and not any(re.search(pat, l.lower()) for pat in [r'^this article', r'^http', r'^doi', r'^copyright', r'^volume', r'^issue', r'^journal']):
                        return l
    except Exception as e:
        print(f"Error extracting detected title from {pdf_path}: {e}")
    return os.path.basename(pdf_path).replace('.pdf', '').replace('_', ' ')


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

    detected_title = extract_detected_title(pdf_path) or title
    print(f"Detected title: '{detected_title}'")

    conn = get_connection()
    cursor = conn.cursor()

    filename = os.path.basename(pdf_path)
    if user_id:
        cursor.execute(
            "INSERT INTO papers (title, filename, user_id, detected_title) VALUES (%s, %s, %s, %s) RETURNING id;",
            (title, filename, user_id, detected_title)
        )
    else:
        cursor.execute(
            "INSERT INTO papers (title, filename, detected_title) VALUES (%s, %s, %s) RETURNING id;",
            (title, filename, detected_title)
        )
    paper_id = cursor.fetchone()[0]
    print(f"Inserted paper record with id: {paper_id}")

    print("Generating embeddings in batch...")
    chunk_texts = [item["text"] for item in chunks_meta]
    embeddings = model.encode(chunk_texts).tolist()

    insert_records = [
        (
            paper_id, title, user_id, item["text"], index, item["page_number"],
            item["bbox_x0"], item["bbox_y0"], item["bbox_x1"], item["bbox_y1"],
            embedding
        )
        for index, (item, embedding) in enumerate(zip(chunks_meta, embeddings))
    ]

    psycopg2.extras.execute_batch(
        cursor,
        """
        INSERT INTO paper_chunks (
            paper_id, doc_id, user_id, chunk_text, chunk_index, page_number,
            bbox_x0, bbox_y0, bbox_x1, bbox_y1, embedding
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
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