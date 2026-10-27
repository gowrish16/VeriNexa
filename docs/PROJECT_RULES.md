# VeriNexa Engineering Guardrails & Quality Assurance Standards

**System**: VeriNexa (Cross-Document Contradiction Detection & Integrity Verification)  
**Track**: Clinical Information Retrieval & Natural Language Inference  
**Document Revision**: 1.0 (Enterprise Quality Protocol)

---

## 1. Architectural Guardrails

### 1.1 Zero-Data-Egress Clinical Privacy Moat
* **HIPAA & GDPR Compliance**: Clinical trial protocols, unpublished drug efficacy data, and patient-level biomarker summaries must remain strictly confidential.
* **No Remote LLM API Calls**: Zero data may leave the local boundary. Calls to external APIs (OpenAI, Anthropic Claude, Google Gemini, Cohere, etc.) are strictly prohibited in all development, testing, and production builds.
* **Local Inference Stack**:
  * LLM Reasoning: Local Ollama daemon running on `http://127.0.0.1:11434` (pinned models: `llama3.2:1b`, `llama3.1:8b`).
  * Dense Embeddings: Local SentenceTransformers (`all-MiniLM-L6-v2`) executing in strict offline mode (`HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`).

### 1.2 Strict 384-Dimensional pgvector Schema Immutability
* The pgvector column (`paper_chunks.embedding`) is permanently locked to **384 dimensions** (matching `all-MiniLM-L6-v2`).
* HNSW / IVFFlat vector indexing and cosine distance queries (`<=> %s::vector`) are immutable. No changes to vector dimensionality or distance metrics are permitted.

### 1.3 Deterministic Spatial Coordinate Preservation
* Coordinate normalization: Bounding boxes `(bbox_x0, bbox_y0, bbox_x1, bbox_y1)` must be computed deterministically in the range `[0.0, 1.0]` relative to page dimensions `(page_w, page_h)`.
* Negative coordinate offsets or overflows (> 1.0) must be clamped defensibly.
* Precision is required for frontend PDF canvas overlays and visual grounding.

---

## 2. Coding Standards & API Specifications

### 2.1 Typing & Pydantic v2 Schemas
* All FastAPI routes must include full Python type annotations (`typing.Optional`, `typing.List`, `typing.Dict`, `typing.Union`).
* Every request body and structured response must be represented by a Pydantic v2 `BaseModel` schema with validation bounds (e.g. `Field(ge=1, le=100)`).

### 2.2 Structured Exception Handling
* No bare `except:` or silent `pass` blocks.
* Clean HTTP error mapping:
  * `400 Bad Request`: Corrupted payload, malformed parameters, non-PDF upload.
  * `401 Unauthorized`: Missing, expired, or invalid JWT authentication token.
  * `403 Forbidden`: Cross-tenant access violation or insufficient privileges.
  * `404 Not Found`: Target paper, chunk, or session does not exist.
  * `422 Unprocessable Entity`: Document fails 3-Tier biomedical verification gate or contains unparseable internal structures.
  * `503 Service Unavailable`: Local Ollama inference service is offline or connection pool is exhausted.

### 2.3 Strict Multi-Tenant Isolation
* All SQL queries touching clinical data must enforce tenant scoping (`WHERE user_id = %s` or tenant predicate).
* Cross-tenant data leakage is treated as a critical security defect.

---

## 3. Testing & Verification Checklist

| Test Category | Target Module | Pass Criteria |
|---|---|---|
| **Unit: Spatial Math** | `backend/ingest.py` | Normalizes coordinates `[0.0, 1.0]`, handles rotated/arbitrary pages without NaN or negative values. |
| **Unit: NLI & Verdict Parsing** | `backend/conflict_engine.py`, `frontend/src/App.jsx` | Sanitizes all model verdict outputs into 4 canonical states (`CONFLICT DETECTED`, `CONCORDANT`, `INSUFFICIENT DATA`, `PARTIAL`). |
| **Unit: Statistical Chunking** | `backend/ingest.py` | Never splits numerical values (hazard ratios, confidence intervals, p-values) from their statistical context. |
| **Integration: Evidence Chat** | `backend/chat_engine.py`, `/api/chat/stream` | Full SSE streaming lifecycle, valid JSON node tokens, deterministic citation metadata. |
| **Integration: LangGraph Conflict Engine** | `backend/conflict_graph.py` | 4-node state traversal (`retrieve` -> `extract` -> `arbitrate` -> `critic`) with verifiable contradiction flags. |
| **Integration: Abstract Spin Auditor** | `backend/integrity_graph.py` | Abstract claims audited against raw table data, flagging exaggerations as `INCONSISTENT`. |
| **Red-Team: Prompt Injections** | `backend/tests/test_adversarial.py` | Closed-corpus grounding overrides adversarial attempts to force `CONCORDANT` or hallucinate safety. |
| **Red-Team: Malformed Ingestion** | `backend/tests/test_adversarial.py` | 0-byte files, corrupted streams, and password-locked PDFs return clean 400/422 without 500 crashes. |
| **Red-Team: SQL & Boundary** | `backend/tests/test_adversarial.py` | Parameterized queries block SQL injection; out-of-range pagination limits (`limit=-1`, `limit=100000`) are safely clamped. |
| **Concurrency & Load** | `backend/tests/test_concurrency.py` | 10 concurrent requests (5 Chat, 3 Integrity, 2 Conflict) fulfill gracefully without connection pool exhaustion. |
