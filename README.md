# VeriNexa

> **On-Device Agentic Retrieval-Augmented Generation (RAG) System for Cross-Trial Contradiction Detection and Abstract Spin Verification in Biomedical Literature**

VeriNexa is a closed-corpus, privacy-centric literature auditing platform engineered to verify findings across clinical research studies and identify internal abstract-to-results discrepancies.

---

## 🔬 Key Architectural Highlights

- **Hybrid Retrieval Architecture**: Combines BM25 lexical keyword search with dense semantic retrieval (`pgvector`) fused via Reciprocal Rank Fusion (RRF, $k=60$) to avoid dense-retrieval semantic collapse on negation.
- **Model Cascade & Agentic Reasoning**:
  - `llama3.2:1b`: Lightweight pre-indexing gate to screen and classify valid biomedical literature.
  - `llama3.1:8b`: Local, quantized LLM orchestrated via LangGraph for abstract spin auditing and cross-paper contradiction mapping.
- **Strict Evidence Provenance**: Grounded citations linked to exact PDF page indices and bounding coordinates.
- **Privacy-First & Air-Gapped**: Fully on-device inference with zero external API calls or third-party cloud data leakage.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn, SQLAlchemy 2.0 Async, `asyncpg`
- **AI / RAG**: LangGraph, LangChain, Ollama (`llama3.1:8b`, `llama3.2:1b`)
- **Database**: PostgreSQL 17 with `pgvector` extension (Docker container on port 5433)
- **Embeddings**: Sentence-Transformers / FastEmbed (`all-MiniLM-L6-v2`, 384-dimensional dense vectors)
- **Ingestion**: `pdfplumber` for structured PDF layout, section, and table extraction
- **Security & Auth**: JWT authentication (bcrypt password hashing, Bearer route guards)
- **Frontend**: React 19 (Vite), Tailwind CSS v4, Lucide Icons, Glassmorphism Design System

---

## 🚀 Local Deployment Setup

### 1. Database (PostgreSQL + pgvector)
Ensure Docker is running, then start the container:
```bash
docker start verilit-postgres
```

### 2. Ollama Local LLMs
Pull and launch the local Llama models via Ollama:
```bash
ollama run llama3.1:8b
ollama run llama3.2:1b
```

### 3. Backend Setup
From the `backend/` directory:
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python init_db.py
uvicorn main:app --reload --port 8000
```
- Interactive API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Backend Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### 4. Frontend Setup
From the `frontend/` directory:
```bash
cd frontend
npm install
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## 📸 Key Features & Capabilities

1. **Air-Gapped Ingestion Gate**: Automatically screens uploaded papers using `llama3.2:1b` + fast-path medical heuristics. Non-biomedical documents are rejected with HTTP 422 to maintain corpus integrity.
2. **Dual-Pane Audit Workspace**: Interactive PDF reader synchronized with verified AI citations and coordinate-based excerpt highlighting.
3. **Abstract Spin Integrity Checker**: Detects divergence between abstract conclusions and empirical results tables (e.g., unreported statistically non-significant endpoints, $p > 0.05$).
4. **Cross-Paper Contradiction Engine**: LangGraph multi-agent synthesis comparing claims across multiple trials (e.g., SGLT2 inhibitors vs Placebo/Insulin therapy).
5. **Persistent Audit History**: Researcher audit sessions and multi-turn chat dialogues stored in PostgreSQL with complete citation tracking.

---

## 📄 License

MIT License — Copyright (c) 2026 VeriNexa Team.
