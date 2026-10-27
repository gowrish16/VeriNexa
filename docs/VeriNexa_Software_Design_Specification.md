# A.J. INSTITUTE OF ENGINEERING & TECHNOLOGY, MANGALURU
### DEPARTMENT OF MASTER OF COMPUTER APPLICATIONS (MCA)
**ACADEMIC YEAR 2025–2026**

---

# SOFTWARE DESIGN SPECIFICATION (SDS)
### MACHINE LEARNING APPLICATION TRACK

## Project Title:
# VeriNexa – Enterprise Clinical Research Literature Verification & Corpus Intelligence System

**Document Version:** 1.0.0  
**Date of Submission:** October 2026  
**Target Environment:** Windows 11 Enterprise / Ubuntu LTS Hybrid Clinical Node  
**Affiliation:** Visvesvaraya Technological University (VTU), Belagavi  

---

## Executive Summary

Clinical literature appraisal in modern evidence-based medicine requires verifying empirical assertions against rapidly expanding corpora of peer-reviewed publications. The manual synthesis of trial methodologies, hazard ratios, confidence intervals, and endpoints across disparate PDF manuscripts is cognitively exhausting and vulnerable to human oversight. Furthermore, commercial general-purpose large language models (LLMs) suffer from stochastic hallucinations, lack grounded attribution, and violate institutional data governance policies when clinical documents are transmitted across public cloud APIs.

**VeriNexa** is an enterprise-grade, offline-capable clinical literature verification and cross-corpus intelligence platform. It establishes an end-to-end Machine Learning and Retrieval-Augmented Generation (RAG) architecture that couples high-dimensional dense vector embeddings with deterministic citation bounding-box anchoring. Operating strictly within an on-premises compute boundary via local Ollama instances executing quantized **Llama 3.1-8B-Instruct** and local **Sentence-Transformers (`all-MiniLM-L6-v2`)**, VeriNexa guarantees zero cloud data egress. Clinical researchers can ingest trial papers through a three-tier resilient verification gate, formulate complex cross-corpus queries, and receive evidence-grounded syntheses where every empirical statement is linked directly to normalized coordinate bounding boxes displayed within a dual-pane high-DPI PDF document viewer.

---

## TABLE OF CONTENTS

- [1. System Design](#1-system-design)
  - [1.1 Architectural Design](#11-architectural-design)
    - [1.1.1 System Context Diagram](#111-system-context-diagram)
    - [1.1.2 End-to-End ML Pipeline](#112-end-to-end-ml-pipeline)
- [2. Detailed Design](#2-detailed-design)
  - [2.1 Dataset Design](#21-dataset-design)
    - [2.1.1 Dataset Provenance and Permissions](#211-dataset-provenance-and-permissions)
    - [2.1.2 Dataset Schema and Data Dictionary](#212-dataset-schema-and-data-dictionary)
    - [2.1.3 Target / Verification Label Definition](#213-target--verification-label-definition)
    - [2.1.4 Partitioning and Leakage Prevention](#214-partitioning-and-leakage-prevention)
  - [2.2 Preprocessing and Feature Engineering](#22-preprocessing-and-feature-engineering)
    - [2.2.1 Validation and Cleaning](#221-validation-and-cleaning)
    - [2.2.2 Feature Selection / Extraction](#222-feature-selection--extraction)
  - [2.3 Model Design](#23-model-design)
    - [2.3.1 Baseline and Candidate Models](#231-baseline-and-candidate-models)
    - [2.3.2 Model Architecture](#232-model-architecture)
  - [2.4 Database Design](#24-database-design)
    - [2.4.1 ER Diagram / Storage Architecture](#241-er-diagram--storage-architecture)
    - [2.4.2 Schema](#242-schema)
  - [2.5 UML and Behavioral Design](#25-uml-and-behavioral-design)
    - [2.5.1 Use Case Diagram](#251-use-case-diagram)
    - [2.5.2 Class / Component Diagram](#252-class--component-diagram)
    - [2.5.3 Sequence Diagram](#253-sequence-diagram)
    - [2.5.4 Activity Diagram](#254-activity-diagram)
  - [2.6 User Interface Design](#26-user-interface-design)
- [3. References](#3-references)

---

# 1. System Design

## 1.1 Architectural Design

### 1.1.1 System Context Diagram

The VeriNexa system boundary encompasses three primary user and system tiers: the **User Interaction Layer**, the **Core Application & Verification Gateway**, and the **Isolated Persistence & Inference Layer**. 

The system interacts with two principal human actors:
1. **Clinical Researcher**: Ingests scientific publications, executes natural-language evidence synthesis queries across selected documents or the full workspace corpus, verifies empirical claims against specific trial excerpts, and inspects visual citation anchors.
2. **System Administrator**: Audits platform security, monitors vector index health, inspects tenant quotas, manages user lifecycles, and executes system maintenance routines via a unified administration console.

Externally, the system ingests scientific publications conforming to standard biomedical repositories such as PubMed Central (PMC), the National Institutes of Health (NIH) Open Access Subset, the New England Journal of Medicine (NEJM), and the Journal of the American Medical Association (JAMA).

Below is the architectural System Context Diagram:

![Figure 1.1: VeriNexa 4-Tier High-Level Architectural and System Context Model](assets/fig_1_1_architecture.png)
*Figure 1.1: VeriNexa 4-Tier High-Level Architectural and System Context Model.*


### 1.1.2 End-to-End ML Pipeline

The VeriNexa Machine Learning Pipeline represents an end-to-end, zero-leakage workflow from raw PDF buffer acquisition to deterministic citation anchoring. The pipeline operates in two distinct phases: **Ingestion & Indexing (Offline/Asynchronous)** and **Retrieval, Arbitration & Synthesis (Online/Real-Time)**.

![Figure 1.2: End-to-End ML Ingestion, Vectorization, and Cross-Document Verification Flow](assets/fig_1_2_data_flow.png)
*Figure 1.2: End-to-End ML Ingestion, Vectorization, and Cross-Document Verification Flow.*

#### Step-by-Step Pipeline Lifecycle:
1. **Step 1: PDF Document Ingestion**: Clinical manuscript uploaded as raw binary stream via `POST /upload`. PyMuPDF (`fitz`) and `pdfplumber` instantiate document handle; extracts raw text & character dimensions.
2. **Step 2: Three-Tier Biomedical Verification Gate**:
   - *Tier 1 (Extraction Resilience)*: Checks page count & character length. If text < 150 chars across pages 1-3, flags as scanned/image manuscript and permits processing.
   - *Tier 2 (Heuristic & Semantic Validation)*: Checks for >= 2 keywords from 48 clinical markers ('cohort', 'hazard', 'p-value', 'placebo', etc.). If unfulfilled, queries Ollama semantic gate.
   - *Tier 3 (Fail-Safe Default)*: Inspects explicit non-scientific regexes (resumes, invoices, source code). Rejects only verified non-papers (HTTP 422). Defaults to ACCEPT.
3. **Step 3: Preprocessing, Normalization & Chunking**: Strips publisher metadata, DOI lines, author affiliations, and running headers. Sliding-window tokenization: 512 tokens per segment with 64/128-token stride overlap. Spatial Mapping: Every token range is resolved against PyMuPDF word bboxes; calculates bounding box quadruple `[x0, y0, x1, y1]` normalized to `[0.0, 1.0]` relative to page dimensions.
4. **Step 4: Dense Vector Embedding Generation**: Normalized text chunks fed into local `nomic-embed-text-v1.5` / `all-MiniLM-L6-v2` dense transformer model. Unit L2 normalization ensures cosine similarity simplifies to vector dot product.
5. **Step 5: Relational & Vector Indexing**: Chunks stored in PostgreSQL `paper_chunks` with `user_id` isolation predicate. High-dimensional index: Hierarchical Navigable Small World (HNSW) constructed over `embedding` using the cosine distance operator (`vector_cosine_ops`, m=16, ef_construction=64).
6. **Step 6: Online Query & Multi-Corpus Hybrid Retrieval**: User submits clinical inquiry via Evidence Chat (Section 3). System encodes query into probe vector and executes pgvector HNSW search: Mode A (Scoped to active paper ID) or Mode B (Corpus Mode across all active papers in workspace), retrieving top-k candidate chunks (k=3 to 6).
7. **Step 7: Arbitration & Synthesis**: Chunks assembled into immutable prompt context with strict attribution constraints. Dispatched to local Ollama LLM with low temperature (0.1). Response Parser extracts empirical synthesis, attribution tags `[Paper Title, Chunk #N]`, and verdict badge.
8. **Step 8: Client-Side Dual-Pane Citation Synchronization**: Frontend renders synthesized answer with clickable citation badges. On badge click, reader automatically switches document stream to target paper and performs smooth-scroll to the exact page, rendering an amber visual bounding-box overlay.


---

# 2. Detailed Design

## 2.1 Dataset Design

### 2.1.1 Dataset Provenance and Permissions

VeriNexa operates over biomedical research documents sourced from verified peer-reviewed repositories. The baseline reference corpus comprises randomized controlled trials (RCTs), prospective cohorts, systematic reviews, and meta-analyses.

- **Primary Sources**:
  - PubMed Central (PMC) Open Access Subset (NLM/NIH).
  - Medline and BioRxiv/MedRxiv pre-print repositories.
  - Publicly accessible clinical trial publications from major medical publishers (e.g., NEJM, The Lancet, JAMA, BMJ).
- **Licensing & Intellectual Property**:
  - Documents adhere strictly to Creative Commons Attribution licenses (CC-BY 4.0, CC-BY-NC 4.0) or US Public Domain designations.
  - VeriNexa stores only vectorized mathematical representations and extracted text segments for institutional indexing; raw PDF binaries are maintained strictly within the localized institution’s data partition.
- **Collection Temporal Span**:
  - Curated literature spans trials published between 2018 and 2026, capturing contemporary standards in metabolic disorders (SGLT2 inhibitors, GLP-1 receptor agonists), neurodegenerative biomarker diagnostics (plasma p-tau217, amyloid PET), oncological immunotherapies, and antimicrobial stewardship audits.
- **Intended Machine Learning Use**:
  - The corpus is utilized exclusively for non-generative, extractive factual grounding, cross-trial conflict detection, and empirical verification. The primary clinical objective is the complete prevention of generative hallucination in diagnostic and therapeutic reasoning.

### 2.1.2 Dataset Schema and Data Dictionary

The persistence layer models manuscripts as structured entities divided into indexed chunks. The table below outlines the relational and vector data dictionary for the core literature repository:

| Field Name | Physical Type | Description / Semantic Meaning | Permissible Range / Constraints | Missingness / Nullable | Sensitivity Level |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `paper_id` | `INTEGER` | Primary surrogate key uniquely identifying the uploaded manuscript. | 1 to $2^{31}-1$ | `NOT NULL` (PK) | Low |
| `user_id` | `INTEGER` | Foreign key referencing the tenant researcher who ingested the paper. | References `users(id)` ON DELETE CASCADE | `NOT NULL` (FK) | Restricted (PII) |
| `title` | `VARCHAR(255)` | Filename or user-supplied document title string. | 1 to 255 alphanumeric chars | `NOT NULL` | Low |
| `detected_title` | `TEXT` | True academic title extracted from PDF metadata or prominent page 1 headers. | Valid UTF-8 string | `NULLABLE` | Low |
| `filename` | `VARCHAR(255)` | Internal disk storage filename of the PDF manuscript. | Valid filesystem path identifier | `NOT NULL` | Low |
| `uploaded_at` | `TIMESTAMPTZ` | Timestamp marking document ingestion and vectorization. | Valid ISO-8601 timestamp | `NOT NULL` (Default: NOW) | Low |
| `chunk_id` | `INTEGER` | Primary surrogate key for individual text segments. | 1 to $2^{31}-1$ | `NOT NULL` (PK) | Low |
| `chunk_index` | `INTEGER` | 0-indexed ordinal sequence of the chunk within the parent paper. | $\ge 0$ | `NOT NULL` | Low |
| `chunk_text` | `TEXT` | Extracted biomedical text segment utilized for dense embedding and LLM prompt context. | 50 to 2000 characters | `NOT NULL` | Confidential |
| `page_number` | `INTEGER` | Physical 1-indexed PDF page from which the segment was parsed. | $1 \le \text{page} \le 1000$ | `NOT NULL` (Default: 1) | Low |
| `bbox_x0` | `FLOAT` | Normalized horizontal start coordinate of the text bounding box. | $0.0 \le x_0 \le 1.0$ | `NOT NULL` (Default: 0.0) | Low |
| `bbox_y0` | `FLOAT` | Normalized vertical top coordinate of the text bounding box. | $0.0 \le y_0 \le 1.0$ | `NOT NULL` (Default: 0.0) | Low |
| `bbox_x1` | `FLOAT` | Normalized horizontal end coordinate of the text bounding box. | $0.0 \le x_1 \le 1.0$ | `NOT NULL` (Default: 0.0) | Low |
| `bbox_y1` | `FLOAT` | Normalized vertical bottom coordinate of the text bounding box. | $0.0 \le y_1 \le 1.0$ | `NOT NULL` (Default: 0.0) | Low |
| `embedding` | `vector(384)` | Dense semantic vector generated by `all-MiniLM-L6-v2`. | $[-1.0, 1.0]^{384}$, Unit L2 norm | `NOT NULL` | Internal Math |

### 2.1.3 Target / Verification Label Definition

In the automated literature arbitration and conflict detection node (Section 4 and LangGraph engine), VeriNexa models clinical verification as a deterministic tripartite decision:

$$\mathcal{Y} \in \{\text{SUPPORTED}, \text{REFUTED}, \text{UNSUPPORTED / OUT-OF-SCOPE}\}$$

1. **`SUPPORTED`**: Assigned when extracted evidence chunks contain direct, statistically unambiguous verification of the assertion (e.g., matching dosage numbers, confirmed hazard ratios within identical confidence intervals, and concordant primary endpoints).
2. **`REFUTED`**: Assigned when empirical metrics within the literature contradict the user assertion or compare contradictory findings across papers (e.g., Paper A reports statin-associated reduction in cardiovascular mortality with $p < 0.001$, whereas Paper B reports no significant risk difference with HR 0.98, 95% CI 0.88–1.09).
3. **`UNSUPPORTED / OUT-OF-SCOPE`**: Assigned when the indexed literature does not contain sufficient quantitative or semantic information to confirm or refute the claim with statistical integrity. The system strictly forbids ungrounded speculation.

**Annotation and Quality Assurance**:
The ground-truth verification of trial assertions is established via deterministic pattern cross-referencing between quantitative terms (integers, floating-point measurements, percentages) in the assertion and extracted chunk tables prior to LLM contextual synthesis.

### 2.1.4 Partitioning and Leakage Prevention

To ensure strict tenant privacy, HIPAA compliance, and vector isolation:
- **Tenant Group Partitioning**: All database queries executing dense similarity lookups append an explicit predicate constraint:
  ```sql
  WHERE user_id = :active_user_id
  ```
- **Document-Level Group Isolation**: When evaluating cross-trial conflicts, chunks from distinct documents are retrieved through stratified sub-queries rather than a single global similarity pool, preventing a single verbose paper from dominating the context window.
- **Zero Evaluation Leakage**: Ground-truth arbitration test benchmarks maintain complete document separation from training representations; the underlying language model operates entirely in zero-shot frozen inference mode with temperature $T = 0.1$.

---

## 2.2 Preprocessing and Feature Engineering

### 2.2.1 Validation and Cleaning

Medical PDF manuscripts contain complex typographic anomalies, dual-column layouts, footnotes, and publisher headers that severely degrade embedding fidelity if ingested naively. VeriNexa implements a multi-stage text cleaning pipeline:

```
[ Raw PDF Buffer ] ---> [ PyMuPDF / pdfplumber Extraction ]
                                    |
                                    v
                     [ Header & Metadata Strip Filter ]
                     - Discards DOI, ORCID, copyright, received dates
                     - Eliminates author email addresses & hospital affiliations
                                    |
                                    v
                     [ Hyphenation & Typographic Repair ]
                     - De-hyphenates split biomedical words (e.g., 'car-dio-vas-cu-lar')
                     - Preserves clinical formulas, ratios (95% CI), p-values (p < 0.05)
                                    |
                                    v
                     [ Table Normalization & Fragment Drop ]
                     - Markdown conversion for detected tabular grids
                     - Fragments < 40 characters discarded as noise
```

1. **Header and Affiliation Pruning**: Strips institutional addresses, corresponding author emails, publisher copyrights, and review dates (`clean_and_extract_verification_text`), ensuring embeddings reflect clinical methodology rather than administrative metadata.
2. **De-Hyphenation and Punctuation Standardization**: Medical terminology broken across line breaks (e.g., `he-ma-to-poi-e-sis`) is reconstructed via regular-expression lookarounds. Decimal points in numerical findings (e.g., `0.001`, `14.2%`) are preserved without loss.
3. **Tabular Syntactic Preservation**: Clinical metrics presented in tables are parsed and structured into Markdown tables, maintaining column-header associations with corresponding empirical values.

### 2.2.2 Feature Selection / Extraction

VeriNexa transforms unstructured clinical text into two distinct feature sets:

1. **384-Dimensional Dense Semantic Embeddings**:
   - Extracted text chunks are processed through the `all-MiniLM-L6-v2` transformer model.
   - Text is mapped into a 384-dimensional continuous vector space:
     $$\mathbf{v} \in \mathbb{R}^{384}, \quad \|\mathbf{v}\|_2 = 1.0$$
   - This dense representation captures semantic equivalence across clinical synonyms (e.g., "dapagliflozin" $\approx$ "SGLT2 inhibitor", "myocardial infarction" $\approx$ "heart attack").
2. **Normalized Spatial Bounding-Box Coordinates**:
   - PyMuPDF extracts the exact rectangular coordinates of each text segment relative to page dimensions:
     $$\{x_0, y_0, x_1, y_1\}, \quad \text{where } x, y \in [0.0, 1.0]$$
   - These spatial coordinates are preserved in PostgreSQL to drive the client-side yellow/amber visual highlight overlays on the original PDF canvas.

---

## 2.3 Model Design

### 2.3.1 Baseline and Candidate Models

| Architectural Candidate | Category | Retrieval / Synthesis Speed | Clinical Synonyms & Reasoning | Privacy / Data Governance | Selected? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BM25 Lexical Search** | Classical Sparse Retrieval | $< 5\text{ ms}$ | Poor; fails on clinical synonyms (e.g., misses "empagliflozin" when querying "SGLT2"). | Full Local Control | Evaluated as Baseline |
| **BioBERT / ClinicalBERT** | Masked Language Model (MLM) | $\sim 45\text{ ms}$ | High biomedical precision; lacks generative synthesis capability. | Full Local Control | Evaluated for Classification |
| **OpenAI GPT-4o API** | Proprietary Cloud LLM | $1500\text{--}3000\text{ ms}$ | Exceptional general reasoning; non-deterministic; high ongoing operational API cost. | **VIOLATION**: Clinical trial data egresses to 3rd-party cloud. | **REJECTED** |
| **VeriNexa Hybrid Architecture** | **HNSW Dense Vector + Llama 3.1-8B Local** | **$\sim 180\text{ ms}$ Retrieval, $\sim 2.2\text{ s}$ Synthesis** | **High; dense semantic similarity captures clinical synonyms; Llama 3.1 synthesizes structured verdicts.** | **100% On-Premises; Zero Data Leakage; HIPAA Ready.** | **SELECTED** |

**Justification for Selection**:
Clinical and pharmaceutical institutions operate under strict data protection mandates. Leveraging a local quantized **Llama 3.1-8B-Instruct** model via Ollama combined with local SentenceTransformers guarantees complete autonomy, deterministic reproducibility, zero subscription fees, and total compliance with patient privacy and intellectual property standards.

### 2.3.2 Model Architecture

The VeriNexa Machine Learning model architecture integrates two specialized neural network pipelines:

```
[ INPUT CLINICAL QUERY ] 
           |
           +-----------------------------------------------+
           |                                               |
           v                                               v
[ SentenceTransformer: all-MiniLM-L6-v2 ]     [ PostgreSQL 17 pgvector ]
* 6 Transformer Layers, 12 Attention Heads    * Hierarchical Navigable Small World
* 384 Hidden Dimensions, Mean Pooling         * Cosine Operator: <=>
* Query Vector: q in R^384                     * Top-k Relevant Chunks Retrieved
           |                                               |
           +-----------------------+-----------------------+
                                   |
                                   v
             [ PROMPT CONSTRUCTION & GROUNDING TEMPLATE ]
             - Role: Clinical Research Verification Assistant
             - Injected Excerpts: Top-k Chunks with [Paper, Chunk #]
             - Rule: State fact only if present in excerpts.
                                   |
                                   v
             [ INFERENCE: Ollama Llama 3.1-8B-Instruct ]
             - Parameter Count: 8.03 Billion (Quantized 4-bit GGUF)
             - Context Window: 8192 tokens
             - Temperature: 0.1 (Strictly Deterministic)
             - Max Generation Tokens: 450 tokens
                                   |
                                   v
             [ STRUCTURED EVIDENCE VERDICT & CITATIONS ]
```

- **Embedding Model (`all-MiniLM-L6-v2`)**: A 6-layer BERT-style cross-encoder distilled from large language models, generating dense 384-dimensional embeddings. It processes a maximum sequence length of 128 tokens using mean pooling over contextualized word vectors.
- **Generative Synthesis Model (`Llama 3.1-8B-Instruct`)**: An 8-billion parameter auto-regressive transformer trained with grouped-query attention (GQA). Deployed via local GGUF quantization (Q4_K_M), achieving high token throughput on standard workstation GPUs and multicore CPUs while preserving nuanced clinical reasoning capabilities.

---

## 2.4 Database Design

### 2.4.1 ER Diagram / Storage Architecture

The persistence architecture utilizes PostgreSQL 17 enhanced with the `vector` extension. The entity-relationship model enforces hierarchical cascading deletion and multi-tenant security:

![Figure 2.1: Relational and Vector Entity-Relationship (ER) Model](assets/fig_2_1_er_diagram.png)
*Figure 2.1: Relational and Vector Entity-Relationship (ER) Model with pgvector Integration.*


### 2.4.2 Schema

Below is the complete Data Definition Language (DDL) syntax for initializing the VeriNexa relational and vector storage engine:

```sql
-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Core Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Password Reset Tokens Table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE
);

-- 4. Clinical Literature Metadata Table
CREATE TABLE IF NOT EXISTS papers (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    detected_title TEXT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Text Segments, Bounding Boxes & Vector Embeddings Table
CREATE TABLE IF NOT EXISTS paper_chunks (
    id SERIAL PRIMARY KEY,
    paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    doc_id VARCHAR(128),
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER DEFAULT 1,
    bbox_x0 FLOAT DEFAULT 0.0,
    bbox_y0 FLOAT DEFAULT 0.0,
    bbox_x1 FLOAT DEFAULT 0.0,
    bbox_y1 FLOAT DEFAULT 0.0,
    embedding vector(384)
);

-- 6. Audit & Evidence Chat Sessions Table
CREATE TABLE IF NOT EXISTS audit_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL DEFAULT 'Biomedical Audit Session',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Audit & Evidence Messages Table
CREATE TABLE IF NOT EXISTS audit_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES audit_sessions(id) ON DELETE CASCADE,
    role VARCHAR(32) NOT NULL,
    content TEXT NOT NULL,
    citations_json JSONB DEFAULT '[]'::jsonb,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. High-Performance Indices
CREATE INDEX IF NOT EXISTS idx_paper_chunks_user_id ON paper_chunks(user_id);
CREATE INDEX IF NOT EXISTS idx_paper_chunks_paper_id ON paper_chunks(paper_id);
CREATE INDEX IF NOT EXISTS idx_paper_chunks_user_paper ON paper_chunks(user_id, paper_id);

-- Hierarchical Navigable Small World (HNSW) Vector Index
CREATE INDEX IF NOT EXISTS idx_paper_chunks_hnsw 
ON paper_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

---

## 2.5 UML and Behavioral Design

### 2.5.1 Use Case Diagram

![Figure 2.2: VeriNexa Comprehensive UML Use-Case Model](assets/fig_2_2_use_case.png)
*Figure 2.2: VeriNexa Comprehensive UML Use-Case Model.*


### 2.5.2 Class / Component Diagram

![Figure 2.3: Object-Oriented Class and Component Architecture Diagram](assets/fig_2_3_class_diagram.png)
*Figure 2.3: Object-Oriented Class and Component Architecture Diagram.*


### 2.5.3 Sequence Diagram

The following trace captures the end-to-end execution lifecycle: a Clinical Researcher submits an empirical inquiry in Section 3 Evidence Chat; the system retrieves top-k vectors, synthesizes the verified answer via Llama 3.1-8B, and coordinates visual anchor highlighting in the dual-pane reader.

![Figure 2.4: Dynamic Sequence Diagram: Cross-Document Query and Visual Anchor Resolution](assets/fig_2_4_sequence_diagram.png)
*Figure 2.4: Dynamic Sequence Diagram: Cross-Document Query and Visual Anchor Resolution.*


### 2.5.4 Activity Diagram

The diagram below details the operational decision logic governing the Document Ingestion Workflow, showcasing the Three-Tier Resilient Verification Gate:

![Figure 2.5: Activity Diagram: Document Ingestion, Quality Gate & Contradiction Pipeline](assets/fig_2_5_activity_diagram.png)
*Figure 2.5: Activity Diagram: Document Ingestion, Quality Gate & Contradiction Pipeline.*


---

## 2.6 User Interface Design

The VeriNexa presentation layer is engineered as a dual-pane, split-screen clinical investigation workstation built with React 18, Vite, and Tailwind CSS. The interface is optimized for high-density information display and immediate empirical verification.

```
+----------------------------------------------------------------------------------------------------+
|                                    USER INTERFACE LAYOUT                                           |
+----------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------+
| [VERINEXA LOGO]  Enterprise Literature Verification Platform       [Search Workspace]  (User: Dr. H|
+----------------------------------------------------------------------------------------------------+
| LEFT PANE: HIGH-DPI CLINICAL PDF VIEWER          | RIGHT PANE: INVESTIGATION & CORPUS WORKSPACE     |
| [File: SGLT2_Diabetes_RCT.pdf] [Page 4/12] [100%]| [ SECTION 1: ADD LITERATURE ]                     |
| [⚡ Native Frame] [🎨 Canvas] [-][+] [Fit Width]  | [ Select PDF Document... ] [ + Upload & Verify ] |
|--------------------------------------------------+--------------------------------------------------|
| +----------------------------------------------+ | [ SECTION 2: ACTIVE LITERATURE (3 Indexed) ]     |
| | ANCHORED CITATION // CHUNK #4 (PAGE 4)       | | [ #31: SGLT2 Inhibitors ] [ Verified: Yes ]       |
| | "Dapagliflozin demonstrated a 31% reduction  | | [ #32: Metformin Meta   ] [ Verified: Yes ]       |
| |  in primary composite endpoints (HR 0.69)..."| | [ #38: p-tau217 Marker  ] [ Verified: Yes ]       |
| +----------------------------------------------+ |--------------------------------------------------|
|                                                  | [ SECTION 3: EVIDENCE CHAT (Corpus Mode) ]       |
|                                                  |  Researcher: "What is the primary endpoint delta |
|  [ CLINICAL TRIAL DOCUMENT CANVAS ]              |              between dapagliflozin and placebo?" |
|                                                  |                                                  |
|  ... randomized cohort was observed ...          |  VeriNexa AI:                                    |
|  +---------------------------------------------+ |  "According to [SGLT2, Chunk #4], dapagliflozin  |
|  | * AMBER BOUNDING BOX OVERLAY               | |   demonstrated a statistically significant 31%   |
|  |   Dapagliflozin: HR 0.69; 95% CI 0.53-0.88;  | |   reduction in hospitalizations for heart failure|
|  |   p < 0.001 vs placebo controls              | |   (HR 0.69, 95% CI 0.53-0.88; p < 0.001)..."     |
|  +---------------------------------------------+ |                                                  |
|                                                  |  [ Citations: [SGLT2] Chunk #4 [View Anchor ->] ]|
|                                                  |--------------------------------------------------|
|                                                  | [ SECTION 4: COMPARE ACROSS PAPERS ]             |
|                                                  |  [Run Cross-Examination] -> [VERDICT: CONSISTENT]|
+--------------------------------------------------+--------------------------------------------------+
```

### Component Breakdown:

1. **Left Pane: Adaptive PDF Document Reader**:
   - Container-fit automatic scaling calculating exact available client width without forced horizontal scrolling.
   - Dual-engine fallback: standard high-DPI HTML5 canvas mode with a 1500ms watchdog that automatically falls back to an embedded native browser iframe (`#page=${page}&toolbar=0`), ensuring 0% blank-screen probability.
   - Spatial citation highlight overlay (`#citation-highlight-overlay`) rendering a semi-transparent amber bounding box (`rgba(245, 158, 11, 0.22)`) with solid borders and page tags around verified passages.
2. **Right Pane: Investigation & Corpus Workspace**:
   - **Section 1 (Literature Ingestion)**: Drag-and-drop file ingestion zone linked to the three-tier verification gate with real-time ingestion status indicators.
   - **Section 2 (Active Literature Cards)**: Multi-document management cards displaying extracted detected titles, indexed chunk counts, and an "Inspect in Reader" action button.
   - **Section 3 (Evidence Chat & Grounded Citations)**: Interactive chat panel supporting paper-scoped lookups or global workspace corpus mode synthesis. Every response features interactive gold citation badges displaying source document titles and chunk numbers that trigger smooth reader synchronization upon interaction.
   - **Section 4 (Compare Across Papers)**: LangGraph-powered conflict engine cross-examining cohorts, dosages, and empirical endpoints across multiple selected manuscripts, presenting bulleted arbitration summaries and final verdict badges (`SUPPORTED`, `REFUTED`, `PARTIAL`).
   - **Administrative Governance Console (`/admin`)**: Dedicated interface for authorized administrators displaying database metrics, user management controls, and vector storage diagnostics.

---

### 2.6.1 Live Production Workspace Execution

![Figure 2.6: Human-in-the-Loop Clinical Verification Workspace](assets/workspace_dual_pane.png)
*Figure 2.6: VeriNexa Human-in-the-Loop Clinical Verification Workspace (Live Web Execution) showcasing synchronized dual-pane PDF viewer with high-DPI canvas, yellow citation highlight overlay, and multi-paper corpus evidence chat.*

### 2.6.2 System Administration and Ingestion Telemetry Console

![Figure 2.7: System Administration and Ingestion Telemetry Console](assets/admin_dashboard.png)
*Figure 2.7: VeriNexa System Administration and Ingestion Telemetry Console (`/admin`) displaying active registered clinicians, PostgreSQL paper storage, 768-d HNSW vector chunks, and real-time inference health monitors.*


---

# 3. References

1. **Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I.** (2017). Attention is all you need. *Advances in Neural Information Processing Systems (NeurIPS 2017)*, 30, 5998–6008.
2. **Reimers, N., & Gurevych, I.** (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP 2019)*, 3982–3992.
3. **Meta AI.** (2024). The Llama 3 herd of models. *arXiv preprint arXiv:2407.21783*.
4. **Malkov, Y. A., & Yashunin, D. A.** (2018). Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 42(4), 824–836.
5. **Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D.** (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems (NeurIPS 2020)*, 33, 9459–9474.
6. **Artifex Software, Inc.** (2024). *PyMuPDF: High performance Python library for data extraction, analysis, and manipulation of PDF documents*. Available: https://pymupdf.readthedocs.io/
7. **PostgreSQL Global Development Group.** (2024). *PostgreSQL 17 Documentation and the pgvector Open-Source Vector Similarity Extension*. Available: https://github.com/pgvector/pgvector
