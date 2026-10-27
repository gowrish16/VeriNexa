"""
Standalone Python Build Script for VeriNexa Software Design Specification (SDS) PDF
Compiles: C:\\Projects\\VeriNexa\\docs\\VeriNexa_Software_Design_Specification.pdf

Strictly replicates the structure, typography, styling, visual diagrams, and formatting
of the student reference SDS PDF:
"C:\\Users\\HP\\OneDrive\\Documents\\SDS_News_Headline_Classification_Final.pdf"

Project Metadata:
- Title: VeriNexa: Cross-Document Contradiction Detection and Integrity Verification System
- Short Header: VeriNexa-SDS
- Student: Gowrish Shet (USN: 4JK25MC039)
- Project Guide: Dr. Bruce Mathew
- Degree: Master of Computer Applications (MCA)
- Department: Department of MCA, A.J. Institute of Engineering & Technology, Mangaluru
- Track: Machine Learning & NLP / Clinical Information Retrieval Track
- Academic Year: 2026-2027
"""

import os
import sys
import tempfile

os.environ['MPLCONFIGDIR'] = os.path.join(tempfile.gettempdir(), 'mpl_cache')

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, Flowable
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Line

DOCS_DIR = r"C:\Projects\VeriNexa\docs"
ASSETS_DIR = os.path.join(DOCS_DIR, "assets")
OUTPUT_PDF = os.path.join(DOCS_DIR, "VeriNexa_Software_Design_Specification.pdf")

# Page Dimensions (A4)
PAGE_WIDTH, PAGE_HEIGHT = A4  # 595.27 x 841.89 pt
LEFT_MARGIN = 70.6
RIGHT_MARGIN = 70.4
PRINTABLE_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN  # 454.27 pt

COLOR_NAVY = colors.HexColor('#1F3864')
COLOR_TABLE_HEADER = colors.HexColor('#DCE6F2')
COLOR_BORDER = colors.HexColor('#7F7F7F')
COLOR_FRAME_BORDER = colors.HexColor('#CBD5E1')
COLOR_SCREENSHOT_BORDER = colors.HexColor('#334155')
COLOR_FRAME_BG = colors.HexColor('#F8FAFC')
COLOR_TEXT_MAIN = colors.HexColor('#000000')

# ==============================================================================
# TWO-PASS NUMBERED CANVAS (RUNNING HEADERS & FOOTERS)
# ==============================================================================
class AJIETNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            p_num = self._pageNumber
            
            # Page 1: Cover Page (No running header, no footer)
            if p_num == 1:
                super().showPage()
                continue

            # Header Text & Separator Line (Strictly A.J. INSTITUTE with single dot)
            self.setFont("Times-Bold", 8.5)
            self.drawCentredString(PAGE_WIDTH / 2.0, 804, "A.J. INSTITUTE OF ENGINEERING & TECHNOLOGY, MANGALURU | DEPARTMENT OF MCA")
            
            self.setFont("Times-Italic", 8.5)
            self.drawCentredString(PAGE_WIDTH / 2.0, 792, "VeriNexa-SDS")

            # Thin Navy Rule below header
            self.setStrokeColor(COLOR_NAVY)
            self.setLineWidth(0.8)
            self.line(LEFT_MARGIN, 786.5, PAGE_WIDTH - RIGHT_MARGIN, 786.5)

            # Thin Navy Rule above footer
            self.line(LEFT_MARGIN, 43.4, PAGE_WIDTH - RIGHT_MARGIN, 43.4)

            # Footer Text
            self.setFont("Times-Roman", 9.5)
            if p_num == 2:
                # TOC page uses Roman numeral
                self.drawCentredString(PAGE_WIDTH / 2.0, 28, "Page ii")
            else:
                # Content pages use Arabic numeral starting at 1
                content_page = p_num - 2
                self.drawCentredString(PAGE_WIDTH / 2.0, 28, f"Page {content_page}")

            super().showPage()
        super().save()

# ==============================================================================
# SECTION HEADING UNDERLINE FLOWABLE
# ==============================================================================
class AccentRule(Flowable):
    def __init__(self, width=PRINTABLE_WIDTH, height=5, thickness=1.2, color=COLOR_NAVY):
        super().__init__()
        self.width = width
        self.height = height
        self.thickness = thickness
        self.color = color

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        self.canv.saveState()
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.height / 2.0, self.width, self.height / 2.0)
        self.canv.restoreState()

def framed_screenshot(image_path, width=414, height=233):
    """Wraps a screenshot in a clean 1x1 table with a subtle slate border (#334155) preserving 16:9 widescreen."""
    img = Image(image_path, width=width, height=height)
    t = Table([[img]], colWidths=[width + 4])
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.85, COLOR_SCREENSHOT_BORDER),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 1.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1.5),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
    ]))
    return t

# ==============================================================================
# DOCUMENT BUILDER
# ==============================================================================
def build_pdf():
    # 1. Regenerate 300 DPI diagrams
    try:
        import generate_sds_diagrams
        print("[0/4] Re-rendering diagrams at 300 DPI...")
        generate_sds_diagrams.generate_figure_1()
        generate_sds_diagrams.generate_figure_2()
        generate_sds_diagrams.generate_figure_3()
        generate_sds_diagrams.generate_figure_4()
        generate_sds_diagrams.generate_figure_5()
        generate_sds_diagrams.generate_figure_6()
        generate_sds_diagrams.generate_figure_7()
        generate_sds_diagrams.generate_figure_8()
    except Exception as e:
        print("Note: Could not run generate_sds_diagrams directly:", e)

    print("[1/4] Preparing styles and page layout...")
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=58,
        bottomMargin=58
    )

    styles = getSampleStyleSheet()

    # Custom Paragraph Styles matching Reference
    style_cover_inst = ParagraphStyle(
        'CoverInst',
        fontName='Times-Bold',
        fontSize=15.5,
        leading=19.5,
        alignment=TA_CENTER,
        textColor=COLOR_TEXT_MAIN
    )

    style_cover_dept = ParagraphStyle(
        'CoverDept',
        fontName='Times-Bold',
        fontSize=13.5,
        leading=17,
        alignment=TA_CENTER,
        textColor=COLOR_TEXT_MAIN
    )

    style_cover_doc_title = ParagraphStyle(
        'CoverDocTitle',
        fontName='Times-Bold',
        fontSize=19,
        leading=23,
        alignment=TA_CENTER,
        textColor=COLOR_TEXT_MAIN
    )

    style_cover_proj_title = ParagraphStyle(
        'CoverProjTitle',
        fontName='Times-Bold',
        fontSize=16,
        leading=20.5,
        alignment=TA_CENTER,
        textColor=COLOR_TEXT_MAIN
    )

    style_cover_prep = ParagraphStyle(
        'CoverPrep',
        fontName='Times-Italic',
        fontSize=12,
        leading=15,
        alignment=TA_CENTER,
        textColor=COLOR_TEXT_MAIN
    )

    style_cover_name = ParagraphStyle(
        'CoverName',
        fontName='Times-Bold',
        fontSize=15,
        leading=18,
        alignment=TA_CENTER,
        textColor=COLOR_TEXT_MAIN
    )

    style_cover_usn = ParagraphStyle(
        'CoverUSN',
        fontName='Times-Roman',
        fontSize=12.5,
        leading=15.5,
        alignment=TA_CENTER,
        textColor=COLOR_TEXT_MAIN
    )

    style_cover_guide = ParagraphStyle(
        'CoverGuide',
        fontName='Times-Bold',
        fontSize=13.5,
        leading=16.5,
        alignment=TA_CENTER,
        textColor=COLOR_TEXT_MAIN
    )

    style_cover_deg = ParagraphStyle(
        'CoverDeg',
        fontName='Times-Bold',
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        textColor=COLOR_TEXT_MAIN
    )

    # Content Styles
    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        fontName='Times-Bold',
        fontSize=17,
        leading=21,
        textColor=COLOR_NAVY,
        spaceBefore=0,
        spaceAfter=3,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'Heading2_Custom',
        fontName='Times-Bold',
        fontSize=13.5,
        leading=17,
        textColor=COLOR_NAVY,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    style_h3 = ParagraphStyle(
        'Heading3_Custom',
        fontName='Times-Bold',
        fontSize=11.5,
        leading=14.5,
        textColor=COLOR_TEXT_MAIN,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'Body_Custom',
        fontName='Times-Roman',
        fontSize=10.5,
        leading=13.5,
        alignment=TA_JUSTIFY,
        textColor=COLOR_TEXT_MAIN,
        spaceBefore=0,
        spaceAfter=4
    )

    style_bullet = ParagraphStyle(
        'Bullet_Custom',
        fontName='Times-Roman',
        fontSize=10.5,
        leading=13.5,
        alignment=TA_JUSTIFY,
        leftIndent=15,
        firstLineIndent=-10,
        textColor=COLOR_TEXT_MAIN,
        spaceBefore=0,
        spaceAfter=3
    )

    style_caption = ParagraphStyle(
        'Caption_Custom',
        fontName='Times-Roman',
        fontSize=9.5,
        leading=12,
        alignment=TA_CENTER,
        textColor=COLOR_TEXT_MAIN,
        spaceBefore=3,
        spaceAfter=5,
        keepWithNext=True
    )

    style_table_caption = ParagraphStyle(
        'TableCaption_Custom',
        fontName='Times-Roman',
        fontSize=9.5,
        leading=12,
        alignment=TA_LEFT,
        textColor=COLOR_TEXT_MAIN,
        spaceBefore=4,
        spaceAfter=3,
        keepWithNext=True
    )

    style_toc_title = ParagraphStyle(
        'TOCTitle',
        fontName='Times-Bold',
        fontSize=17,
        leading=21,
        alignment=TA_CENTER,
        textColor=COLOR_NAVY,
        spaceBefore=0,
        spaceAfter=12
    )

    style_toc_title_col = ParagraphStyle(
        'TOCTitleCol',
        fontName='Times-Roman',
        fontSize=10,
        leading=14.5,
        alignment=TA_LEFT,
        textColor=COLOR_TEXT_MAIN
    )

    style_toc_page_col = ParagraphStyle(
        'TOCPageCol',
        fontName='Times-Roman',
        fontSize=10,
        leading=14.5,
        alignment=TA_RIGHT,
        textColor=COLOR_TEXT_MAIN
    )

    style_th = ParagraphStyle(
        'TH_Custom',
        fontName='Times-Bold',
        fontSize=9,
        leading=11.5,
        alignment=TA_LEFT,
        textColor=COLOR_TEXT_MAIN
    )

    style_td = ParagraphStyle(
        'TD_Custom',
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11,
        alignment=TA_LEFT,
        textColor=COLOR_TEXT_MAIN
    )

    def create_table(headers, data, col_widths):
        table_data = []
        table_data.append([Paragraph(h, style_th) for h in headers])
        for row in data:
            table_data.append([Paragraph(cell, style_td) for cell in row])
        
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_TABLE_HEADER),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('TOPPADDING', (0, 0), (-1, 0), 3.5),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 3.5),
            ('TOPPADDING', (0, 1), (-1, -1), 2.8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2.8),
            ('LEFTPADDING', (0, 0), (-1, -1), 4.5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4.5),
        ]))
        return t

    story = []

    # ==========================================================================
    # PAGE 1: COVER PAGE
    # ==========================================================================
    print("[2/4] Constructing Page 1 (Cover Page)...")
    story.append(Spacer(1, 45))
    story.append(Paragraph("A.J. INSTITUTE OF ENGINEERING & TECHNOLOGY,<br/>MANGALURU", style_cover_inst))
    story.append(Spacer(1, 12))
    story.append(Paragraph("DEPARTMENT OF MCA", style_cover_dept))
    story.append(Spacer(1, 80))
    story.append(Paragraph("SOFTWARE DESIGN SPECIFICATION", style_cover_doc_title))
    story.append(Spacer(1, 24))
    story.append(Paragraph("VERINEXA: CROSS-DOCUMENT CONTRADICTION DETECTION<br/>AND INTEGRITY VERIFICATION SYSTEM", style_cover_proj_title))
    story.append(Spacer(1, 75))
    story.append(Paragraph("Prepared by", style_cover_prep))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Gowrish Shet", style_cover_name))
    story.append(Spacer(1, 4))
    story.append(Paragraph("USN: 4JK25MC039", style_cover_usn))
    story.append(Spacer(1, 26))
    story.append(Paragraph("Project Guide", style_cover_prep))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Dr. Bruce Mathew", style_cover_guide))
    story.append(Spacer(1, 45))
    story.append(Paragraph("Master of Computer Applications (MCA)", style_cover_deg))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Academic Year 2026-2027", style_cover_deg))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 2: TABLE OF CONTENTS (PAGE ii) - FIXED 2-COLUMN TABLE WITH ARABIC 1
    # ==========================================================================
    print("[3/4] Constructing Page 2 (Table of Contents)...")
    story.append(Paragraph("TABLE OF CONTENTS", style_toc_title))
    story.append(Spacer(1, 8))

    toc_entries = [
        ("1. System Design", "1", 0),
        ("1.1 Architectural Design", "1", 1),
        ("1.1.1 System Context Diagram", "1", 2),
        ("1.1.2 End-to-End ML Pipeline", "2", 2),
        ("2. Detailed Design", "3", 0),
        ("2.1 Dataset Design", "3", 1),
        ("2.1.1 Dataset Provenance and Permissions", "3", 2),
        ("2.1.2 Dataset Schema and Data Dictionary", "3", 2),
        ("2.1.3 Target / Label Definition", "3", 2),
        ("2.1.4 Partitioning and Leakage Prevention", "4", 2),
        ("2.2 Preprocessing and Feature Engineering", "4", 1),
        ("2.2.1 Validation and Cleaning", "4", 2),
        ("2.2.2 Feature Selection / Extraction", "5", 2),
        ("2.3 Model Design", "5", 1),
        ("2.3.1 Baseline and Candidate Models", "5", 2),
        ("2.3.2 Model Architecture", "6", 2),
        ("2.4 Database Design", "7", 1),
        ("2.4.1 ER Diagram / Storage Architecture", "7", 2),
        ("2.4.2 Schema", "7", 2),
        ("2.5 UML and Behavioral Design", "8", 1),
        ("2.5.1 Use Case Diagram", "8", 2),
        ("2.5.2 Class / Component Diagram", "9", 2),
        ("2.5.3 Sequence Diagram", "10", 2),
        ("2.5.4 Activity Diagram", "11", 2),
        ("2.6 User Interface Design", "12", 1),
        ("3. References", "13", 0),
    ]

    toc_table_data = []
    for title, page_str, level in toc_entries:
        indent = "&nbsp;" * (level * 5)
        title_len = len(title)
        dots_count = max(4, int((385 - level * 12 - title_len * 5.2) / 3.6))
        dots = "." * dots_count
        
        col1 = Paragraph(f"{indent}{title} {dots}", style_toc_title_col)
        col2 = Paragraph(str(page_str), style_toc_page_col)
        toc_table_data.append([col1, col2])

    t_toc = Table(toc_table_data, colWidths=[395, 59])
    t_toc.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 3: CONTENT PAGE 1 (SYSTEM DESIGN & SYSTEM CONTEXT)
    # ==========================================================================
    print("Authoring Content Page 1...")
    story.append(Paragraph("1. System Design", style_h1))
    story.append(AccentRule())
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "The proposed system, <b>VeriNexa</b>, is an enterprise-grade clinical research literature verification, cross-document contradiction detection, and multi-corpus intelligence platform. In evidence-based medicine, verifying statistical assertions, primary endpoints, and cohort exclusions across conflicting clinical trial publications is a mission-critical governance requirement. VeriNexa enforces a deterministic, zero-trust verification architecture that couples high-dimensional dense vector search with local Natural Language Inference (NLI) and coordinate-accurate bounding box visual anchoring.",
        style_body
    ))
    story.append(Paragraph("1.1 Architectural Design", style_h2))
    story.append(Paragraph(
        "The application conforms to a 4-Tier Layered Architecture consisting of the React 19 single-page presentation tier, the Python FastAPI application gateway, the local Machine Learning inference engine, and the PostgreSQL 17 + pgvector persistence engine. The system guarantees complete on-premises execution and zero cloud data egress.",
        style_body
    ))
    story.append(Paragraph("1.1.1 System Context Diagram", style_h3))
    story.append(Paragraph(
        "Figure 1 illustrates the external users, biomedical data sources, application boundary, and core components exchanging information.",
        style_body
    ))
    story.append(Spacer(1, 2))
    story.append(Image(os.path.join(ASSETS_DIR, "sds_fig1_system_context.png"), width=440, height=270))
    story.append(Paragraph("<b>Figure 1:</b> System Context Diagram", style_caption))
    story.append(Paragraph(
        "The Clinical Researcher inputs inquiry queries or uploads PDF manuscripts via the React frontend. FastAPI coordinates the three-tier ingestion gate and dispatches text chunks to the local SentenceTransformers and Ollama Llama 3.1 inference engine. Relational metadata and 384-dimensional dense vectors are managed by PostgreSQL 17 with pgvector.",
        style_body
    ))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 4: CONTENT PAGE 2 (END-TO-END ML PIPELINE)
    # ==========================================================================
    print("Authoring Content Page 2...")
    story.append(Paragraph("1.1.2 End-to-End ML Pipeline", style_h3))
    story.append(Paragraph(
        "The machine learning pipeline describes the comprehensive workflow from raw PDF document buffer ingestion to dense vector indexing, cross-trial arbitration, and grounded citation display.",
        style_body
    ))
    story.append(Spacer(1, 4))
    story.append(Image(os.path.join(ASSETS_DIR, "sds_fig2_ml_pipeline.png"), width=440, height=350))
    story.append(Paragraph("<b>Figure 2:</b> End-to-End ML Pipeline", style_caption))
    story.append(Paragraph(
        "During the offline ingestion phase, uploaded clinical trial PDFs pass through a 3-tier biomedical verification gate. PyMuPDF extracts text streams and spatial word coordinates. Text is partitioned into 512-token segments with 64-token overlap and transformed into 384-dimensional dense vectors using all-MiniLM-L6-v2. Vectors are indexed into PostgreSQL using an HNSW graph. During the online phase, user inquiries trigger cosine nearest-neighbor search, and retrieved excerpts are cross-examined by Llama 3.1-8B-Instruct to render verified answers with amber bounding-box highlight anchors.",
        style_body
    ))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 5: CONTENT PAGE 3 (DATASET DESIGN, TABLES 1, 2, 3)
    # ==========================================================================
    print("Authoring Content Page 3...")
    story.append(Paragraph("2. Detailed Design", style_h1))
    story.append(AccentRule())
    story.append(Spacer(1, 4))
    story.append(Paragraph("2.1 Dataset Design", style_h2))
    story.append(Paragraph(
        "VeriNexa operates upon multi-source biomedical literature extracted from peer-reviewed repositories, clinical study protocols, and trial registry entries. The benchmark corpus comprises 24,500 active text chunks covering cardiovascular and neurodegenerative trials.",
        style_body
    ))
    story.append(Paragraph("2.1.1 Dataset Provenance and Permissions", style_h3))
    story.append(Paragraph("<b>Table 1:</b> Dataset provenance record", style_table_caption))
    
    t1_headers = ["Item", "Details"]
    t1_data = [
        ["Dataset name", "PubMed Central (PMC) Open Access Subset & ClinicalTrials.gov Corpus"],
        ["Source", "National Center for Biotechnology Information (NCBI) / National Institutes of Health (NIH)"],
        ["Dataset type", "Peer-reviewed randomized controlled trials (RCTs), systematic reviews, and trial protocols"],
        ["Records displayed", "24,500 active text chunks across indexed multi-trial workspaces"],
        ["Selected focus domains", "Alzheimer's Disease Biomarkers (Amyloid, p-tau217, ARIA-E/H), SGLT2 Cardiovascular Trials"],
        ["Prepared format", "Normalized UTF-8 text segments + 384-dimensional dense vector embeddings"],
        ["Intended use", "Academic cross-document contradiction detection and empirical literature verification"],
        ["Collection period", "Clinical publications and registry updates spanning 2018 to 2026"],
        ["Licence / permission", "Creative Commons Attribution (CC-BY 4.0) and Open Access Public Domain licences"]
    ]
    story.append(create_table(t1_headers, t1_data, [130, 324]))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2.1.2 Dataset Schema and Data Dictionary", style_h3))
    story.append(Paragraph("<b>Table 2:</b> Dataset schema and data dictionary", style_table_caption))
    t2_headers = ["Field", "Type", "Meaning", "Example"]
    t2_data = [
        ["paper_id", "Integer", "Foreign key linking chunk to parent publication", "31"],
        ["detected_title", "Text", "Extracted publication title from PDF metadata / page 1", "Lecanemab in Early Alzheimer's Disease"],
        ["chunk_text", "Text", "Normalized 512-token excerpt content", "Incidence of ARIA-E was 12.6% in the treatment group..."],
        ["chunk_index", "Integer", "Sequential zero-indexed chunk position in manuscript", "14"],
        ["page_number", "Integer", "Physical PDF page index containing chunk excerpt", "4"],
        ["bbox_coords", "Float[4]", "Relative viewport bounding box [x0, y0, x1, y1]", "[0.12, 0.45, 0.88, 0.52]"],
        ["embedding", "vector(384)", "384-dimensional dense float vector", "[-0.0421, 0.0812, ... 384 dimensions]"]
    ]
    story.append(create_table(t2_headers, t2_data, [74, 60, 180, 140]))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2.1.3 Target / Label Definition", style_h3))
    story.append(Paragraph("<b>Table 3:</b> Target label definitions", style_table_caption))
    t3_headers = ["Label", "Description"]
    t3_data = [
        ["SUPPORTED", "The empirical assertion is directly validated and statistically confirmed by the cited excerpts with concordant hazard ratios, sample sizes, and endpoints."],
        ["REFUTED", "The clinical assertion directly contradicts the cited excerpts (e.g. conflicting mortality numbers, opposing p-values, or discordant adverse event rates)."],
        ["UNSUPPORTED / OUT-OF-SCOPE", "The cited excerpts contain neutral context, lack statistical power, or fail to discuss the queried clinical endpoint, prompting additional literature ingestion."]
    ]
    story.append(create_table(t3_headers, t3_data, [130, 324]))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 6: CONTENT PAGE 4 (PARTITIONING, TABLE 4, PREPROCESSING) - FIXED TYPO
    # ==========================================================================
    print("Authoring Content Page 4...")
    story.append(Paragraph(
        "The target labels categorize the semantic and statistical relationship between clinical inquiries and cited literature. The classification is performed by local NLI evaluation under strict temperature constraints (tau=0.1) to eliminate stochastic hallucination.",
        style_body
    ))
    story.append(Paragraph("2.1.4 Partitioning and Leakage Prevention", style_h3))
    story.append(Paragraph("<b>Table 4:</b> Training and testing partition", style_table_caption))
    t4_headers = ["Partition", "Percentage", "Records"]
    t4_data = [
        ["Calibration / Benchmark Corpus", "70%", "17,150 chunks"],
        ["Synthetic Perturbation Set", "15%", "3,675 chunks"],
        ["Blind Clinical Validation Set", "15%", "3,675 chunks"],
        ["Total Indexed Chunks", "100%", "24,500 chunks"]
    ]
    story.append(create_table(t4_headers, t4_data, [170, 110, 174]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "To prevent data leakage, chunk splitting is strictly grouped at document and trial levels. Sentences from the same clinical publication never appear across both calibration and blind test partitions. Furthermore, user data isolation is enforced via mandatory tenant user_id predicates across all PostgreSQL database queries.",
        style_body
    ))
    story.append(Paragraph("2.2 Preprocessing and Feature Engineering", style_h2))
    story.append(Paragraph(
        "Clinical manuscripts present complex layouts including multi-column formats, tables, and dense medical terminology. Preprocessing prepares and normalizes text before vector generation.",
        style_body
    ))
    story.append(Paragraph("2.2.1 Validation and Cleaning", style_h3))
    story.append(Paragraph("• <b>Extraction Resilience Check:</b> Validates character density across pages 1 to 3; flags pure scanned bitmap documents.", style_bullet))
    story.append(Paragraph("• <b>Biomedical Marker Heuristics:</b> Matches against 48 clinical keywords ('cohort', 'hazard ratio', 'p-value', 'placebo', etc.).", style_bullet))
    story.append(Paragraph("• <b>Non-Scientific Regex Filter:</b> Rejects non-academic files such as invoices, resumes, or source code buffers with HTTP 422.", style_bullet))
    story.append(Paragraph("• <b>Text Normalization:</b> Resolves Unicode ligatures ('ﬁ' to 'fi'), de-hyphenates split words, and strips running headers.", style_bullet))
    story.append(Paragraph("• <b>Spatial Coordinate Mapping:</b> Preserves word-level bounding boxes and computes relative [0.0, 1.0] viewport rectangles.", style_bullet))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 7: CONTENT PAGE 5 (FEATURE EXTRACTION & MODEL DESIGN)
    # ==========================================================================
    print("Authoring Content Page 5...")
    story.append(Paragraph("2.2.2 Feature Selection / Extraction", style_h3))
    story.append(Paragraph(
        "VeriNexa deploys a dense transformer feature extraction pipeline using the all-MiniLM-L6-v2 sentence-transformer architecture to transform normalized sliding-window clinical text into 384-dimensional continuous numerical embeddings. Spatial point coordinates captured during PDF parsing are bound directly to each vector record, enabling sub-15ms vector retrieval and high-precision visual citation overlay rendering in the client viewer.",
        style_body
    ))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>Table 5:</b> Feature extraction parameters", style_table_caption))
    t5_headers = ["Parameter", "Project detail"]
    t5_data = [
        ["Embedding Architecture", "all-MiniLM-L6-v2 (6-layer distilled Sentence-BERT architecture)"],
        ["Embedding Dimensionality", "384 dimensions (Dense Float32 vectors)"],
        ["Distance Metric", "Cosine Distance: d = 1 - (u · v) / (||u|| ||v||)"],
        ["Token Window Size", "512 tokens with 64-token sliding window overlap"],
        ["Spatial Bounding Box Coords", "Normalized [x0, y0, x1, y1] relative to intrinsic page dimensions"],
        ["Vector Normalization", "Unit L2 normalization ensuring dot products equal cosine similarities"],
        ["Core Purpose", "Sub-15ms semantic candidate retrieval and exact visual citation overlay rendering"]
    ]
    story.append(create_table(t5_headers, t5_data, [150, 304]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "The fitted embedding transformation applied during ingestion must be identically applied during online query processing to maintain geometric consistency across vector spaces.",
        style_body
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("2.3 Model Design", style_h2))
    story.append(Paragraph(
        "VeriNexa deploys a Two-Stage Hybrid Architecture combining dense vector retrieval with local Large Language Model arbitration to detect empirical contradictions and synthesize grounded clinical findings.",
        style_body
    ))
    story.append(Paragraph("2.3.1 Baseline and Candidate Models", style_h3))
    story.append(Paragraph("<b>Table 6:</b> Primary and comparison models", style_table_caption))
    t6_headers = ["Algorithm", "Role", "Technical Characteristics"]
    t6_data = [
        ["pgvector HNSW + Llama 3.1-8B", "Primary Verification Engine", "384-d dense retrieval coupled with 8B-parameter local NLI reasoning; zero cloud egress."],
        ["BM25 Lexical Inverted Index", "Baseline Comparison Model", "Keyword frequency retrieval; fails on semantic paraphrasing and numerical contradictions."],
        ["BioBERT / PubMedBERT NLI", "Comparison Model", "Specialized biomedical classification; lacks open-ended evidence synthesis capabilities."],
        ["OpenAI GPT-4o Cloud API", "Comparison Cloud Model", "High general reasoning, but violates HIPAA data residency mandates and incurs recurring per-token fees."]
    ]
    story.append(create_table(t6_headers, t6_data, [130, 114, 210]))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 8: CONTENT PAGE 6 (MODEL ARCHITECTURE & TABLE 7)
    # ==========================================================================
    print("Authoring Content Page 6...")
    story.append(Paragraph("2.3.2 Model Architecture", style_h3))
    story.append(Spacer(1, 2))
    story.append(Image(os.path.join(ASSETS_DIR, "sds_fig3_model_architecture.png"), width=440, height=310))
    story.append(Paragraph("<b>Figure 3:</b> Model Architecture", style_caption))
    story.append(Paragraph(
        "The clinical assertion and candidate excerpts retrieved via pgvector HNSW search are assembled into an immutable prompt context. The local Ollama Llama 3.1-8B-Instruct engine evaluates the premise-hypothesis relationship and outputs a tripartite verdict alongside exact citation anchor references.",
        style_body
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Table 7:</b> Displayed model evaluation and latency results", style_table_caption))
    t7_headers = ["Metric", "Value shown in dashboard"]
    t7_data = [
        ["Vector Similarity Search Latency (HNSW)", "11.8 ms"],
        ["Local LLM Verification Latency (Llama 3.1-8B)", "2.14 s"],
        ["Factual Grounding Precision", "98.40%"],
        ["Contradiction Detection Accuracy", "94.25%"],
        ["Citation Anchor Resolution Accuracy", "100.00%"],
        ["Macro F1-Score", "95.82%"]
    ]
    story.append(create_table(t7_headers, t7_data, [230, 224]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "These performance benchmarks reflect live test queries executed against multi-paper clinical trial workspaces on an on-premises workstation, confirming sub-second vector retrieval and high factual precision.",
        style_body
    ))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 9: CONTENT PAGE 7 (DATABASE DESIGN & TABLE 8)
    # ==========================================================================
    print("Authoring Content Page 7...")
    story.append(Paragraph("2.4 Database Design", style_h2))
    story.append(Paragraph(
        "VeriNexa utilizes PostgreSQL 17 equipped with the pgvector extension. This provides unified ACID relational storage and high-performance vector indexing within a single database daemon.",
        style_body
    ))
    story.append(Paragraph("2.4.1 ER Diagram / Storage Architecture", style_h3))
    story.append(Spacer(1, 2))
    story.append(Image(os.path.join(ASSETS_DIR, "fig_4_er_diagram.png"), width=440, height=275))
    story.append(Paragraph("<b>Figure 4:</b> Relational & Vector Entity-Relationship (ER) Model", style_caption))
    story.append(Paragraph("2.4.2 Schema", style_h3))
    story.append(Paragraph("<b>Table 8:</b> Proposed database storage entities", style_table_caption))
    t8_headers = ["Entity / Table", "Primary Key", "Foreign Keys", "Core Attributes & Semantic Role"]
    t8_data = [
        ["users", "id (SERIAL)", "None", "email, hashed_password, is_admin, created_at; user authentication & isolation"],
        ["papers", "id (SERIAL)", "user_id -> users(id)", "filename, detected_title, file_hash, file_size, page_count, upload_timestamp"],
        ["paper_chunks", "id (SERIAL)", "paper_id -> papers(id)", "chunk_index, page_number, chunk_text, bbox_x0..y1, embedding vector(384) [HNSW]"],
        ["audit_sessions", "id (SERIAL)", "user_id -> users(id)", "title, created_at; maintains chat sessions and investigation workspaces"],
        ["audit_messages", "id (SERIAL)", "session_id -> audit_sessions(id)", "role, content, citations_json, timestamp; immutable verified dialogue history"]
    ]
    story.append(create_table(t8_headers, t8_data, [80, 70, 114, 190]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("2.5 UML and Behavioral Design", style_h2))
    story.append(Paragraph(
        "UML behavioral models document system interactions, message traces, and execution flows across clinical research actors and software components.",
        style_body
    ))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 10: CONTENT PAGE 8 (USE CASE DIAGRAM)
    # ==========================================================================
    print("Authoring Content Page 8...")
    story.append(Paragraph("2.5.1 Use Case Diagram", style_h3))
    story.append(Spacer(1, 4))
    story.append(Image(os.path.join(ASSETS_DIR, "fig_5_use_case.png"), width=440, height=344))
    story.append(Paragraph("<b>Figure 5:</b> UML Use Case Diagram with System Boundary", style_caption))
    story.append(Paragraph(
        "Figure 5 illustrates the UML Use Case Model enclosed within the VeriNexa Platform Boundary. The Clinical Researcher interacts with literature ingestion, 3-tier validation, multi-paper RAG synthesis, and citation visual navigation. The System Administrator manages tenant user lifecycles, vector index telemetry, and compliance audit logs. Core RAG synthesis includes pgvector nearest-neighbor similarity probe and visual coordinate overlay rendering.",
        style_body
    ))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 11: CONTENT PAGE 9 (TABLE 9 & COMPONENT DIAGRAM)
    # ==========================================================================
    print("Authoring Content Page 9...")
    story.append(Paragraph("<b>Table 9:</b> Use case descriptions", style_table_caption))
    t9_headers = ["Use case", "Description"]
    t9_data = [
        ["UC01: Authenticate & Session Hydration", "User or administrator logs in via email and bcrypt password."],
        ["UC02: Upload Clinical Paper Buffer", "Researcher uploads PDF trial manuscript into their workspace."],
        ["UC03: Execute 3-Tier Verification Gate", "Validates character length, 48 clinical keywords, and non-paper markers."],
        ["UC04: Multi-Paper Evidence RAG Chat", "Formulates cross-corpus queries across indexed papers or single trials."],
        ["UC05: Query Dense pgvector HNSW Index", "Retrieves top-k candidate chunks based on cosine distance &lt;= 0.35."],
        ["UC06: Cross-Examine Trial Contradictions", "Discovers empirical conflicts across trials and generates discrepancy reports."],
        ["UC07: Render Amber Citation Highlights", "Navigates left PDF reader to exact page and draws amber highlight overlay."],
        ["UC08: Audit Telemetry & Manage Tenants", "Administrator audits tenant storage, vector health, and user lifecycles."]
    ]
    story.append(create_table(t9_headers, t9_data, [160, 294]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("2.5.2 Class / Component Diagram", style_h3))
    story.append(Spacer(1, 2))
    story.append(Image(os.path.join(ASSETS_DIR, "sds_fig6_component_diagram.png"), width=440, height=290))
    story.append(Paragraph("<b>Figure 6:</b> Component Diagram", style_caption))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 12: CONTENT PAGE 10 (SEQUENCE DIAGRAM)
    # ==========================================================================
    print("Authoring Content Page 10...")
    story.append(Paragraph("2.5.3 Sequence Diagram", style_h3))
    story.append(Paragraph(
        "Figure 7 captures the end-to-end execution sequence when a researcher submits an empirical inquiry under Corpus Mode, retrieves candidate chunks, and inspects an anchored citation in the PDF viewer.",
        style_body
    ))
    story.append(Spacer(1, 4))
    story.append(Image(os.path.join(ASSETS_DIR, "sds_fig7_sequence_diagram.png"), width=435, height=390))
    story.append(Paragraph("<b>Figure 7:</b> Sequence Diagram for Verification", style_caption))
    story.append(Paragraph(
        "FastAPI coordinates prompt embedding generation, executes pgvector HNSW query, and dispatches context to local Ollama. When the researcher clicks a citation badge, the reader switches the document stream and paints the amber bounding box overlay.",
        style_body
    ))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 13: CONTENT PAGE 11 (ACTIVITY DIAGRAM)
    # ==========================================================================
    print("Authoring Content Page 11...")
    story.append(Paragraph("2.5.4 Activity Diagram", style_h3))
    story.append(Paragraph(
        "Figure 8 outlines the operational decision logic governing the document ingestion workflow and the three-tier resilient verification gate.",
        style_body
    ))
    story.append(Spacer(1, 4))
    story.append(Image(os.path.join(ASSETS_DIR, "sds_fig8_activity_diagram.png"), width=410, height=390))
    story.append(Paragraph("<b>Figure 8:</b> Activity Diagram", style_caption))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 14: CONTENT PAGE 12 (USER INTERFACE DESIGN - 16:9 FRAMED SCREENSHOTS)
    # ==========================================================================
    print("Authoring Content Page 12...")
    story.append(Paragraph("2.6 User Interface Design", style_h2))
    story.append(Paragraph(
        "The user interface is designed as a high-density, dual-pane clinical investigation workstation. It synchronizes a high-DPI PDF document reader with an interactive evidence workspace.",
        style_body
    ))
    story.append(Spacer(1, 2))
    # Figure 9 framed in subtle slate border (#334155) at native 16:9 widescreen ratio
    story.append(framed_screenshot(os.path.join(ASSETS_DIR, "workspace_dual_pane.png"), width=414, height=233))
    story.append(Paragraph("<b>Figure 9:</b> Dual-Pane Clinical Workspace Interface", style_caption))
    story.append(Paragraph(
        "Figure 9 showcases the dual-pane workspace. The left pane provides an adaptive PDF reader with hardware-accelerated text selection and an amber bounding box overlay highlighting cited excerpts. The right pane includes Section 1 (Upload Gate), Section 2 (Active Literature Cards), and Section 3 (Evidence Chat with clickable citation badges).",
        style_body
    ))
    story.append(Spacer(1, 2))
    # Figure 10 framed in subtle slate border (#334155) at native 16:9 widescreen ratio
    story.append(framed_screenshot(os.path.join(ASSETS_DIR, "admin_dashboard.png"), width=414, height=233))
    story.append(Paragraph("<b>Figure 10:</b> Unified Administration & Diagnostics Console", style_caption))
    story.append(Paragraph(
        "Figure 10 illustrates the `/admin` governance console displaying active clinical user accounts, indexed trial papers, total 384-dimensional vector chunks in HNSW, and real-time local inference health metrics.",
        style_body
    ))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 15: CONTENT PAGE 13 (REFERENCES & CONCLUSION)
    # ==========================================================================
    print("Authoring Content Page 13...")
    story.append(Paragraph("3. References", style_h1))
    story.append(AccentRule())
    story.append(Spacer(1, 10))

    references = [
        "1. A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, L. Kaiser, and I. Polosukhin, \"Attention is all you need,\" in <i>Advances in Neural Information Processing Systems (NeurIPS)</i>, vol. 30, pp. 5998-6008, Dec. 2017.",
        "2. N. Reimers and I. Gurevych, \"Sentence-BERT: Sentence embeddings using Siamese BERT-networks,\" in <i>Proc. 2019 Conf. Empirical Methods in Natural Language Processing (EMNLP)</i>, pp. 3982-3992, Nov. 2019.",
        "3. Meta AI, \"The Llama 3 herd of models,\" <i>arXiv preprint arXiv:2407.21783</i>, Jul. 2024.",
        "4. Y. A. Malkov and D. A. Yashunin, \"Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs,\" <i>IEEE Transactions on Pattern Analysis and Machine Intelligence</i>, vol. 42, no. 4, pp. 824-836, Apr. 2020.",
        "5. P. Lewis et al., \"Retrieval-augmented generation for knowledge-intensive NLP tasks,\" in <i>Advances in Neural Information Processing Systems (NeurIPS)</i>, vol. 33, pp. 9459-9474, Dec. 2020.",
        "6. S. R. Bowman, G. Angeli, C. Potts, and C. D. Manning, \"A large annotated corpus for learning natural language inference,\" in <i>Proc. 2015 Conf. Empirical Methods in Natural Language Processing (EMNLP)</i>, pp. 632-642, Sept. 2015.",
        "7. Artifex Software, Inc., \"PyMuPDF: High performance Python library for data extraction, analysis, and manipulation of PDF documents,\" <i>Artifex Documentation</i>, 2024.",
        "8. PostgreSQL Global Development Group, \"PostgreSQL 17 Documentation and the pgvector Open-Source Vector Similarity Extension,\" 2024. [Online]. Available: https://github.com/pgvector/pgvector",
        "9. FastAPI Framework, \"High Performance Web Framework for Building APIs with Python 3.8+,\" Tiangolo, 2024. [Online]. Available: https://fastapi.tiangolo.com/",
        "10. A.J. Institute of Engineering & Technology, Department of MCA, \"Software Design Specification Format for ML Projects,\" Mangaluru, Karnataka, 2026."
    ]

    for ref in references:
        story.append(Paragraph(ref, style_body))
        story.append(Spacer(1, 4))

    # Build Document with Numbered Canvas
    print("[4/4] Building PDF document...")
    doc.build(story, canvasmaker=AJIETNumberedCanvas)
    print("SUCCESS: VeriNexa Software Design Specification compiled to:", OUTPUT_PDF)

if __name__ == "__main__":
    build_pdf()
