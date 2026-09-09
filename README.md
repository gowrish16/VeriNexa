# VeriNexa

> **On-Device Agentic RAG Platform for Biomedical Contradiction Detection & Literature Integrity Auditing**

VeriNexa audits clinical trial literature to identify cross-study contradictions and within-paper abstract spin without relying on external cloud APIs.

---

## ⚡ Core Architecture
- **Hybrid Retrieval (RRF):** Fuses dense vector similarity (`pgvector`) with sparse lexical matching (`BM25`) via Reciprocal Rank Fusion to prevent retrieval failures on negated clinical claims.
- **Model Cascade:** Fast domain screening using `llama3.2:1b`, paired with deep claim contradiction analysis using `llama3.1:8b`.
- **Verifiable Provenance:** Bounding-box coordinate extraction via `pdfplumber` for interactive source-text verification.
- **100% On-Device:** Air-gapped pipeline ensuring zero clinical data leakage.

---

## 🛠️ Tech Stack
- **AI Core:** LangGraph, Ollama (Llama 3.1 8B, Llama 3.2 1B), Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Backend:** FastAPI (Python 3.11), PostgreSQL 17 + `pgvector` (Docker), pdfplumber
- **Frontend:** React, Tailwind CSS, Vite

---

## 🚀 Quickstart

```bash
# 1. Start vector database & inference engine
docker start verilit-postgres
ollama serve

# 2. Run backend (Port 8000)
cd backend && uvicorn main:app --reload --port 8000

# 3. Run frontend (Port 5173)
cd ../frontend && npm run dev
```
