export const RESEARCH_PAPERS = [
  {
    id: "paper-01",
    name: "Cellular Longevity & mTORC1 Kinetics",
    category: "Cellular Biology",
    title: "Double-Blind Multicenter Longevity Trial",
    doi: "10.1016/j.cell.2026.04.019",
    sampleSize: "N = 1,420",
    pValue: "p < 0.001",
    tagColor: "emerald",
    accentHex: "#10b981",
    tagLabel: "Verified P-Value",
    integrityScore: "99.4%",
    abstractMatch: "100% Consistent",
    hallucinationRisk: "0.00% (Closed Corpus)",
    contradictionsFound: "0 Discrepancies",
    auditDate: "August 28, 2026",
    ragEngine: "Hybrid BM25 + pgvector (1536-dim)",
    description: "Multi-agent LangGraph audit verified sample cohorts (N=1,420) and p-value claims across 42 data tables against raw supplementary appendix.",
    highlights: ["Abstract-to-Methodology Match 100%", "BM25 + pgvector Hybrid Hit", "Cross-Table P-Value Confirmed"],
    specs: {
      pdfStructure: "Clean text layer + 14 vector tables parsed",
      embeddingDistance: "Cosine similarity 0.942",
      claimAttribution: "48 exact bounding-box citations",
      langGraphNodes: "Extraction -> Cross-Ref -> Synthesis Verified"
    }
  },
  {
    id: "paper-02",
    name: "Dual GLP-1/GIP Agonist Meta-Study",
    category: "Metabolic Research",
    title: "Comparative Glycemic & Lipolysis Meta-Analysis",
    doi: "10.1056/NEJMoa2521908",
    sampleSize: "N = 8,940 (12 Cohorts)",
    pValue: "p = 0.002",
    tagColor: "gold",
    accentHex: "#d4af37",
    tagLabel: "Multi-Cohort Audit",
    integrityScore: "98.7%",
    abstractMatch: "99.1% Consistent",
    hallucinationRisk: "0.00% (Closed Corpus)",
    contradictionsFound: "1 Minor Metric Flagged",
    auditDate: "August 25, 2026",
    ragEngine: "Hybrid BM25 + pgvector (1536-dim)",
    description: "Detected subtle metric discrepancy between abstract reported weight delta (-17.4%) and Table 3 subgroup sensitivity analysis (-16.9%).",
    highlights: ["Contradiction Matrix Flagged", "Cohort Size Cross-Referenced", "Exact Dual-Pane Highlighting"],
    specs: {
      pdfStructure: "Scanned OCR + High-Density Tables Extracted",
      embeddingDistance: "Cosine similarity 0.918",
      claimAttribution: "72 precise span anchors",
      langGraphNodes: "Statistical Validator -> Discrepancy Flag"
    }
  },
  {
    id: "paper-03",
    name: "Mitochondrial MOTS-c Transcription",
    category: "Genomics",
    title: "Nuclear-Mitochondrial Signaling Cascade",
    doi: "10.1038/s41586-026-0711-2",
    sampleSize: "N = 340 (In-Vivo)",
    pValue: "p < 0.005",
    tagColor: "cyan",
    accentHex: "#06b6d4",
    tagLabel: "Structural Verification",
    integrityScore: "99.8%",
    abstractMatch: "100% Consistent",
    hallucinationRisk: "0.00% (Closed Corpus)",
    contradictionsFound: "0 Discrepancies",
    auditDate: "August 22, 2026",
    ragEngine: "Hybrid BM25 + pgvector (1536-dim)",
    description: "Autonomous verification of Western blot quantifications and qPCR replication data against stated abstract conclusions.",
    highlights: ["Closed-Corpus RAG Anchored", "Table-to-Text Concordance", "Zero Hallucination Guarantee"],
    specs: {
      pdfStructure: "Native PDF + High-Res Blot Graphics OCR",
      embeddingDistance: "Cosine similarity 0.961",
      claimAttribution: "36 verified figure references",
      langGraphNodes: "Figure Auditor -> Methodology Parser"
    }
  },
  {
    id: "paper-04",
    name: "CRISPR-Cas9 Off-Target Frequency",
    category: "Gene Editing",
    title: "High-Throughput Cleavage Specificity Assay",
    doi: "10.1126/science.ade9041",
    sampleSize: "1.2M Cleavage Sites",
    pValue: "p < 0.0001",
    tagColor: "violet",
    accentHex: "#a855f7",
    tagLabel: "Genomic Deep Scan",
    integrityScore: "99.2%",
    abstractMatch: "99.6% Consistent",
    hallucinationRisk: "0.00% (Closed Corpus)",
    contradictionsFound: "0 Discrepancies",
    auditDate: "August 18, 2026",
    ragEngine: "Hybrid BM25 + pgvector (1536-dim)",
    description: "Cross-correlated deep sequencing datasets across 5 supplementary appendices to confirm reported 0.003% cleavage margin.",
    highlights: ["Supplementary Indexing", "Algorithmic P-Value Recalculation", "Dual-Pane Synchronized"],
    specs: {
      pdfStructure: "Dense tabular appendix (180 pages)",
      embeddingDistance: "Cosine similarity 0.954",
      claimAttribution: "114 cross-document links",
      langGraphNodes: "Multi-Agent Consensus Protocol"
    }
  }
];

export const WORKFLOW_STEPS = [
  {
    step: "01",
    title: "PDF Ingestion & Structure Validation",
    subtitle: "Automated ingestion pipeline parses multi-column typography, tabular matrices, formulas, and visual figures into structured AST chunks.",
    badge: "AST Parse Engine",
    spec: "Zero Loss OCR"
  },
  {
    step: "02",
    title: "Hybrid Indexing (BM25 + pgvector)",
    subtitle: "Combines exact lexical keyword BM25 retrieval with 1536-dimensional dense vector embeddings stored in PostgreSQL pgvector.",
    badge: "Reciprocal Rank Fusion",
    spec: "Sub-50ms Retrieval"
  },
  {
    step: "03",
    title: "Multi-Agent LangGraph Verification",
    subtitle: "Specialized AI agents independently audit p-values, recalculate sample confidence intervals, and evaluate abstract-to-body integrity.",
    badge: "Autonomous Consensus",
    spec: "P-Value & Metric Audit"
  },
  {
    step: "04",
    title: "Interactive Dual-Pane Workspace",
    subtitle: "Synchronized reading pane with real-time text highlight syncing, exact bounding-box claim attribution, and live contradiction flags.",
    badge: "Real-Time Sync",
    spec: "100% Verifiable Source"
  }
];

export const CORE_FEATURES = [
  {
    title: "Contradiction & Conflict Matrix",
    description: "Detects numerical and methodological contradictions across multiple studies. Instantly flags when sample sizes, effect magnitudes, or p-values conflict between abstract, results, or external papers.",
    metric: "Discrepancy Detector",
    tag: "Multi-Paper Conflict"
  },
  {
    title: "Abstract Integrity Audit",
    description: "Rigorously verifies whether the paper's abstract makes assertions not backed by its methodology or statistical results, highlighting overclaimed outcomes or missing subgroup data.",
    metric: "100% Claim Cross-Ref",
    tag: "Overclaim Prevention"
  },
  {
    title: "Closed-Corpus RAG Engine",
    description: "Restricts all AI synthesis strictly to uploaded literature. Built with pgvector and strict citation bounding boxes to guarantee zero hallucinations and instant source auditability.",
    metric: "Zero Hallucination",
    tag: "Guaranteed Grounding"
  },
  {
    title: "Dual-Pane Synchronized Attribution",
    description: "Click any synthesized assertion to jump directly to the exact page, paragraph, and highlighted coordinate in the original research PDF with side-by-side verification.",
    metric: "Bounding-Box Sync",
    tag: "Real-Time Traceability"
  }
];

export const FAQ_ITEMS = [
  {
    question: "How does the platform handle complex scientific PDF parsing and tables?",
    answer: "Our ingestion engine decomposes research PDFs into unified Abstract Syntax Trees (ASTs). It reconstructs multi-column scientific layouts, parses complex LaTeX formulas, extracts high-density tables into structured JSON schemas, and cleans OCR artifacts without losing header-to-data-cell relationships."
  },
  {
    question: "Does it cite exact sources and bounding boxes for every claim?",
    answer: "Yes, 100% of the time. Every summary statement, metric extraction, or cross-reference includes a cryptographic citation token. Clicking any token in the Dual-Pane Workspace navigates the viewer to the exact page, paragraph, and bounding-box highlight in the original PDF source."
  },
  {
    question: "Can I cross-reference and compare multiple papers simultaneously?",
    answer: "Absolutely. You can upload a dossier of dozens or hundreds of papers. Our Contradiction & Conflict Matrix maps shared biomarkers, dosages, sample sizes, and p-values side-by-side, surfacing consensus findings as well as conflicting trial results across the entire corpus."
  },
  {
    question: "How does the Closed-Corpus RAG Engine eliminate hallucinations?",
    answer: "Unlike general-purpose conversational LLMs, our RAG architecture enforces hard closed-corpus retrieval constraints. If an assertion or p-value is not explicitly present within the hybrid BM25 + pgvector context retrieval window, the model is architecturally prevented from inferring or fabricating data."
  },
  {
    question: "What checks does the LangGraph multi-agent system execute on statistical claims?",
    answer: "The LangGraph graph coordinates four autonomous specialized agents: (1) Extraction Agent isolates numerical claims, (2) Statistical Validator recalculates degrees of freedom and p-value bounds, (3) Abstract Auditor tests claim alignment against the methodology, and (4) Adversarial Referee probes for confounding variables or subgroup bias."
  }
];
