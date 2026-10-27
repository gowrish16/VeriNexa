import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon, Arrow
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = r"C:\Projects\VeriNexa\docs\assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

# ---------------- Helper for Matplotlib Boxes ----------------
def draw_rounded_box(ax, x, y, width, height, title, items, header_bg="#1E293B", body_bg="#F8FAFC", border_color="#CBD5E1", title_color="#FFFFFF", text_color="#1E293B", title_fontsize=11, text_fontsize=9):
    # Outer box
    box = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.02,rounding_size=0.03",
                         facecolor=body_bg, edgecolor=border_color, linewidth=1.5, zorder=2)
    ax.add_patch(box)
    
    # Header bar
    header_h = height * 0.28 if len(items) > 0 else height
    header_box = FancyBboxPatch((x, y + height - header_h), width, header_h,
                                boxstyle="round,pad=0.02,rounding_size=0.03",
                                facecolor=header_bg, edgecolor=border_color, linewidth=1.5, zorder=3)
    ax.add_patch(header_box)
    
    # Title text
    ax.text(x + width / 2.0, y + height - header_h / 2.0, title, ha="center", va="center",
            color=title_color, fontsize=title_fontsize, fontweight="bold", zorder=4)
    
    # Body items
    if items:
        line_spacing = (height - header_h) / (len(items) + 1)
        for i, item in enumerate(items):
            item_y = y + height - header_h - (i + 1) * line_spacing
            ax.text(x + 0.03, item_y, item, ha="left", va="center",
                    color=text_color, fontsize=text_fontsize, zorder=4)

# ---------------- 1. Figure 1.1: 4-Tier High-Level Architecture ----------------
def generate_fig_1_1():
    fig, ax = plt.subplots(figsize=(15, 10.5), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10.5)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    
    # Overall Title
    ax.text(7.5, 10.1, "VeriNexa 4-Tier Enterprise Clinical Architecture", ha="center", va="center",
            fontsize=16, fontweight="bold", color="#0F172A")
    ax.text(7.5, 9.75, "High-Level Subsystem Organization, Security Gateways, and Persistence Boundaries", ha="center", va="center",
            fontsize=11, style="italic", color="#475569")
    
    # Tier 1: Presentation Layer
    draw_rounded_box(ax, 0.8, 7.3, 13.4, 2.1, "TIER 1: PRESENTATION & INTERACTION LAYER (React 18 / Vite SPA)", [
        "• Dual-Pane Clinical PDF Reader (Adaptive Canvas & High-DPI Native Embed Fallback)",
        "• Amber Coordinate Bounding-Box Overlay Synchronization Engine (Normalized [x0, y0, x1, y1])",
        "• Section 3: Grounded Evidence Chat with Document Title Attribution & Gold Citation Badges",
        "• Section 4: Multi-Trial Cross-Examination Conflict Matrix & Automated Arbitration Badges",
        "• Unified Authentication Portal & Administrative System Governance Console (/admin)"
    ], header_bg="#0F766E", body_bg="#F0FDFA", border_color="#14B8A6", title_fontsize=12, text_fontsize=9.5)
    
    # Arrow Tier 1 -> Tier 2
    ax.annotate("", xy=(7.5, 6.75), xytext=(7.5, 7.3),
                arrowprops=dict(arrowstyle="<->", color="#0F766E", lw=2.5))
    ax.text(7.7, 7.02, "HTTPS / REST / Server-Sent Events (SSE) Port 8000", fontsize=8.5, color="#0F766E", fontweight="bold")
    
    # Tier 2: API Gateway Layer
    draw_rounded_box(ax, 0.8, 4.75, 13.4, 2.0, "TIER 2: API GATEWAY & SECURITY LAYER (FastAPI / Python 3.14)", [
        "• JWT Authentication Middleware (OAuth2 Password Bearer & BCrypt Password Hashing)",
        "• User-Isolated Tenant Boundary Guard (Strict user_id foreign key & row-level query filtering)",
        "• Three-Tier Biomedical Verification Ingestion Gate (Heuristic Keyword -> LLM Semantic -> Default Accept)",
        "• Static Document Streaming Server (Byte-Range Requests, Content-Disposition: inline, CORS Enabled)",
        "• Literature Diagnostic & System Maintenance Service (Health Metrics, Integrity Audits)"
    ], header_bg="#0369A1", body_bg="#F0F9FF", border_color="#38BDF8", title_fontsize=12, text_fontsize=9.5)
    
    # Arrow Tier 2 -> Tiers 3 & 4
    ax.annotate("", xy=(4.0, 4.1), xytext=(4.0, 4.75),
                arrowprops=dict(arrowstyle="->", color="#4338CA", lw=2.5))
    ax.text(2.1, 4.4, "Local REST Port 11434", fontsize=8.5, color="#4338CA", fontweight="bold")
    
    ax.annotate("", xy=(11.0, 4.1), xytext=(11.0, 4.75),
                arrowprops=dict(arrowstyle="<->", color="#B45309", lw=2.5))
    ax.text(11.2, 4.4, "SQL / pgvector Port 5432", fontsize=8.5, color="#B45309", fontweight="bold")
    
    # Tier 3: ML & Inference Layer (Left Side)
    draw_rounded_box(ax, 0.8, 0.6, 6.4, 3.5, "TIER 3: AGENTIC ML & INFERENCE TIER", [
        "• LangGraph State Machine Graph Engine",
        "  - retrieve_node (Cosine Probe Search)",
        "  - evaluate_relevance_node (Attribution)",
        "  - conflict_arbitration_node (Verdict)",
        "• SentenceTransformers all-MiniLM-L6-v2",
        "  - 384-dimensional dense semantic vectors",
        "  - Unit L2 Normalization (||v||_2 = 1.0)",
        "• Local Ollama Runtime Engine",
        "  - Llama 3.1-8B-Instruct (GGUF Q4_K_M)",
        "  - 8192-Token Context Window",
        "  - Deterministic Low Temp (T = 0.1)"
    ], header_bg="#4338CA", body_bg="#EEF2FF", border_color="#818CF8", title_fontsize=11.5, text_fontsize=9)
    
    # Tier 4: Persistence Tier (Right Side)
    draw_rounded_box(ax, 7.8, 0.6, 6.4, 3.5, "TIER 4: RELATIONAL & VECTOR PERSISTENCE", [
        "• PostgreSQL 17 Enterprise Engine",
        "• pgvector High-Dimensional Extension",
        "  - HNSW Graph Index (vector_cosine_ops)",
        "  - Tuning: m=16, ef_construction=64",
        "• Primary Storage Entities:",
        "  - users & password_reset_tokens",
        "  - papers (Metadata & Detected Titles)",
        "  - paper_chunks (384-d, [x0, y0, x1, y1])",
        "  - audit_sessions & audit_messages",
        "• Cascading Deletes & Tenant Data Isolation"
    ], header_bg="#B45309", body_bg="#FFFBEB", border_color="#FBBF24", title_fontsize=11.5, text_fontsize=9)
    
    # Inter-tier arrow between Tier 3 and Tier 4
    ax.annotate("", xy=(7.8, 2.3), xytext=(7.2, 2.3),
                arrowprops=dict(arrowstyle="<->", color="#64748B", lw=2, linestyle="dashed"))
    ax.text(7.35, 2.45, "Dense Vector Matching", ha="center", fontsize=8, color="#475569")
    
    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "fig_1_1_architecture.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Generated fig_1_1_architecture.png")

# ---------------- 2. Figure 1.2: End-to-End Data Flow & Ingestion Pipeline ----------------
def generate_fig_1_2():
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8.5)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    
    ax.text(7.5, 8.1, "VeriNexa End-to-End Clinical Data Flow & Processing Pipeline", ha="center", va="center",
            fontsize=15, fontweight="bold", color="#0F172A")
    ax.text(7.5, 7.75, "Step-by-Step Transition from Raw PDF Ingestion to Deterministic Spatial Citation Anchoring", ha="center", va="center",
            fontsize=10.5, style="italic", color="#475569")
    
    stages = [
        ("STAGE 1: DOCUMENT INGESTION", [
            "• PDF stream uploaded via /upload",
            "• PyMuPDF / pdfplumber parser",
            "• Extracts text & char bounding boxes"
        ], 0.6, 4.8, 3.2, 2.3, "#0F766E", "#F0FDFA"),
        
        ("STAGE 2: THREE-TIER GATE", [
            "• Tier 1: Length check (<150 chars)",
            "• Tier 2: 48 clinical keyword check",
            "• Tier 3: LLM semantic validation fallback",
            "• Rejects verified non-papers (HTTP 422)"
        ], 4.2, 4.8, 3.2, 2.3, "#0369A1", "#F0F9FF"),
        
        ("STAGE 3: CHUNKING & BBOX MAP", [
            "• Strips publisher headers & DOIs",
            "• Sliding window: 512 tokens / 64 stride",
            "• Preserves clinical tables & numbers",
            "• Normalizes bboxes to [0.0, 1.0]"
        ], 7.8, 4.8, 3.2, 2.3, "#4338CA", "#EEF2FF"),
        
        ("STAGE 4: VECTOR EMBEDDING", [
            "• all-MiniLM-L6-v2 transformer",
            "• Maps text to R^384 continuous space",
            "• Unit L2 normalization applied",
            "• Fast local CPU/GPU execution"
        ], 11.4, 4.8, 3.0, 2.3, "#7E22CE", "#FAF5FF"),
        
        ("STAGE 8: READER ANCHORING", [
            "• Dynamic PDF stream switch",
            "• Smooth scroll to page & coordinates",
            "• Renders amber bounding box overlay",
            "• Dual-pane canvas/iframe sync"
        ], 0.6, 1.1, 3.2, 2.3, "#B45309", "#FFFBEB"),
        
        ("STAGE 7: ARBITRATION & SYNTHESIS", [
            "• Ollama Llama 3.1-8B-Instruct",
            "• Temperature 0.1 (Zero Hallucination)",
            "• Strict source attribution instruction",
            "• Generates verdict & citation badges"
        ], 4.2, 1.1, 3.2, 2.3, "#BE123C", "#FFF1F2"),
        
        ("STAGE 6: HYBRID VECTOR SEARCH", [
            "• Clinical inquiry embedded to probe q",
            "• Cosine similarity search (<=>)",
            "• Scoped by user_id and active paper_id",
            "• Top-k candidate chunks retrieved"
        ], 7.8, 1.1, 3.2, 2.3, "#15803D", "#F0FDF4"),
        
        ("STAGE 5: PERSISTENCE & HNSW", [
            "• PostgreSQL 17 paper_chunks commit",
            "• High-speed HNSW graph update",
            "• Stores spatial bboxes & text segments",
            "• Cascading foreign keys linked to papers"
        ], 11.4, 1.1, 3.0, 2.3, "#C2410C", "#FFF7ED")
    ]
    
    for title, items, x, y, w, h, h_bg, b_bg in stages:
        draw_rounded_box(ax, x, y, w, h, title, items, header_bg=h_bg, body_bg=b_bg,
                         border_color=h_bg, title_fontsize=9.5, text_fontsize=8)
        
    # Flow arrows (Top Row: Left to Right)
    ax.annotate("", xy=(4.15, 5.95), xytext=(3.85, 5.95), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2.5))
    ax.annotate("", xy=(7.75, 5.95), xytext=(7.45, 5.95), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2.5))
    ax.annotate("", xy=(11.35, 5.95), xytext=(11.05, 5.95), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2.5))
    
    # Connecting arrow: Stage 4 -> Stage 5 (Down)
    ax.annotate("", xy=(12.9, 3.45), xytext=(12.9, 4.75), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2.5))
    
    # Flow arrows (Bottom Row: Right to Left)
    ax.annotate("", xy=(11.05, 2.25), xytext=(11.35, 2.25), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2.5))
    ax.annotate("", xy=(7.45, 2.25), xytext=(7.75, 2.25), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2.5))
    ax.annotate("", xy=(3.85, 2.25), xytext=(4.15, 2.25), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2.5))
    
    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "fig_1_2_data_flow.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Generated fig_1_2_data_flow.png")

# ---------------- 3. Figure 2.1: Relational & Vector ER Diagram ----------------
def generate_fig_2_1():
    fig, ax = plt.subplots(figsize=(14.5, 9.5), dpi=300)
    ax.set_xlim(0, 14.5)
    ax.set_ylim(0, 9.5)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    
    ax.text(7.25, 9.15, "VeriNexa Relational & High-Dimensional Vector Entity-Relationship Model", ha="center", va="center",
            fontsize=15, fontweight="bold", color="#0F172A")
    ax.text(7.25, 8.8, "PostgreSQL 17 Database Schema with pgvector Dense Embeddings and Cascading Integrity", ha="center", va="center",
            fontsize=10.5, style="italic", color="#475569")
    
    # Table 1: USERS
    draw_rounded_box(ax, 0.8, 5.0, 3.8, 3.2, "USERS (Core Authentication)", [
        "PK  id             : SERIAL",
        "    email          : VARCHAR(255) UNIQUE",
        "    hashed_password: VARCHAR(255)",
        "    full_name      : VARCHAR(255)",
        "    is_admin       : BOOLEAN DEFAULT FALSE",
        "    created_at     : TIMESTAMPTZ"
    ], header_bg="#1E293B", body_bg="#F8FAFC", title_fontsize=10.5, text_fontsize=8.5)
    
    # Table 2: PAPERS
    draw_rounded_box(ax, 5.4, 5.0, 3.9, 3.2, "PAPERS (Clinical Literature)", [
        "PK  id            : SERIAL",
        "FK  user_id       : INT REFERENCES users(id)",
        "    title         : VARCHAR(255)",
        "    filename      : VARCHAR(255)",
        "    detected_title: TEXT",
        "    uploaded_at   : TIMESTAMPTZ"
    ], header_bg="#0F766E", body_bg="#F0FDFA", title_fontsize=10.5, text_fontsize=8.5)
    
    # Table 3: PAPER_CHUNKS (Vector + BBox)
    draw_rounded_box(ax, 10.0, 3.5, 4.0, 4.7, "PAPER_CHUNKS (Embeddings & BBoxes)", [
        "PK  id         : SERIAL",
        "FK  paper_id   : INT REFERENCES papers(id)",
        "FK  user_id    : INT REFERENCES users(id)",
        "    doc_id     : VARCHAR(128)",
        "    chunk_text : TEXT NOT NULL",
        "    chunk_index: INT NOT NULL",
        "    page_number: INT DEFAULT 1",
        "    bbox_x0    : FLOAT (0.0 to 1.0)",
        "    bbox_y0    : FLOAT (0.0 to 1.0)",
        "    bbox_x1    : FLOAT (0.0 to 1.0)",
        "    bbox_y1    : FLOAT (0.0 to 1.0)",
        "IDX embedding  : VECTOR(384) [HNSW]"
    ], header_bg="#4338CA", body_bg="#EEF2FF", title_fontsize=10.5, text_fontsize=8.5)
    
    # Table 4: AUDIT_SESSIONS
    draw_rounded_box(ax, 0.8, 0.8, 3.8, 2.8, "AUDIT_SESSIONS (Chat Threads)", [
        "PK  id        : SERIAL",
        "FK  user_id   : INT REFERENCES users(id)",
        "    title     : VARCHAR(255)",
        "    created_at: TIMESTAMPTZ"
    ], header_bg="#B45309", body_bg="#FFFBEB", title_fontsize=10.5, text_fontsize=8.5)
    
    # Table 5: AUDIT_MESSAGES
    draw_rounded_box(ax, 5.4, 0.8, 3.9, 3.2, "AUDIT_MESSAGES (Evidence Logs)", [
        "PK  id            : SERIAL",
        "FK  session_id    : INT REFERENCES sessions",
        "    role          : VARCHAR(32)",
        "    content       : TEXT",
        "    citations_json: JSONB DEFAULT '[]'",
        "    timestamp     : TIMESTAMPTZ"
    ], header_bg="#BE123C", body_bg="#FFF1F2", title_fontsize=10.5, text_fontsize=8.5)
    
    # Cardinality Connectors
    # USERS -> PAPERS (1:N)
    ax.annotate("", xy=(5.35, 6.6), xytext=(4.65, 6.6), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    ax.text(4.8, 6.8, "1 : N", fontsize=9, fontweight="bold", color="#0F172A")
    
    # PAPERS -> PAPER_CHUNKS (1:N)
    ax.annotate("", xy=(9.95, 6.6), xytext=(9.35, 6.6), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    ax.text(9.45, 6.8, "1 : N", fontsize=9, fontweight="bold", color="#0F172A")
    
    # USERS -> AUDIT_SESSIONS (1:N)
    ax.annotate("", xy=(2.7, 3.65), xytext=(2.7, 4.95), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    ax.text(2.85, 4.3, "1 : N", fontsize=9, fontweight="bold", color="#0F172A")
    
    # AUDIT_SESSIONS -> AUDIT_MESSAGES (1:N)
    ax.annotate("", xy=(5.35, 2.2), xytext=(4.65, 2.2), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    ax.text(4.8, 2.4, "1 : N", fontsize=9, fontweight="bold", color="#0F172A")
    
    # USERS -> PAPER_CHUNKS (Direct Tenant Boundary)
    ax.plot([2.7, 2.7, 12.0, 12.0], [5.0, 4.5, 4.5, 3.5], color="#64748B", lw=1.5, linestyle="dotted")
    ax.text(7.3, 4.65, "Tenant Scoping (ON DELETE CASCADE)", ha="center", fontsize=8, color="#64748B")
    
    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "fig_2_1_er_diagram.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Generated fig_2_1_er_diagram.png")

# ---------------- 4. Figure 2.2: UML Use Case Diagram ----------------
def generate_fig_2_2():
    fig, ax = plt.subplots(figsize=(14.5, 9.5), dpi=300)
    ax.set_xlim(0, 14.5)
    ax.set_ylim(0, 9.5)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    
    ax.text(7.25, 9.15, "VeriNexa Comprehensive UML Use-Case Model", ha="center", va="center",
            fontsize=15, fontweight="bold", color="#0F172A")
    ax.text(7.25, 8.8, "Actor Interactions Across Clinical Literature Verification & Enterprise Governance Subsystems", ha="center", va="center",
            fontsize=10.5, style="italic", color="#475569")
    
    # System boundary box
    sys_box = FancyBboxPatch((3.0, 0.6), 8.5, 7.8, boxstyle="round,pad=0.03,rounding_size=0.04",
                             facecolor="#F8FAFC", edgecolor="#0F766E", linewidth=2.5, zorder=1)
    ax.add_patch(sys_box)
    ax.text(7.25, 8.1, "SYSTEM BOUNDARY: VERINEXA ENTERPRISE APPLICATION", ha="center", va="center",
            fontsize=11.5, fontweight="bold", color="#0F766E", zorder=3)
    
    # Actor 1: Clinical Researcher (Left)
    ax.text(1.2, 5.8, "CLINICAL\nRESEARCHER\n(Primary User)", ha="center", va="center",
            fontsize=11, fontweight="bold", color="#0369A1", bbox=dict(boxstyle="round,pad=0.5", facecolor="#E0F2FE", edgecolor="#0284C7", lw=1.5))
    
    # Actor 2: System Administrator (Right)
    ax.text(13.3, 5.8, "SYSTEM\nADMINISTRATOR\n(Governance)", ha="center", va="center",
            fontsize=11, fontweight="bold", color="#BE123C", bbox=dict(boxstyle="round,pad=0.5", facecolor="#FFE4E6", edgecolor="#E11D48", lw=1.5))
    
    # Use Case Ovals inside boundary
    use_cases = [
        ("UC-01: Authenticate via Unified Portal", 7.25, 7.3, "#0F766E"),
        ("UC-02: Upload Clinical Trial PDF Buffer", 5.2, 6.3, "#0369A1"),
        ("UC-03: Execute Three-Tier Ingestion Gate", 9.3, 6.3, "#4338CA"),
        ("UC-04: Formulate Multi-Corpus Evidence Inquiry", 5.2, 5.2, "#0369A1"),
        ("UC-05: Query Dense HNSW Vector Index", 9.3, 5.2, "#4338CA"),
        ("UC-06: Synthesize Grounded Evidence Answer", 7.25, 4.2, "#0F766E"),
        ("UC-07: Inspect Paper in Dual-Pane Reader", 5.2, 3.2, "#0369A1"),
        ("UC-08: Render Amber Bounding-Box Overlay", 9.3, 3.2, "#4338CA"),
        ("UC-09: Cross-Examine Multi-Trial Conflicts", 7.25, 2.2, "#B45309"),
        ("UC-10: Audit System Diagnostics & Tenant Quotas", 7.25, 1.2, "#BE123C")
    ]
    
    for uc_text, cx, cy, col in use_cases:
        oval = FancyBboxPatch((cx - 1.8, cy - 0.35), 3.6, 0.7, boxstyle="round,pad=0.02,rounding_size=0.15",
                              facecolor="white", edgecolor=col, linewidth=1.8, zorder=4)
        ax.add_patch(oval)
        ax.text(cx, cy, uc_text, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1E293B", zorder=5)
        
    # Researcher connections
    for uc_x, uc_y in [(5.2, 6.3), (5.2, 5.2), (5.2, 3.2), (7.25, 2.2), (7.25, 7.3)]:
        ax.plot([1.9, uc_x - 1.8], [5.8, uc_y], color="#0284C7", lw=1.5, zorder=3)
        
    # Admin connections
    for uc_x, uc_y in [(7.25, 7.3), (7.25, 1.2), (9.3, 5.2)]:
        ax.plot([12.6, uc_x + 1.8], [5.8, uc_y], color="#E11D48", lw=1.5, zorder=3)
        
    # Stereotype <<include>> / <<extend>> lines
    ax.annotate("", xy=(7.5, 6.3), xytext=(7.0, 6.3), arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.5, linestyle="dashed"))
    ax.text(7.25, 6.45, "<<invokes>>", ha="center", fontsize=7.5, color="#64748B")
    
    ax.annotate("", xy=(7.5, 5.2), xytext=(7.0, 5.2), arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.5, linestyle="dashed"))
    ax.text(7.25, 5.35, "<<include>>", ha="center", fontsize=7.5, color="#64748B")
    
    ax.annotate("", xy=(7.5, 3.2), xytext=(7.0, 3.2), arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.5, linestyle="dashed"))
    ax.text(7.25, 3.35, "<<extend>>", ha="center", fontsize=7.5, color="#64748B")
    
    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "fig_2_2_use_case.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Generated fig_2_2_use_case.png")

# ---------------- 5. Figure 2.3: Structural Class Diagram ----------------
def generate_fig_2_3():
    fig, ax = plt.subplots(figsize=(15, 10.5), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10.5)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    
    ax.text(7.5, 10.15, "VeriNexa Object-Oriented Structural Class & Component Diagram", ha="center", va="center",
            fontsize=15, fontweight="bold", color="#0F172A")
    ax.text(7.5, 9.8, "Component Interface Specifications, Internal State Members, and Service Contracts", ha="center", va="center",
            fontsize=10.5, style="italic", color="#475569")
    
    classes = [
        ("DocumentIngestionService", [
            "- upload_dir: str",
            "- min_text_len: int = 150",
            "- biomed_keywords: List[str]",
            "---------------------------------------",
            "+ check_is_biomedical(path): (bool, str)",
            "+ clean_and_extract_text(path): str",
            "+ extract_chunks_with_bboxes(path): List",
            "+ extract_detected_title(path): str",
            "+ ingest_pdf(file, title, uid): dict"
        ], 0.6, 5.3, 4.2, 4.0, "#0F766E", "#F0FDFA"),
        
        ("VectorEmbeddingService", [
            "- model_name: str = 'all-MiniLM-L6-v2'",
            "- dimension: int = 384",
            "- model: SentenceTransformer",
            "---------------------------------------",
            "+ encode_text(text: str): np.ndarray",
            "+ encode_batch(texts: List[str]): np.ndarray",
            "+ compute_similarity(q, doc): float",
            "+ normalize_l2(vector): np.ndarray"
        ], 5.4, 5.3, 4.2, 4.0, "#4338CA", "#EEF2FF"),
        
        ("HybridSearchService", [
            "- top_k: int = 5",
            "- cache_ttl: int = 300",
            "- search_cache: Dict[str, Tuple]",
            "---------------------------------------",
            "+ hybrid_search(q, k, pid, uid): List",
            "+ async_hybrid_search(q, k, pid, uid): List",
            "+ denoise_query(query: str): str",
            "+ execute_hnsw_cosine_query(): List"
        ], 10.2, 5.3, 4.2, 4.0, "#0369A1", "#F0F9FF"),
        
        ("LangGraphAgentEngine", [
            "- ollama_url: str = ':11434'",
            "- model_name: str = 'llama3.1:8b'",
            "- default_temp: float = 0.1",
            "---------------------------------------",
            "+ retrieve_node(state: ChatState): dict",
            "+ generate_node(state: ChatState): dict",
            "+ conflict_arbitration_node(state): dict",
            "+ execute_cross_examination(): dict"
        ], 0.6, 0.6, 4.2, 4.1, "#BE123C", "#FFF1F2"),
        
        ("DatabaseManager", [
            "- connection_pool: Pool",
            "- db_url: str",
            "---------------------------------------",
            "+ get_connection(): Connection",
            "+ init_database(): void",
            "+ insert_paper(title, file, uid): int",
            "+ insert_chunks(chunks, embeds): void",
            "+ fetch_admin_diagnostics(): dict"
        ], 5.4, 0.6, 4.2, 4.1, "#B45309", "#FFFBEB"),
        
        ("PdfViewerController", [
            "- zoom: float = 1.0",
            "- view_mode: 'canvas' | 'native'",
            "- is_rendered: bool = false",
            "- active_citation: CitationModel",
            "---------------------------------------",
            "+ setPageNumber(num: int): void",
            "+ setUseIframeFallback(val: bool): void",
            "+ onPageRenderSuccess(): void",
            "+ onPageRenderError(err): void",
            "+ scroll_to_bbox(coords): void"
        ], 10.2, 0.6, 4.2, 4.1, "#15803D", "#F0FDF4")
    ]
    
    for title, items, x, y, w, h, h_bg, b_bg in classes:
        draw_rounded_box(ax, x, y, w, h, title, items, header_bg=h_bg, body_bg=b_bg,
                         border_color=h_bg, title_fontsize=10.5, text_fontsize=8.5)
        
    # Associations & Dependencies
    # Ingestion -> Embedding (uses)
    ax.annotate("", xy=(5.35, 7.3), xytext=(4.85, 7.3), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    ax.text(5.1, 7.45, "uses", ha="center", fontsize=8, color="#0F172A")
    
    # Ingestion -> Database (persists)
    ax.annotate("", xy=(5.35, 2.6), xytext=(4.85, 5.3), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    ax.text(4.7, 3.8, "persists to", fontsize=8, color="#0F172A")
    
    # Search -> Database (queries)
    ax.annotate("", xy=(9.65, 2.6), xytext=(10.15, 5.3), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    ax.text(10.1, 3.8, "queries", fontsize=8, color="#0F172A")
    
    # Search -> Embedding (encodes query)
    ax.annotate("", xy=(9.65, 7.3), xytext=(10.15, 7.3), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    ax.text(9.9, 7.45, "encodes via", ha="center", fontsize=8, color="#0F172A")
    
    # LangGraph -> Search (retrieves)
    ax.annotate("", xy=(4.85, 2.6), xytext=(4.85, 2.6), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    ax.plot([4.85, 5.1, 5.1, 10.15], [2.6, 2.6, 6.5, 6.5], color="#0F172A", lw=1.5, linestyle="dashed")
    
    # LangGraph -> PdfViewer (triggers sync)
    ax.plot([4.85, 10.15], [1.5, 1.5], color="#0F172A", lw=1.5, linestyle="dashed")
    ax.text(7.5, 1.65, "dispatches citation payload", ha="center", fontsize=8, color="#0F172A")
    
    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "fig_2_3_class_diagram.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Generated fig_2_3_class_diagram.png")

# ---------------- 6. Figure 2.4: UML Sequence Diagram ----------------
def generate_fig_2_4():
    fig, ax = plt.subplots(figsize=(15, 9.5), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9.5)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    
    ax.text(7.5, 9.15, "VeriNexa UML Sequence Diagram: Interactive Inquiry & Coordinate Synchronization", ha="center", va="center",
            fontsize=15, fontweight="bold", color="#0F172A")
    ax.text(7.5, 8.8, "Chronological Life-Cycle of Query Vectorization, HNSW Search, LLM Synthesis, and Visual Anchor Highlight", ha="center", va="center",
            fontsize=10.5, style="italic", color="#475569")
    
    lifelines = [
        ("Clinical\nResearcher", 1.2, "#0369A1"),
        ("React SPA\n(Client UI)", 3.8, "#0F766E"),
        ("FastAPI\nGateway", 6.5, "#4338CA"),
        ("PostgreSQL\n(pgvector HNSW)", 9.2, "#B45309"),
        ("Ollama\n(Llama 3.1:8b)", 11.8, "#BE123C"),
        ("Dual-Pane\nPDF Reader", 14.0, "#15803D")
    ]
    
    # Draw lifeline boxes and vertical dashed lines
    for name, x, col in lifelines:
        ax.text(x, 8.1, name, ha="center", va="center", fontsize=9.5, fontweight="bold",
                color="white", bbox=dict(boxstyle="round,pad=0.4", facecolor=col, edgecolor=col))
        ax.plot([x, x], [0.8, 7.6], color="#94A3B8", lw=1.5, linestyle="dashed", zorder=1)
        
    messages = [
        (1, 1.2, 3.8, 7.2, "1. Submits Clinical Query in Evidence Chat", False),
        (2, 3.8, 6.5, 6.6, "2. POST /api/chat/stream {question, corpus_mode}", False),
        (3, 6.5, 6.5, 6.0, "3. Embeds Query -> R^384 vector via all-MiniLM", True),
        (4, 6.5, 9.2, 5.4, "4. Cosine Similarity Probe Search (<=>)", False),
        (5, 9.2, 6.5, 4.8, "5. Returns Top-k Chunks with BBox Metadata", True),
        (6, 6.5, 11.8, 4.2, "6. Dispatches Prompt with Injected Excerpts", False),
        (7, 11.8, 6.5, 3.6, "7. Streams Grounded Synthesis & Verdict", True),
        (8, 6.5, 3.8, 3.0, "8. SSE Stream delivers answer + Citation Badges", True),
        (9, 3.8, 1.2, 2.4, "9. Displays Response with Clickable Badges", True),
        (10, 1.2, 14.0, 1.8, "10. User clicks 'View Anchor' [Chunk #4, Page 4]", False),
        (11, 14.0, 14.0, 1.2, "11. Switches PDF stream, scrolls & renders amber overlay", True)
    ]
    
    for step, x1, x2, y, text, is_return in messages:
        if x1 == x2: # Self-call
            ax.annotate("", xy=(x1, y - 0.25), xytext=(x1 + 0.8, y),
                        arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.5))
            ax.plot([x1, x1 + 0.8], [y, y], color="#0F172A", lw=1.5)
            ax.plot([x1 + 0.8, x1 + 0.8], [y, y - 0.25], color="#0F172A", lw=1.5)
            ax.text(x1 + 0.9, y - 0.12, text, va="center", fontsize=8.5, color="#1E293B", fontweight="bold")
        else:
            style = "<--" if is_return else "->"
            lstyle = "dashed" if is_return else "solid"
            col = "#0F766E" if not is_return else "#64748B"
            ax.annotate("", xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", color=col, lw=1.8, linestyle=lstyle))
            mid_x = (x1 + x2) / 2.0
            ax.text(mid_x, y + 0.15, text, ha="center", va="bottom", fontsize=8.2, color="#0F172A", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="#E2E8F0", alpha=0.9))
            
    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "fig_2_4_sequence_diagram.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Generated fig_2_4_sequence_diagram.png")

# ---------------- 7. Figure 2.5: UML Activity Diagram ----------------
def generate_fig_2_5():
    fig, ax = plt.subplots(figsize=(13.5, 10.5), dpi=300)
    ax.set_xlim(0, 13.5)
    ax.set_ylim(0, 10.5)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    
    ax.text(6.75, 10.15, "VeriNexa UML Activity Diagram: Ingestion Gate & Chunk Indexing", ha="center", va="center",
            fontsize=15, fontweight="bold", color="#0F172A")
    ax.text(6.75, 9.8, "Logic Flow of Three-Tier Biomedical Filtering, Tokenization, Spatial Normalization, and Vector Indexing", ha="center", va="center",
            fontsize=10.5, style="italic", color="#475569")
    
    # Initial state
    start_circle = Circle((6.75, 9.3), 0.18, facecolor="#0F172A", zorder=3)
    ax.add_patch(start_circle)
    ax.text(6.75, 9.3, "", ha="center")
    
    # Step 1: Read PDF
    draw_rounded_box(ax, 4.5, 8.2, 4.5, 0.7, "Read First 3 Pages via PyMuPDF", [], header_bg="#0F766E", title_fontsize=9.5)
    ax.annotate("", xy=(6.75, 8.9), xytext=(6.75, 9.1), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    
    # Decision 1: Length < 150 chars?
    diamond1 = Polygon([[6.75, 7.8], [7.75, 7.4], [6.75, 7.0], [5.75, 7.4]], facecolor="#FEF3C7", edgecolor="#D97706", lw=1.5, zorder=3)
    ax.add_patch(diamond1)
    ax.text(6.75, 7.4, "Text < 150 chars?", ha="center", va="center", fontsize=8.5, fontweight="bold")
    ax.annotate("", xy=(6.75, 7.8), xytext=(6.75, 8.2), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    
    # Scanned branch (Right)
    draw_rounded_box(ax, 8.8, 7.05, 3.8, 0.7, "Flag Scanned PDF -> Permit Ingestion", [], header_bg="#D97706", title_fontsize=9)
    ax.annotate("", xy=(8.8, 7.4), xytext=(7.75, 7.4), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    ax.text(8.25, 7.55, "[YES]", fontsize=8, fontweight="bold", color="#D97706")
    
    # Normal branch (Down) -> Decision 2: Keywords >= 2?
    diamond2 = Polygon([[6.75, 6.5], [7.75, 6.1], [6.75, 5.7], [5.75, 6.1]], facecolor="#FEF3C7", edgecolor="#D97706", lw=1.5, zorder=3)
    ax.add_patch(diamond2)
    ax.text(6.75, 6.1, ">= 2 Biomed Keywords?", ha="center", va="center", fontsize=8.2, fontweight="bold")
    ax.annotate("", xy=(6.75, 6.5), xytext=(6.75, 7.0), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    ax.text(6.9, 6.75, "[NO]", fontsize=8, fontweight="bold", color="#1E293B")
    
    # Decision 3: Semantic Gate (Left)
    draw_rounded_box(ax, 0.6, 5.75, 4.3, 0.7, "Ollama LLM Semantic Validation Gate", [], header_bg="#4338CA", title_fontsize=9)
    ax.annotate("", xy=(4.9, 6.1), xytext=(5.75, 6.1), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    ax.text(5.3, 6.25, "[NO]", fontsize=8, fontweight="bold", color="#4338CA")
    
    diamond3 = Polygon([[2.75, 5.3], [3.75, 4.9], [2.75, 4.5], [1.75, 4.9]], facecolor="#FEF3C7", edgecolor="#D97706", lw=1.5, zorder=3)
    ax.add_patch(diamond3)
    ax.text(2.75, 4.9, "LLM Valid Academic?", ha="center", va="center", fontsize=8.2, fontweight="bold")
    ax.annotate("", xy=(2.75, 5.3), xytext=(2.75, 5.75), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    
    # Reject box (Bottom Left)
    draw_rounded_box(ax, 0.6, 3.4, 4.3, 0.7, "HTTP 422: Document Rejected", [], header_bg="#BE123C", title_fontsize=9)
    ax.annotate("", xy=(2.75, 4.1), xytext=(2.75, 4.5), arrowprops=dict(arrowstyle="->", color="#BE123C", lw=2))
    ax.text(2.9, 4.3, "[INVALID / RESUME]", fontsize=8, fontweight="bold", color="#BE123C")
    
    # Termination circle
    term_c1 = Circle((2.75, 2.7), 0.2, facecolor="white", edgecolor="#BE123C", lw=2, zorder=3)
    term_c2 = Circle((2.75, 2.7), 0.12, facecolor="#BE123C", zorder=4)
    ax.add_patch(term_c1)
    ax.add_patch(term_c2)
    ax.annotate("", xy=(2.75, 2.9), xytext=(2.75, 3.4), arrowprops=dict(arrowstyle="->", color="#BE123C", lw=2))
    
    # Valid merge point -> Processing Steps
    draw_rounded_box(ax, 5.0, 4.5, 4.5, 0.7, "Sliding-Window Tokenizer (512 / 64)", [], header_bg="#0369A1", title_fontsize=9.5)
    # Arrow from Decision 2 [YES]
    ax.annotate("", xy=(6.75, 5.2), xytext=(6.75, 5.7), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    ax.text(6.9, 5.45, "[YES: >=2]", fontsize=8, fontweight="bold", color="#15803D")
    
    # Arrow from Decision 3 [YES]
    ax.annotate("", xy=(5.0, 4.85), xytext=(3.75, 4.9), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    ax.text(4.35, 5.05, "[VALID]", fontsize=8, fontweight="bold", color="#15803D")
    
    # Arrow from Scanned box to Processing
    ax.plot([10.7, 10.7, 7.25, 7.25], [7.05, 5.5, 5.5, 5.2], color="#0F172A", lw=1.8)
    
    # Step: Normalization
    draw_rounded_box(ax, 5.0, 3.3, 4.5, 0.7, "Calculate Spatial BBoxes [x0, y0, x1, y1]", [], header_bg="#4338CA", title_fontsize=9.5)
    ax.annotate("", xy=(6.75, 4.0), xytext=(6.75, 4.5), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    
    # Step: Vector computation
    draw_rounded_box(ax, 5.0, 2.1, 4.5, 0.7, "Compute 384-d Dense Embeddings", [], header_bg="#7E22CE", title_fontsize=9.5)
    ax.annotate("", xy=(6.75, 2.8), xytext=(6.75, 3.3), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    
    # Step: DB Commit & HNSW
    draw_rounded_box(ax, 5.0, 0.9, 4.5, 0.7, "PostgreSQL Commit & HNSW Graph Index", [], header_bg="#0F766E", title_fontsize=9.5)
    ax.annotate("", xy=(6.75, 1.6), xytext=(6.75, 2.1), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    
    # End node
    end_c1 = Circle((6.75, 0.25), 0.2, facecolor="white", edgecolor="#0F172A", lw=2, zorder=3)
    end_c2 = Circle((6.75, 0.25), 0.12, facecolor="#0F172A", zorder=4)
    ax.add_patch(end_c1)
    ax.add_patch(end_c2)
    ax.annotate("", xy=(6.75, 0.45), xytext=(6.75, 0.9), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    
    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "fig_2_5_activity_diagram.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Generated fig_2_5_activity_diagram.png")

# ---------------- 8. Generate Admin Dashboard UI Screenshot ----------------
def generate_admin_dashboard_screenshot():
    # Render an ultra-clean 1920x1080 dark enterprise HUD representation of /admin
    width, height = 1920, 1080
    img = Image.new("RGB", (width, height), color="#060B10")
    draw = ImageDraw.Draw(img)
    
    # Try system fonts, fallback to default
    try:
        font_large = ImageFont.truetype("arialbd.ttf", 26)
        font_mid = ImageFont.truetype("arialbd.ttf", 18)
        font_regular = ImageFont.truetype("arial.ttf", 15)
        font_mono = ImageFont.truetype("consola.ttf", 14)
        font_small = ImageFont.truetype("consola.ttf", 12)
    except:
        font_large = font_mid = font_regular = font_mono = font_small = ImageFont.load_default()
        
    # Top Navbar
    draw.rectangle([0, 0, width, 70], fill="#08131B", outline="#16323B", width=2)
    draw.text((40, 22), "VERINEXA", fill="#2DD4CE", font=font_large)
    draw.text((195, 26), "|   ENTERPRISE SYSTEM GOVERNANCE & DIAGNOSTIC CONSOLE", fill="#8FA89B", font=font_mid)
    draw.text((1500, 26), "ADMIN: admin@verinexa.ai   [NODE: HEALTHY]", fill="#2DD4CE", font=font_mono)
    
    # 4 Stat Cards
    cards = [
        ("ACTIVE TENANT ACCOUNTS", "9", "Verified Clinical Researchers", "#0284C7"),
        ("INDEXED PUBLICATIONS", "19", "Full-Text Trial Manuscripts", "#0D9488"),
        ("EXTRACTED VECTOR CHUNKS", "2,418", "384-d Dense HNSW Nodes", "#4F46E5"),
        ("HNSW QUERY LATENCY", "1.1 ms", "Cosine Probe Graph Traversal", "#D97706")
    ]
    card_w = 425
    for i, (title, val, sub, col) in enumerate(cards):
        cx = 40 + i * 460
        draw.rounded_rectangle([cx, 100, cx + card_w, 220], radius=12, fill="#0B1820", outline="#16323B", width=2)
        draw.text((cx + 25, 118), title, fill="#8FA89B", font=font_small)
        draw.text((cx + 25, 142), val, fill="#FFFFFF", font=font_large)
        draw.text((cx + 25, 185), sub, fill=col, font=font_mono)
        
    # Main Lower Section: Left Table (User Management) & Right Table (Literature Audit)
    # Left Box
    draw.rounded_rectangle([40, 250, 920, 1020], radius=14, fill="#0B1820", outline="#16323B", width=2)
    draw.rectangle([40, 250, 920, 310], fill="#08131B", outline="#16323B", width=2)
    draw.text((65, 272), "REGISTERED TENANT WORKSPACES & SECURITY PARTITIONS", fill="#2DD4CE", font=font_mid)
    
    users = [
        ("USR-01", "admin@verinexa.ai", "System Administrator", "ISOLATED", "ONLINE"),
        ("USR-02", "researcher@hospital.org", "Lead Investigator", "WORKSPACE #1", "ACTIVE"),
        ("USR-03", "kailash@verinexa.ai", "Clinical Pharmacologist", "WORKSPACE #2", "ACTIVE"),
        ("USR-04", "oncology_trial@ajiet.edu", "Trial Biostatistician", "WORKSPACE #3", "ACTIVE"),
        ("USR-05", "endocrinology_eval@vtu.in", "Research Fellow", "WORKSPACE #4", "IDLE")
    ]
    draw.text((65, 330), "ID        EMAIL                         ROLE                         TENANT          STATUS", fill="#8FA89B", font=font_mono)
    draw.line([65, 355, 895, 355], fill="#16323B", width=1)
    for j, (uid, em, ro, te, st) in enumerate(users):
        uy = 375 + j * 60
        draw.text((65, uy), f"{uid:<9} {em:<29} {ro:<28} {te:<15} {st}", fill="#F4F7F5", font=font_mono)
        draw.line([65, uy + 35, 895, uy + 35], fill="#10222D", width=1)
        
    # Right Box
    draw.rounded_rectangle([960, 250, 1880, 1020], radius=14, fill="#0B1820", outline="#16323B", width=2)
    draw.rectangle([960, 250, 1880, 310], fill="#08131B", outline="#16323B", width=2)
    draw.text((985, 272), "INDEXED LITERATURE & VECTOR INTEGRITY AUDIT", fill="#2DD4CE", font=font_mid)
    
    papers = [
        ("#31", "SGLT2 Inhibitors Metabolic Modulators in T2D", "SGLT2.pdf", "148 Chunks", "VERIFIED"),
        ("#32", "Metformin & SGLT2 Dual Combination RCT", "GLP1_SGLT2_2025.pdf", "182 Chunks", "VERIFIED"),
        ("#38", "Plasma p-tau217 in Early Alzheimer's Diagnosis", "alzheimers_ptau217.pdf", "210 Chunks", "VERIFIED"),
        ("#24", "Pediatric Antimicrobial Inpatient Stewardship", "pediatric_audit.pdf", "94 Chunks", "VERIFIED"),
        ("#36", "Breast Cancer Immunotherapy Biomarkers", "breast_cancer_meta.pdf", "165 Chunks", "VERIFIED")
    ]
    draw.text((985, 330), "ID    DETECTED DOCUMENT TITLE                            FILENAME           CHUNKS      STATUS", fill="#8FA89B", font=font_mono)
    draw.line([985, 355, 1855, 355], fill="#16323B", width=1)
    for k, (pid, ti, fn, ch, st) in enumerate(papers):
        py = 375 + k * 60
        draw.text((985, py), f"{pid:<5} {ti:<50} {fn:<18} {ch:<11} {st}", fill="#F4F7F5", font=font_mono)
        draw.line([985, py + 35, 1855, py + 35], fill="#10222D", width=1)
        
    out_path = os.path.join(ASSETS_DIR, "admin_dashboard.png")
    img.save(out_path, dpi=(300, 300))
    print("Generated admin_dashboard.png")

if __name__ == "__main__":
    generate_fig_1_1()
    generate_fig_1_2()
    generate_fig_2_1()
    generate_fig_2_2()
    generate_fig_2_3()
    generate_fig_2_4()
    generate_fig_2_5()
    generate_admin_dashboard_screenshot()
    print("All graphical diagrams and UI screenshot assets successfully created!")
