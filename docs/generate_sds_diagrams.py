"""
High-Resolution Diagram Generation Script for VeriNexa Software Design Specification (SDS)
Generates 300-DPI vector-quality PNG images conforming to the soft-blue box aesthetic
(Fill: #E8EFF8, Border: #2B4C7E, Text: #111111, Arrows: #2B4C7E)
Matching Figures 1 to 8 of the AJIET Reference SDS PDF with exact alignment fixes.
"""

import os
import tempfile
os.environ['MPLCONFIGDIR'] = os.path.join(tempfile.gettempdir(), 'mpl_cache')

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Global font & DPI configuration for crisp 300 DPI rendering
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

ASSETS_DIR = r"C:\Projects\VeriNexa\docs\assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

# Aesthetic constants matching reference
COLOR_BOX_FILL = "#E8EFF8"
COLOR_BOX_BORDER = "#2B4C7E"
COLOR_CONTAINER_FILL = "#F8FAFC"
COLOR_CONTAINER_BORDER = "#94A3B8"
COLOR_TEXT_MAIN = "#111111"
COLOR_TEXT_TITLE = "#1F3864"
COLOR_ARROW = "#2B4C7E"

def draw_box(ax, x, y, w, h, title="", text="", radius=0.1, fontsize=9.5, title_size=10.5, box_fill=COLOR_BOX_FILL, box_border=COLOR_BOX_BORDER):
    """Draws a rounded soft-blue box with clean centered title and descriptive text."""
    box = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.05,rounding_size={radius}",
        facecolor=box_fill,
        edgecolor=box_border,
        linewidth=1.8,
        zorder=2
    )
    ax.add_patch(box)
    
    if title and text:
        ax.text(x + w/2, y + h*0.70, title, ha='center', va='center', fontsize=title_size, fontweight='bold', color=COLOR_TEXT_TITLE, zorder=3)
        ax.text(x + w/2, y + h*0.36, text, ha='center', va='center', fontsize=fontsize, color=COLOR_TEXT_MAIN, zorder=3)
    elif title:
        ax.text(x + w/2, y + h/2, title, ha='center', va='center', fontsize=title_size, fontweight='bold', color=COLOR_TEXT_TITLE, zorder=3)
    elif text:
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fontsize, color=COLOR_TEXT_MAIN, zorder=3)

def draw_arrow(ax, start, end, label="", label_pos=0.5, label_offset=(0, 0.2), style="-|>", lw=1.8, color=COLOR_ARROW):
    """Draws a crisp directional arrow with optional text label."""
    arrow = patches.FancyArrowPatch(
        start, end,
        arrowstyle=style,
        mutation_scale=16,
        color=color,
        linewidth=lw,
        zorder=4
    )
    ax.add_patch(arrow)
    if label:
        lx = start[0] + (end[0] - start[0]) * label_pos + label_offset[0]
        ly = start[1] + (end[1] - start[1]) * label_pos + label_offset[1]
        ax.text(lx, ly, label, ha='center', va='center', fontsize=8.5, color=COLOR_TEXT_TITLE, fontweight='bold', zorder=5,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFFFFF', edgecolor='#CBD5E1', alpha=0.95))

# ==============================================================================
# FIGURE 1: SYSTEM CONTEXT DIAGRAM (CLEANLY SEPARATED FEEDBACK ARROWS)
# ==============================================================================
def generate_figure_1():
    fig, ax = plt.subplots(figsize=(11, 8.5), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    # Top Actor
    draw_box(ax, 3.8, 7.2, 3.4, 0.9, title="Clinical Researcher / Auditor", text="Ingests Papers, Inquires, Verifies", radius=0.12)

    # Middle Row: Frontend & Backend Gateway
    draw_box(ax, 0.8, 4.7, 3.2, 1.5, title="React 19 Frontend", text="Dual-Pane PDF Document Reader\nAmber BBox Citation Overlays\nCorpus Evidence Chat Interface", radius=0.12)
    draw_box(ax, 7.0, 4.7, 3.3, 1.5, title="FastAPI Application Gateway", text="3-Tier Biomedical Verification Gate\nJWT Security & User Isolation\nRAG Pipeline & LangGraph Nodes", radius=0.12)

    # Bottom Row: Inference & Database
    draw_box(ax, 0.8, 1.3, 3.8, 1.8, title="Local ML Inference Tier", text="PyMuPDF Point Geometry Extractor\nall-MiniLM-L6-v2 (384-d Dense Vectorizer)\nOllama Local Llama 3.1-8B-Instruct\nZero Cloud Data Transmission", radius=0.12)
    draw_box(ax, 6.5, 1.3, 3.8, 1.8, title="PostgreSQL 17 + pgvector Tier", text="papers & detected_titles metadata\npaper_chunks (384-d float embeddings)\nHNSW Cosine Distance Vector Index\nAudit Sessions & Message History", radius=0.12)

    # External Data Source
    draw_box(ax, 4.2, 0.1, 2.6, 0.8, title="Clinical Data Repositories", text="PubMed Central, ClinicalTrials.gov", radius=0.08, box_fill="#F1F5F9", box_border="#64748B")

    # Arrows 1 & 8: User Interactions
    draw_arrow(ax, (4.2, 7.2), (1.8, 6.2), label="1. Ingest Literature & Inquire", label_pos=0.45, label_offset=(-0.75, 0.2))
    draw_arrow(ax, (3.2, 6.2), (5.8, 7.2), label="8. View Anchored PDF Citations", label_pos=0.55, label_offset=(0.75, 0.2))
    
    # Arrows 2 & 7: Frontend <-> Gateway
    draw_arrow(ax, (4.0, 5.6), (7.0, 5.6), label="2. REST API / SSE", label_offset=(0, 0.22))
    draw_arrow(ax, (7.0, 4.95), (4.0, 4.95), label="7. Synthesized Answer & Badges", label_offset=(0, -0.22))

    # Arrow 3: FastAPI Gateway -> ML Tier (Inference Dispatch)
    draw_arrow(ax, (7.1, 4.7), (4.3, 3.1), label="3. Embed & Inference", label_pos=0.35, label_offset=(-0.35, 0.35))

    # Arrow 6: ML Tier -> FastAPI Gateway (Grounded Synthesis Feedback)
    # Originates at lower right of ML tier to completely decouple trajectory from Arrow 3
    draw_arrow(ax, (4.3, 2.1), (7.1, 4.7), label="6. Grounded Synthesis", label_pos=0.55, label_offset=(0.55, -0.35))

    # Arrow 4: FastAPI Gateway -> PostgreSQL (HNSW Vector Query)
    draw_arrow(ax, (8.0, 4.7), (8.0, 3.1), label="4. HNSW Vector Query", label_offset=(-1.15, 0))

    # Arrow 5: PostgreSQL -> FastAPI Gateway (Top-k Chunks Response)
    draw_arrow(ax, (9.6, 3.1), (9.6, 4.7), label="5. Top-k Chunks", label_offset=(0.95, 0))

    # External Data Arrow
    draw_arrow(ax, (5.5, 0.9), (7.5, 1.3), label="Open Access PDFs", label_offset=(0, 0.2))

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "sds_fig1_system_context.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated:", out_path)

# ==============================================================================
# FIGURE 2: END-TO-END ML PIPELINE
# ==============================================================================
def generate_figure_2():
    fig, ax = plt.subplots(figsize=(11, 9.5), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 9.5)
    ax.axis('off')

    stages = [
        ("Step 1: Clinical PDF Upload", "User drops trial manuscript via Web UI", 8.4),
        ("Step 2: 3-Tier Verification Gate", "Resilience -> 48 Clinical Markers -> Non-Scientific Regex", 7.2),
        ("Step 3: Text Cleaning & Normalization", "Ligatures resolved, de-hyphenated, running headers stripped", 6.0),
        ("Step 4: Spatial BBox Token Chunking", "512 tokens / 64 overlap; normalized [x0, y0, x1, y1] coordinates", 4.8),
        ("Step 5: Dense Vector Embedding", "all-MiniLM-L6-v2 model generates 384-dimensional dense vectors", 3.6),
        ("Step 6: pgvector HNSW Graph Indexing", "Hierarchical Navigable Small World index with cosine distance", 2.4),
        ("Step 7: Arbitration & LLM Synthesis", "Local Llama 3.1-8B-Instruct evaluates premise-hypothesis pairs", 1.2),
        ("Step 8: Dual-Pane Verified Display", "Amber visual highlight overlay & grounded citation badges", 0.0)
    ]

    for idx, (title, desc, y) in enumerate(stages):
        draw_box(ax, 2.2, y, 6.6, 0.85, title=title, text=desc, radius=0.08)
        if idx < len(stages) - 1:
            draw_arrow(ax, (5.5, y), (5.5, y - 0.35), lw=2.0)

    # Side Indicators
    ax.text(1.2, 7.8, "INGESTION &\nINDEXING\nPHASE\n(Offline / Async)", ha='center', va='center', fontsize=10, fontweight='bold', color="#2B4C7E",
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#F8FAFC', edgecolor='#94A3B8', linestyle='--'))
    ax.text(1.2, 1.8, "QUERY &\nARBITRATION\nPHASE\n(Online / Real-time)", ha='center', va='center', fontsize=10, fontweight='bold', color="#2B4C7E",
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#F8FAFC', edgecolor='#94A3B8', linestyle='--'))

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "sds_fig2_ml_pipeline.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated:", out_path)

# ==============================================================================
# FIGURE 3: MODEL ARCHITECTURE (FIXED FORMULA & CLEAN MULTI-LINE RENDERING)
# ==============================================================================
def generate_figure_3():
    fig, ax = plt.subplots(figsize=(11, 8.5), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    # Input Box
    draw_box(ax, 3.2, 7.2, 4.6, 1.0, title="Input Assertion & Evidence Chunks", text="Clinical Inquiry: 'Dapagliflozin reduces mortality by 31%'\nCandidate Chunks from pgvector HNSW Search", radius=0.1)

    # Embedding Vectorizer
    draw_box(ax, 0.6, 4.9, 4.5, 1.5, title="Embedding Model (all-MiniLM-L6-v2)", text="6-Layer MiniLM Distilled Architecture\nMean-pooling contextualized representations\nOutputs 384-dimensional dense float32 vector", radius=0.1)

    # pgvector Cosine Search (Clean formula formatted with zero truncation)
    draw_box(ax, 5.7, 4.9, 4.8, 1.5, title="pgvector HNSW Cosine Index", 
             text="Sub-15ms nearest neighbor probe\nCosine Distance: d = 1 - (u · v) / (||u|| ||v||)\nRetrieves Top-k Candidate Chunks", radius=0.1, fontsize=9.2)

    # LLM Reasoning Engine
    draw_box(ax, 2.5, 2.7, 6.0, 1.5, title="Local Generative Engine (Llama 3.1-8B-Instruct)", text="Quantized 4-bit GGUF Model via Ollama\nContext Window: 8,192 tokens | Temperature: 0.1 (Strict Grounding)\nEvaluates Premise-Hypothesis Logical Entailment", radius=0.12)

    # Tripartite Classification Output
    draw_box(ax, 0.6, 0.4, 3.0, 1.3, title="VERDICT: SUPPORTED", text="Claim affirmed by excerpt\nMatching endpoints & cohorts\nHigh confidence (>95%)", radius=0.08, box_fill="#E6F4EA", box_border="#137333")
    draw_box(ax, 4.0, 0.4, 3.0, 1.3, title="VERDICT: REFUTED", text="Statistical conflict found\nConflicting hazard ratio / p-val\nDiscrepancy report flagged", radius=0.08, box_fill="#FCE8E6", box_border="#C5221F")
    draw_box(ax, 7.4, 0.4, 3.0, 1.3, title="UNSUPPORTED / OOS", text="Insufficient trial context\nNeutral / unverified finding\nPrompts additional papers", radius=0.08, box_fill="#FEF7E0", box_border="#B06000")

    # Arrows
    draw_arrow(ax, (5.5, 7.2), (3.0, 6.4), label="Tokenize", label_pos=0.5, label_offset=(-0.4, 0.1))
    draw_arrow(ax, (5.1, 5.65), (5.7, 5.65), label="384-d Vector", label_offset=(0, 0.2))
    draw_arrow(ax, (8.0, 4.9), (6.5, 4.2), label="Top-k Chunks Context", label_offset=(0.85, 0.1))
    draw_arrow(ax, (5.5, 2.7), (2.1, 1.7), label="Affirms", label_offset=(-0.4, 0))
    draw_arrow(ax, (5.5, 2.7), (5.5, 1.7), label="Contradicts", label_offset=(0.6, 0))
    draw_arrow(ax, (5.5, 2.7), (8.9, 1.7), label="Neutral", label_offset=(0.4, 0))

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "sds_fig3_model_architecture.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated:", out_path)

# ==============================================================================
# FIGURE 4: FORMAL RELATIONAL & VECTOR ENTITY-RELATIONSHIP (ER) MODEL
# ==============================================================================
def draw_er_entity(ax, x, y, w, h, entity_name, attributes, pk_indices=[0], fk_indices=[], vec_indices=[]):
    """Draws a standard Relational/Chen entity box with a distinct header compartment."""
    header_h = 0.44
    box = patches.FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.06',
                                facecolor='#FFFFFF', edgecolor='#1F3864', linewidth=1.6, zorder=2)
    ax.add_patch(box)
    hdr = patches.FancyBboxPatch((x, y + h - header_h), w, header_h, boxstyle='round,pad=0.02,rounding_size=0.06',
                                facecolor='#1F3864', edgecolor='#1F3864', linewidth=1.4, zorder=3)
    ax.add_patch(hdr)
    ax.text(x + w/2, y + h - header_h/2, entity_name, ha='center', va='center',
            fontsize=9.0, fontweight='bold', color='#FFFFFF', zorder=4)
    ax.plot([x, x + w], [y + h - header_h, y + h - header_h], color='#1F3864', linewidth=1.2, zorder=4)
    
    attr_y = y + h - header_h - 0.20
    for idx, attr in enumerate(attributes):
        color = '#111111'
        weight = 'normal'
        if idx in pk_indices:
            weight = 'bold'
            color = '#991B1B' # dark red for PK
        elif idx in fk_indices:
            weight = 'bold'
            color = '#1E40AF' # dark blue for FK
        elif idx in vec_indices:
            weight = 'bold'
            color = '#065F46' # emerald for Vector
        ax.text(x + 0.12, attr_y, attr, ha='left', va='center', fontsize=7.8, fontweight=weight, color=color, zorder=4)
        attr_y -= 0.23

def draw_diamond(ax, x, y, w, h, text):
    """Draws a standard Chen diamond relationship symbol."""
    diamond = patches.Polygon([[x, y + h/2], [x + w/2, y], [x, y - h/2], [x - w/2, y]],
                             facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.5, zorder=3)
    ax.add_patch(diamond)
    ax.text(x, y, text, ha='center', va='center', fontsize=7.6, fontweight='bold', color='#92400E', zorder=4)

def generate_figure_4():
    fig, ax = plt.subplots(figsize=(11.5, 7.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 7.2)
    ax.axis('off')

    # Top Row: AUDIT_SESSIONS (left), USERS (center), PAPERS (right)
    draw_er_entity(ax, 0.5, 4.6, 2.7, 2.2, 'AUDIT_SESSIONS', [
        '[PK] id: SERIAL',
        '[FK] user_id: INTEGER',
        'title: VARCHAR(255)',
        'created_at: TIMESTAMP'
    ], pk_indices=[0], fk_indices=[1])

    draw_er_entity(ax, 4.3, 4.5, 2.9, 2.4, 'USERS', [
        '[PK] id: SERIAL',
        'email: VARCHAR(255)',
        'hashed_password: VARCHAR(255)',
        'is_admin: BOOLEAN',
        'created_at: TIMESTAMP'
    ], pk_indices=[0])

    draw_er_entity(ax, 8.3, 4.4, 2.8, 2.5, 'PAPERS', [
        '[PK] id: SERIAL',
        '[FK] user_id: INTEGER',
        'filename: VARCHAR(255)',
        'detected_title: TEXT',
        'file_hash: VARCHAR(64)',
        'uploaded_at: TIMESTAMP'
    ], pk_indices=[0], fk_indices=[1])

    # Relationship USERS -> AUDIT_SESSIONS: USERS --[1]-- <Initiates> --[N]--> AUDIT_SESSIONS
    draw_diamond(ax, 3.75, 5.7, 1.1, 0.6, 'Initiates')
    ax.plot([4.3, 3.75 + 0.55], [5.7, 5.7], color='#2B4C7E', lw=1.5)
    ax.plot([3.75 - 0.55, 3.2], [5.7, 5.7], color='#2B4C7E', lw=1.5)
    ax.text(4.2, 5.9, '1', fontsize=9, fontweight='bold', color='#1E3A8A')
    ax.text(3.3, 5.9, 'N', fontsize=9, fontweight='bold', color='#1E3A8A')

    # Relationship USERS -> PAPERS: USERS --[1]-- <Owns / Ingests> --[N]--> PAPERS
    draw_diamond(ax, 7.75, 5.7, 1.1, 0.6, 'Owns /\nIngests')
    ax.plot([7.2, 7.75 - 0.55], [5.7, 5.7], color='#2B4C7E', lw=1.5)
    ax.plot([7.75 + 0.55, 8.3], [5.7, 5.7], color='#2B4C7E', lw=1.5)
    ax.text(7.3, 5.9, '1', fontsize=9, fontweight='bold', color='#1E3A8A')
    ax.text(8.2, 5.9, 'N', fontsize=9, fontweight='bold', color='#1E3A8A')

    # Bottom Row: AUDIT_MESSAGES (left), PAPER_CHUNKS (right)
    draw_er_entity(ax, 0.5, 0.6, 2.9, 2.6, 'AUDIT_MESSAGES', [
        '[PK] id: SERIAL',
        '[FK] session_id: INTEGER',
        'role: VARCHAR(50)',
        'content: TEXT',
        'citations_json: JSONB',
        'timestamp: TIMESTAMP'
    ], pk_indices=[0], fk_indices=[1])

    draw_er_entity(ax, 6.7, 0.4, 4.4, 2.9, 'PAPER_CHUNKS', [
        '[PK] id: SERIAL',
        '[FK] paper_id: INTEGER',
        '[FK] user_id: INTEGER',
        'chunk_index: INTEGER',
        'page_number: INTEGER',
        'chunk_text: TEXT',
        'bbox_x0..y1: FLOAT[4]',
        '[Vector] embedding: vector(384) [HNSW]'
    ], pk_indices=[0], fk_indices=[1, 2], vec_indices=[7])

    # Relationship AUDIT_SESSIONS -> AUDIT_MESSAGES: AUDIT_SESSIONS --[1]-- <Contains> --[N]--> AUDIT_MESSAGES
    draw_diamond(ax, 1.85, 3.9, 1.2, 0.55, 'Contains')
    ax.plot([1.85, 1.85], [4.6, 3.9 + 0.275], color='#2B4C7E', lw=1.5)
    ax.plot([1.85, 1.85], [3.9 - 0.275, 3.2], color='#2B4C7E', lw=1.5)
    ax.text(2.05, 4.4, '1', fontsize=9, fontweight='bold', color='#1E3A8A')
    ax.text(2.05, 3.35, 'N', fontsize=9, fontweight='bold', color='#1E3A8A')

    # Relationship PAPERS -> PAPER_CHUNKS: PAPERS --[1]-- <Decomposed Into> --[N]--> PAPER_CHUNKS
    draw_diamond(ax, 9.1, 3.85, 1.5, 0.55, 'Decomposed\nInto')
    ax.plot([9.1, 9.1], [4.4, 3.85 + 0.275], color='#2B4C7E', lw=1.5)
    ax.plot([9.1, 9.1], [3.85 - 0.275, 3.3], color='#2B4C7E', lw=1.5)
    ax.text(9.3, 4.25, '1', fontsize=9, fontweight='bold', color='#1E3A8A')
    ax.text(9.3, 3.45, 'N', fontsize=9, fontweight='bold', color='#1E3A8A')

    # Center Bottom: Relational & Vector Legend Box (Generous margins, zero clipping)
    legend_box = patches.FancyBboxPatch((3.55, 0.45), 2.9, 2.65, boxstyle='round,pad=0.05,rounding_size=0.08',
                                       facecolor='#F8FAFC', edgecolor='#94A3B8', linestyle='--', linewidth=1.2, zorder=2)
    ax.add_patch(legend_box)
    ax.text(5.0, 2.85, 'Chen ER Cardinality Model', ha='center', va='center', fontsize=8.8, fontweight='bold', color='#1F3864')
    ax.text(3.75, 2.42, '[PK] Primary Key (Red)', ha='left', va='center', fontsize=7.8, fontweight='bold', color='#991B1B')
    ax.text(3.75, 2.02, '[FK] Foreign Key (Blue)', ha='left', va='center', fontsize=7.8, fontweight='bold', color='#1E40AF')
    ax.text(3.75, 1.62, '[Vector] Embedding (Green)', ha='left', va='center', fontsize=7.8, fontweight='bold', color='#065F46')
    ax.text(3.75, 1.22, '1 : N Explicit Cardinality', ha='left', va='center', fontsize=7.8, fontweight='bold', color='#1E3A8A')
    ax.text(3.75, 0.82, 'Tenant user_id isolation', ha='left', va='center', fontsize=7.8, fontweight='bold', color='#334155')

    plt.tight_layout()
    out_path1 = os.path.join(ASSETS_DIR, "sds_fig4_database_storage.png")
    out_path2 = os.path.join(ASSETS_DIR, "fig_4_er_diagram.png")
    plt.savefig(out_path1, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(out_path2, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated:", out_path1)
    print("Generated:", out_path2)

# ==============================================================================
# FIGURE 5: FORMAL UML USE CASE DIAGRAM (STICK-FIGURE ACTORS & SYSTEM BOUNDARY)
# ==============================================================================
def draw_stick_figure(ax, x, y, title, subtitle=''):
    """Draws a standard UML stick-figure actor (circle head, torso line, outstretched arms, leg lines)."""
    head = patches.Circle((x, y + 0.65), 0.18, facecolor='#E8EFF8', edgecolor='#1F3864', linewidth=1.8, zorder=4)
    ax.add_patch(head)
    ax.plot([x, x], [y + 0.47, y - 0.05], color='#1F3864', linewidth=2.0, zorder=4)
    ax.plot([x - 0.38, x + 0.38], [y + 0.25, y + 0.25], color='#1F3864', linewidth=2.0, zorder=4)
    ax.plot([x, x - 0.30], [y - 0.05, y - 0.58], color='#1F3864', linewidth=2.0, zorder=4)
    ax.plot([x, x + 0.30], [y - 0.05, y - 0.58], color='#1F3864', linewidth=2.0, zorder=4)
    ax.text(x, y - 0.82, title, ha='center', va='top', fontsize=9.5, fontweight='bold', color='#1F3864', zorder=5)
    if subtitle:
        ax.text(x, y - 1.08, subtitle, ha='center', va='top', fontsize=8.0, color='#475569', zorder=5)

def draw_use_case_oval(ax, x, y, w, h, text):
    """Draws a standard UML horizontal use-case ellipse."""
    ellipse = patches.FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle=f'round,pad=0.08,rounding_size={h/2}',
                                    facecolor='#E8EFF8', edgecolor='#2B4C7E', linewidth=1.6, zorder=3)
    ax.add_patch(ellipse)
    ax.text(x, y, text, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#111111', zorder=4)

def draw_include_arrow(ax, start, end, label_offset=(0, 0.26)):
    """Draws a dashed UML <<include>> dependency arrow with clean non-overlapping label."""
    arrow = patches.FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=14,
                                   linestyle='--', color='#2B4C7E', linewidth=1.5, zorder=4)
    ax.add_patch(arrow)
    mid_x = (start[0] + end[0]) / 2 + label_offset[0]
    mid_y = (start[1] + end[1]) / 2 + label_offset[1]
    ax.text(mid_x, mid_y, '<<include>>', ha='center', va='center', fontsize=7.8, fontweight='bold',
            color='#1F3864', zorder=5,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFFFFF', edgecolor='#CBD5E1', linewidth=0.8, alpha=0.98))

def generate_figure_5():
    fig, ax = plt.subplots(figsize=(11.5, 9.0), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 9.0)
    ax.axis('off')

    # Stick Figures: Left = Clinical Researcher, Right = System Administrator
    draw_stick_figure(ax, 0.9, 4.8, 'Clinical\nResearcher', 'Primary Investigator')
    draw_stick_figure(ax, 10.6, 4.8, 'System\nAdministrator', 'Compliance & Security')

    # Formal System Boundary Rectangle
    boundary = patches.FancyBboxPatch((1.9, 0.4), 7.7, 8.2, boxstyle='round,pad=0.08,rounding_size=0.12',
                                    facecolor='#FFFFFF', edgecolor='#94A3B8', linewidth=1.8, linestyle='-', zorder=1)
    ax.add_patch(boundary)
    ax.text(2.1, 8.35, 'VeriNexa Platform Boundary', ha='left', va='top', fontsize=10.5, fontweight='bold', color='#1F3864', zorder=2)

    # Top & Bottom Centered Use Cases
    draw_use_case_oval(ax, 5.75, 7.6, 3.8, 0.65, 'Authenticate & Session Hydration')
    draw_use_case_oval(ax, 5.75, 1.2, 3.8, 0.65, 'Audit Telemetry & Manage Tenants')

    # Left Column Use Cases (width 3.1, x center = 3.65 -> spans 2.1 to 5.2)
    draw_use_case_oval(ax, 3.65, 6.4, 3.1, 0.65, 'Upload Clinical Paper Buffer')
    draw_use_case_oval(ax, 3.65, 4.9, 3.1, 0.65, 'Multi-Paper Evidence RAG Chat')
    draw_use_case_oval(ax, 3.65, 2.5, 3.1, 0.65, 'Cross-Examine Trial Contradictions')

    # Right Column Use Cases (width 3.1, x center = 7.85 -> spans 6.3 to 9.4)
    draw_use_case_oval(ax, 7.85, 6.4, 3.1, 0.65, 'Execute 3-Tier Verification Gate')
    draw_use_case_oval(ax, 7.85, 4.9, 3.1, 0.65, 'Query Dense pgvector HNSW Index')
    draw_use_case_oval(ax, 7.85, 3.5, 3.1, 0.65, 'Render Amber Citation Highlights')

    # Solid Straight Association Lines from Researcher (x=0.9, y=4.8)
    ax.plot([0.9, 3.85], [4.8, 7.6], color='#1F3864', lw=1.5, zorder=2)
    ax.plot([0.9, 2.1], [4.8, 6.4], color='#1F3864', lw=1.5, zorder=2)
    ax.plot([0.9, 2.1], [4.8, 4.9], color='#1F3864', lw=1.5, zorder=2)
    ax.plot([0.9, 2.1], [4.8, 2.5], color='#1F3864', lw=1.5, zorder=2)

    # Solid Straight Association Lines from Administrator (x=10.6, y=4.8)
    ax.plot([10.6, 7.65], [4.8, 7.6], color='#1F3864', lw=1.5, zorder=2)
    ax.plot([10.6, 7.65], [4.8, 1.2], color='#1F3864', lw=1.5, zorder=2)

    # <<include>> Dashed Arrows (1.1-unit horizontal gap with padded, non-overlapping labels)
    draw_include_arrow(ax, (5.2, 6.4), (6.3, 6.4), label_offset=(0, 0.26))
    draw_include_arrow(ax, (5.2, 4.9), (6.3, 4.9), label_offset=(0, 0.26))
    draw_include_arrow(ax, (5.0, 4.6), (6.5, 3.75), label_offset=(0.12, 0.24))

    plt.tight_layout()
    out_path1 = os.path.join(ASSETS_DIR, "sds_fig5_use_case.png")
    out_path2 = os.path.join(ASSETS_DIR, "fig_5_use_case.png")
    plt.savefig(out_path1, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(out_path2, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated:", out_path1)
    print("Generated:", out_path2)

# ==============================================================================
# FIGURE 6: COMPONENT DIAGRAM
# ==============================================================================
def generate_figure_6():
    fig, ax = plt.subplots(figsize=(11, 8.5), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    # Frontend Components (Top)
    draw_box(ax, 0.8, 5.8, 2.8, 1.8, title="UI: Document Reader", text="HTML5 Canvas High-DPI\nNative Frame Fallback\nZoom, Pan & Scale Sync", radius=0.1)
    draw_box(ax, 4.1, 5.8, 2.8, 1.8, title="UI: Evidence Chat", text="Corpus / Paper Mode\nMarkdown & KaTeX Math\nInteractive Citation Badges", radius=0.1)
    draw_box(ax, 7.4, 5.8, 2.8, 1.8, title="UI: Spatial BBox Overlay", text="Amber Highlight Canvas\nNormalized Point Mapping\nInstant Scroll Anchoring", radius=0.1)

    # Backend Gateway (Middle)
    draw_box(ax, 2.0, 3.4, 7.0, 1.5, title="FastAPI Application Controller & Middleware Gateway", text="Ingestion Controller & Three-Tier Heuristic/Semantic Verification Gate\nOAuth2 Password Bearer (JWT) & Tenant Isolation Predicates\nLangGraph State Orchestrator (Retrieve, Re-rank, Arbitrate, Synthesize)", radius=0.12)

    # ML & Persistence (Bottom)
    draw_box(ax, 0.6, 0.6, 3.0, 1.8, title="PyMuPDF Fitz Engine", text="PDF Document Stream Parser\nPoint Geometry Extractor\nUnicode De-hyphenation", radius=0.1)
    draw_box(ax, 4.0, 0.6, 3.0, 1.8, title="SentenceTransformers & Ollama", text="all-MiniLM-L6-v2 (384-d)\nLlama 3.1-8B-Instruct\nZero-Cloud Data Boundary", radius=0.1)
    draw_box(ax, 7.4, 0.6, 3.0, 1.8, title="PostgreSQL 17 + pgvector", text="ACID Relational Storage\nHNSW Cosine Graph Index\nAudit Logs & User Quotas", radius=0.1)

    # Connecting arrows
    draw_arrow(ax, (2.2, 5.8), (3.5, 4.9), lw=1.5)
    draw_arrow(ax, (5.5, 5.8), (5.5, 4.9), lw=1.5)
    draw_arrow(ax, (8.8, 5.8), (7.5, 4.9), lw=1.5)

    draw_arrow(ax, (3.5, 3.4), (2.1, 2.4), lw=1.5)
    draw_arrow(ax, (5.5, 3.4), (5.5, 2.4), lw=1.5)
    draw_arrow(ax, (7.5, 3.4), (8.9, 2.4), lw=1.5)

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "sds_fig6_component_diagram.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated:", out_path)

# ==============================================================================
# FIGURE 7: SEQUENCE DIAGRAM (WIDENED CANVAS & GENEROUS BOUNDARY MARGINS)
# ==============================================================================
def generate_figure_7():
    fig, ax = plt.subplots(figsize=(11.5, 10.5), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 10.5)
    ax.axis('off')

    # Lifelines shifted left to give ample right-hand margin
    lifelines = [
        ("Researcher", 0.8),
        ("React UI", 2.3),
        ("FastAPI Gateway", 4.3),
        ("pgvector HNSW", 6.3),
        ("Ollama Llama 3.1", 8.1),
        ("PDF Reader", 9.7)
    ]

    for name, x in lifelines:
        draw_box(ax, x - 0.65, 9.6, 1.3, 0.65, title=name, radius=0.08, title_size=9)
        ax.plot([x, x], [0.6, 9.6], color="#94A3B8", linestyle="--", linewidth=1.2, zorder=1)

    # Steps 1 to 9 with generous 0.82 vertical spacing
    msgs = [
        (0.8, 2.3, 8.8, "1. Inquire (Corpus Mode)"),
        (2.3, 4.3, 8.0, "2. POST /api/chat/query"),
        (4.3, 6.3, 7.2, "3. Cosine Nearest-Neighbor Search"),
        (6.3, 4.3, 6.4, "4. Return Top-k Excerpts"),
        (4.3, 8.1, 5.6, "5. Dispatch Grounded NLI Prompt"),
        (8.1, 4.3, 4.8, "6. Return Answer & Citations"),
        (4.3, 2.3, 4.0, "7. SSE Stream / JSON Badges"),
        (0.8, 2.3, 3.2, "8. Click Citation Badge [Chunk #N]"),
        (2.3, 9.7, 2.3, "9. Switch Paper & Scroll to Page"),
    ]

    for start_x, end_x, y, label in msgs:
        draw_arrow(ax, (start_x, y), (end_x, y), label=label, label_offset=(0, 0.18), lw=1.5)

    # Step 10: Self-call loop strictly inside bounds on PDF Reader lifeline (x=9.7)
    arc = patches.Arc((9.7, 1.3), 0.6, 0.45, angle=0, theta1=270, theta2=90, color=COLOR_ARROW, linewidth=1.6, zorder=3)
    ax.add_patch(arc)
    ax.annotate('', xy=(9.7, 1.07), xytext=(9.95, 1.07),
                arrowprops=dict(arrowstyle="-|>", color=COLOR_ARROW, lw=1.5, mutation_scale=14))
    
    # Label placed between Ollama (8.1) and PDF Reader (9.7) lifelines, far from canvas edge
    ax.text(7.8, 1.3, "10. Render Amber Highlight [x0, y0, x1, y1]", fontsize=8.5, color=COLOR_TEXT_TITLE,
            fontweight='bold', ha='center', va='center', zorder=5,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFFFFF', edgecolor='#CBD5E1', alpha=0.95))

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "sds_fig7_sequence_diagram.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated:", out_path)

# ==============================================================================
# FIGURE 8: ACTIVITY DIAGRAM (CLOSED OLLAMA SEMANTIC GATE BRANCH)
# ==============================================================================
def generate_figure_8():
    fig, ax = plt.subplots(figsize=(10, 10.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10.5)
    ax.axis('off')

    # Start
    start_circle = plt.Circle((5.0, 10.0), 0.22, color="#1F3864", zorder=3)
    ax.add_patch(start_circle)

    draw_arrow(ax, (5.0, 9.75), (5.0, 9.2))

    # Activity 1: Read PDF
    draw_box(ax, 3.0, 8.5, 4.0, 0.7, title="Read First 3 Pages via PyMuPDF", radius=0.08, title_size=10)
    draw_arrow(ax, (5.0, 8.5), (5.0, 7.9))

    # Decision 1: Text length < 150 chars?
    diamond1 = patches.Polygon([[5.0, 7.9], [6.2, 7.4], [5.0, 6.9], [3.8, 7.4]], facecolor="#FEF3C7", edgecolor="#D97706", linewidth=1.5, zorder=3)
    ax.add_patch(diamond1)
    ax.text(5.0, 7.4, "Text < 150 chars?", ha='center', va='center', fontsize=9, fontweight='bold', zorder=4)

    # Scanned branch
    draw_arrow(ax, (3.8, 7.4), (2.4, 7.4), label="[YES]", label_offset=(0, 0.15))
    draw_box(ax, 0.6, 7.0, 1.8, 0.8, title="Scanned Buffer", text="Flag for OCR", radius=0.06, box_fill="#FEE2E2", box_border="#DC2626")

    # Regular branch
    draw_arrow(ax, (5.0, 6.9), (5.0, 6.2), label="[NO]")
    draw_box(ax, 3.0, 5.5, 4.0, 0.7, title="Strip Metadata & De-hyphenate", radius=0.08, title_size=10)

    draw_arrow(ax, (5.0, 5.5), (5.0, 4.9))

    # Decision 2: >= 2 Clinical Markers?
    diamond2 = patches.Polygon([[5.0, 4.9], [6.2, 4.4], [5.0, 3.9], [3.8, 4.4]], facecolor="#FEF3C7", edgecolor="#D97706", linewidth=1.5, zorder=3)
    ax.add_patch(diamond2)
    ax.text(5.0, 4.4, ">= 2 Clinical Markers?", ha='center', va='center', fontsize=9, fontweight='bold', zorder=4)

    # Branch to Ollama Semantic Gate
    draw_arrow(ax, (6.2, 4.4), (7.4, 4.4), label="[NO]", label_offset=(0, 0.15))
    draw_box(ax, 7.4, 4.0, 2.2, 0.8, title="Ollama Semantic Gate", text="Evaluate Academic Paper", radius=0.06)

    # Clean connection from Ollama back to pipeline [YES / Default Accept]
    draw_arrow(ax, (7.4, 4.0), (6.8, 2.9), label="[Academic / Accept]", label_pos=0.6, label_offset=(0.6, 0.1))

    # Reject branch from Ollama [Non-Academic / Invalid]
    draw_arrow(ax, (8.5, 4.0), (8.5, 2.6), label="[Non-Academic]", label_offset=(0.6, 0))
    draw_box(ax, 7.6, 1.8, 1.8, 0.7, title="Reject HTTP 422", text="Terminate Flow", radius=0.06, box_fill="#FEE2E2", box_border="#DC2626")

    # Main pipeline proceed
    draw_arrow(ax, (5.0, 3.9), (5.0, 3.1), label="[YES]")
    draw_box(ax, 2.5, 2.4, 5.0, 0.7, title="Sliding-Window Tokenization & Spatial BBox Extraction", text="512 tokens / 64 overlap; normalized [0.0, 1.0] coordinates", radius=0.08, title_size=9.5)

    draw_arrow(ax, (5.0, 2.4), (5.0, 1.8))
    draw_box(ax, 2.5, 1.1, 5.0, 0.7, title="all-MiniLM-L6-v2 Embeddings & pgvector HNSW Insert", text="384-d dense vectors indexed into cosine graph", radius=0.08, title_size=9.5)

    draw_arrow(ax, (5.0, 1.1), (5.0, 0.5))

    # End
    end_outer = plt.Circle((5.0, 0.28), 0.24, color="#1F3864", fill=False, linewidth=2, zorder=3)
    end_inner = plt.Circle((5.0, 0.28), 0.16, color="#1F3864", zorder=4)
    ax.add_patch(end_outer)
    ax.add_patch(end_inner)

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "sds_fig8_activity_diagram.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated:", out_path)

if __name__ == "__main__":
    print("Re-rendering all 8 SDS diagrams with exact fixes at 300 DPI...")
    generate_figure_1()
    generate_figure_2()
    generate_figure_3()
    generate_figure_4()
    generate_figure_5()
    generate_figure_6()
    generate_figure_7()
    generate_figure_8()
    print("All diagrams re-rendered successfully!")
