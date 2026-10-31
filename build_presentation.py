import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

output_dir = "milestone1_deliverables"
os.makedirs(output_dir, exist_ok=True)
pptx_path = os.path.join(output_dir, "Milestone1_Presentation.pptx")

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette Constants
COLOR_NAVY = RGBColor(15, 23, 42)       # Slate 900
COLOR_BLUE_DARK = RGBColor(30, 58, 138) # Blue 900
COLOR_BLUE_ACCENT = RGBColor(14, 165, 233) # Sky 500
COLOR_TEAL = RGBColor(13, 148, 136)     # Teal 600
COLOR_GRAY_LIGHT = RGBColor(248, 250, 252) # Slate 50
COLOR_GRAY_CARD = RGBColor(241, 245, 249)  # Slate 100
COLOR_TEXT_DARK = RGBColor(15, 23, 42)
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_GREEN = RGBColor(22, 101, 52)
COLOR_RED = RGBColor(153, 27, 27)
COLOR_AMBER = RGBColor(180, 83, 9)

def add_header(slide, title_text, category_text="MILESTONE 1 REVIEW"):
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_cat = tf.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_BLUE_ACCENT
    
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_NAVY

def create_card(slide, left, top, width, height, bg_color=COLOR_GRAY_CARD, border_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5)
    else:
        shape.line.fill.background()
    return shape

# ==========================================
# SLIDE 1: TITLE SLIDE
# ==========================================
slide1 = prs.slides.add_slide(prs.slide_layouts[6])
bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
bg1.fill.solid()
bg1.fill.fore_color.rgb = COLOR_NAVY
bg1.line.fill.background()

title_box = slide1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(4.5))
tf1 = title_box.text_frame
tf1.word_wrap = True

p = tf1.paragraphs[0]
p.text = "AI PROJECT INTELLIGENCE & RISK ADVISOR"
p.font.size = Pt(36)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE

p2 = tf1.add_paragraph()
p2.text = "Milestone 1: Initial Project Planning, System Architecture & Setup Review"
p2.font.size = Pt(20)
p2.font.color.rgb = COLOR_BLUE_ACCENT
p2.space_before = Pt(12)

p3 = tf1.add_paragraph()
p3.text = "Final Year B.Tech Major Project Review  |  Academic Year 2026-2027"
p3.font.size = Pt(14)
p3.font.color.rgb = RGBColor(148, 163, 184)
p3.space_before = Pt(24)

p4 = tf1.add_paragraph()
p4.text = "Student Presenter: Manish  |  Department of Computer Science & Engineering"
p4.font.size = Pt(14)
p4.font.bold = True
p4.font.color.rgb = COLOR_WHITE
p4.space_before = Pt(16)

p5 = tf1.add_paragraph()
p5.text = "Scope: Days 1-4 Initial Planning, Architecture Design, Agile Backlog & Test Setup"
p5.font.size = Pt(12)
p5.font.color.rgb = COLOR_BLUE_ACCENT
p5.space_before = Pt(8)

slide1.notes_slide.notes_text_frame.text = (
    "Good morning/afternoon, respected faculty members and project evaluators. "
    "I am Manish, presenting Milestone 1 for my final-year B.Tech major project: "
    "'AI Project Intelligence & Risk Advisor'. "
    "This initial milestone review represents our first 3 to 4 days of project planning, "
    "architectural design, repository audit, and quality assurance framework setup. "
    "We have established realistic user stories, an initial sprint backlog, and foundational test specifications "
    "to govern our development in the upcoming milestones."
)

# ==========================================
# SLIDE 2: PROBLEM STATEMENT & MOTIVATION
# ==========================================
slide2 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide2, "Problem Statement & Industry Motivation", "BACKGROUND & CONTEXT")

card2_1 = create_card(slide2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0))
tf2_1 = card2_1.text_frame
tf2_1.word_wrap = True
tf2_1.margin_left = tf2_1.margin_right = tf2_1.margin_top = Inches(0.25)
p = tf2_1.paragraphs[0]
p.text = "Fragmented Project Knowledge"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf2_1.add_paragraph()
p_sub.text = "• Modern engineering teams manage artifacts across disparate formats: PDF contracts, DOCX minutes, CSV task backlogs, and plain text notes.\n• Key commitments, scope limits, and dependencies become buried in hundreds of unstructured pages.\n• Project managers spend 20-30% of their time manually cross-referencing documents."
p_sub.font.size = Pt(13)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(10)

card2_2 = create_card(slide2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0))
tf2_2 = card2_2.text_frame
tf2_2.word_wrap = True
tf2_2.margin_left = tf2_2.margin_right = tf2_2.margin_top = Inches(0.25)
p = tf2_2.paragraphs[0]
p.text = "Latent Risks & Schedule Slips"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf2_2.add_paragraph()
p_sub.text = "• Delivery risks and schedule slips are often identified too late, after milestones are already missed.\n• Lack of deterministic float and deadline monitoring leads to subjective, biased risk reporting.\n• Blocker items discussed in daily standups or retrospectives are frequently lost without designated owners."
p_sub.font.size = Pt(13)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(10)

card2_3 = create_card(slide2, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.0))
tf2_3 = card2_3.text_frame
tf2_3.word_wrap = True
tf2_3.margin_left = tf2_3.margin_right = tf2_3.margin_top = Inches(0.25)
p = tf2_3.paragraphs[0]
p.text = "LLM Hallucination Hazards"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf2_3.add_paragraph()
p_sub.text = "• Generic AI chatbots hallucinate deliverable dates, fabricate missing stakeholders, and generate unsubstantiated advice.\n• Enterprise project governance demands 100% auditability: every claim must cite exact source documents.\n• Need for an agentic, multi-stage RAG architecture with strict evidence-grounding constraints."
p_sub.font.size = Pt(13)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(10)

slide2.notes_slide.notes_text_frame.text = (
    "To understand our project's motivation, software projects routinely suffer from three main problems: "
    "fragmented project documents, hidden delivery risks that surface too late, and the risk of hallucination when using generic AI models. "
    "Our project addresses these challenges with a grounded RAG architecture, deterministic deadline tracking, and multi-agent reasoning."
)

# ==========================================
# SLIDE 3: PROJECT VISION & ARCHITECTURE OVERVIEW
# ==========================================
slide3 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide3, "Project Objectives & Proposed Solution Architecture", "SOLUTION DESIGN")

c3_1 = create_card(slide3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf3_1 = c3_1.text_frame
tf3_1.word_wrap = True
tf3_1.margin_left = tf3_1.margin_right = tf3_1.margin_top = Inches(0.25)
p = tf3_1.paragraphs[0]
p.text = "Key Project Objectives"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf3_1.add_paragraph()
p_sub.text = (
    "1. Multi-Format Ingestion: Robustly parse PDF, DOCX, CSV, and TXT files while retaining coordinate metadata (page numbers, table rows, timestamps).\n\n"
    "2. Grounded RAG Knowledge Base: Chunk, embed, and index artifacts into ChromaDB with strict project isolation.\n\n"
    "3. Multi-Agent Intelligence: Deploy LangGraph agents to extract scope, calculate deterministic and qualitative risks, and identify blockers.\n\n"
    "4. Transparent Project Health Score: Compute an objective, reproducible 0-100 metric with missing-data penalties.\n\n"
    "5. Grounded Conversational Assistant: Stakeholder chat interface citing exact source chunks with refusal on missing evidence."
)
p_sub.font.size = Pt(12)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

c3_2 = create_card(slide3, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf3_2 = c3_2.text_frame
tf3_2.word_wrap = True
tf3_2.margin_left = tf3_2.margin_right = tf3_2.margin_top = Inches(0.25)
p = tf3_2.paragraphs[0]
p.text = "Proposed Technology Stack"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf3_2.add_paragraph()
p_sub.text = (
    "• Frontend User Interface:\n"
    "  React 19 + TypeScript + Vite + Tailwind CSS + Lucide Icons + Recharts.\n\n"
    "• Backend Microservice:\n"
    "  FastAPI (Python 3.13) + Uvicorn + Pydantic v2 schemas.\n\n"
    "• Vector Database & Retrieval:\n"
    "  ChromaDB (Local persistent) + Sentence Transformers embeddings.\n\n"
    "• Agent Orchestration Framework:\n"
    "  LangGraph stateful workflow graphs + Google Gemini / Claude LLM nodes.\n\n"
    "• Document Engineering:\n"
    "  PyMuPDF (fitz) for PDF, python-docx for Word, pandas for CSV data."
)
p_sub.font.size = Pt(12)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

slide3.notes_slide.notes_text_frame.text = (
    "Here we see our planned solution architecture and technology stack: FastAPI with Python 3.13, "
    "ChromaDB for vector storage, LangGraph for multi-agent workflows, and React with TypeScript for the frontend dashboard."
)

# ==========================================
# SLIDE 4: ACTUAL REPOSITORY AUDIT
# ==========================================
slide4 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide4, "Actual Repository Audit & Baseline Verification", "PHYSICAL EVIDENCE")

c4_1 = create_card(slide4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf4_1 = c4_1.text_frame
tf4_1.word_wrap = True
tf4_1.margin_left = tf4_1.margin_right = tf4_1.margin_top = Inches(0.25)
p = tf4_1.paragraphs[0]
p.text = "Exhaustive Workspace Directory Tree"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY

p_sub = tf4_1.add_paragraph()
p_sub.text = (
    "Target Location: C:\\Users\\manis\\Desktop\\SP\\\n\n"
    "Directory Tree (PowerShell Get-ChildItem -Recurse -Force):\n"
    "C:\\Users\\manis\\Desktop\\SP\\\n"
    "│\n"
    "├── Agile_Template_v0.1.xls           (205 KB)\n"
    "├── Defect_Tracker Template_v0.1.xlsx (19.8 KB)\n"
    "└── Unit_Test_Plan_v0.1.xlsx          (11.8 KB)\n\n"
    "Physical Audit Verdict:\n"
    "• Exactly 3 files detected; 0 subdirectories.\n"
    "• No frontend or backend source code currently exists.\n"
    "• Git repository is uninitialized (fatal: not a git repo).\n"
    "• No fabricated files or mock fallbacks introduced."
)
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

c4_2 = create_card(slide4, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf4_2 = c4_2.text_frame
tf4_2.word_wrap = True
tf4_2.margin_left = tf4_2.margin_right = tf4_2.margin_top = Inches(0.25)
p = tf4_2.paragraphs[0]
p.text = "Initial Setup & Remediation Strategy"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY

p_sub = tf4_2.add_paragraph()
p_sub.text = (
    "• Starting State:\n"
    "  The project workspace is at Days 1-4 of initial setup. The 3 original spreadsheets contained template structures from earlier projects.\n\n"
    "• Clean Deliverables Generation:\n"
    "  We preserved the original files and created verified, project-specific deliverables in 'milestone1_deliverables/':\n"
    "  1. Agile_Template_Milestone1.xlsx (6 stories, 7 initial sprint tasks)\n"
    "  2. Defect_Tracker_Milestone1.xlsx (1 genuine setup observation, ready for QA)\n"
    "  3. Unit_Test_Plan_Milestone1.xlsx (7 basic test cases for initial verification)\n\n"
    "• Milestone 1 Positioning:\n"
    "  Transparently presented as Days 1-4: Project Inception, System Architecture Blueprint & QA Governance."
)
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

slide4.notes_slide.notes_text_frame.text = (
    "In Slide 4, we present the physical reality of our repository. "
    "A PowerShell audit confirmed that exactly three spreadsheet files existed. "
    "We have established clean, verified project management workbooks representing 3-4 days of initial planning and setup, "
    "saving them in milestone1_deliverables/."
)

# ==========================================
# SLIDE 5: SYSTEM ARCHITECTURE & END-TO-END WORKFLOW
# ==========================================
slide5 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide5, "System Architecture & Component Implementation State", "SYSTEM ARCHITECTURE")

layers = [
    ("1. Data Ingestion Layer", "• PDF (PyMuPDF)\n• DOCX (python-docx)\n• CSV / TXT (pandas)\n• MIME & Size Validator\n• Coordinate Tracking", "STATUS: PLANNED\n(Initial Design Done)", COLOR_AMBER),
    ("2. Vector Store & RAG", "• Recursive Text Chunker\n  (800 char / 150 overlap)\n• Dense Embeddings\n• ChromaDB Persistence\n• Project-ID Isolation Filter", "STATUS: PLANNED\n(Architecture Done)", COLOR_AMBER),
    ("3. LangGraph Agents", "• Scope Extraction Node\n• Risk & Slip Engine\n• Blocker / Action Items\n• Documentation Generator\n• UNKNOWN Fallbacks", "STATUS: PLANNED\n(Sprint 2 Target)", COLOR_AMBER),
    ("4. API & Health Scorer", "• FastAPI REST Router\n• Deterministic Formula\n  (0-100 Health Score)\n• Missing-Data Penalties\n• Grounded /chat Route", "STATUS: PLANNED\n(Sprint 2/3 Target)", COLOR_AMBER),
    ("5. UI & Governance", "• React 19 Dashboard\n• Risk Heatmap / KPIs\n• Chat Assistant Drawer\n• Agile Backlog (Verified)\n• Test Plan (Verified)", "STATUS: PARTIAL\n(Planning Complete)", COLOR_BLUE_ACCENT)
]

for idx, (title, details, status, col) in enumerate(layers):
    x = Inches(0.8 + idx * 2.38)
    card = create_card(slide5, x, Inches(1.8), Inches(2.25), Inches(5.0))
    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.15)
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    
    p_body = tf.add_paragraph()
    p_body.text = details
    p_body.font.size = Pt(10)
    p_body.font.color.rgb = COLOR_TEXT_DARK
    p_body.space_before = Pt(8)
    
    p_stat = tf.add_paragraph()
    p_stat.text = status
    p_stat.font.size = Pt(9)
    p_stat.font.bold = True
    p_stat.font.color.rgb = col
    p_stat.space_before = Pt(14)

slide5.notes_slide.notes_text_frame.text = (
    "Slide 5 illustrates our 5-tier architecture. "
    "Our project management foundations and system specifications are verified, while code implementation for each tier is scheduled across upcoming sprints."
)

# ==========================================
# SLIDE 6: DOCUMENT INGESTION & RAG PIPELINE
# ==========================================
slide6 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide6, "Document Ingestion & Grounded RAG Pipeline Architecture", "MODULES 1 & 2")

c6_1 = create_card(slide6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf6_1 = c6_1.text_frame
tf6_1.word_wrap = True
tf6_1.margin_left = tf6_1.margin_right = tf6_1.margin_top = Inches(0.25)
p = tf6_1.paragraphs[0]
p.text = "Module 1: Ingestion & Parsing Strategy"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf6_1.add_paragraph()
p_sub.text = (
    "• Multi-Format Parsing Engines:\n"
    "  - PDF: PyMuPDF (fitz) extracts text blocks while tracking exact page numbers.\n"
    "  - DOCX: python-docx serializes heading hierarchies, paragraphs, and 4-column tables.\n"
    "  - CSV: pandas transforms tabular sprint backlogs into structured row entities.\n"
    "  - TXT: UTF-8 stream reader maintaining line-level indexes.\n\n"
    "• Document Validation Service:\n"
    "  - MIME type verification rejects unsupported formats (.exe, .zip).\n"
    "  - File size capping (max 25MB per document) prevents memory exhaustion.\n"
    "  - Graceful error handling for corrupted and password-protected files."
)
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

c6_2 = create_card(slide6, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf6_2 = c6_2.text_frame
tf6_2.word_wrap = True
tf6_2.margin_left = tf6_2.margin_right = tf6_2.margin_top = Inches(0.25)
p = tf6_2.paragraphs[0]
p.text = "Module 2: RAG Pipeline & ChromaDB Indexing"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf6_2.add_paragraph()
p_sub.text = (
    "• Semantic Chunking Configuration:\n"
    "  - Recursive character text splitter: Chunk Size = 800 chars, Overlap = 150 chars.\n"
    "  - Boundary preservation keeps sentences and paragraphs intact.\n\n"
    "• Dense Vector Embeddings:\n"
    "  - Sentence Transformers (all-MiniLM-L6-v2) or Gemini Embeddings (768-dim).\n\n"
    "• ChromaDB Collection Schema & Multi-Tenancy:\n"
    "  - Persistent local vector store in backend/data/chroma/.\n"
    "  - Multi-tenant isolation: every chunk tagged with {project_id, file_id, page}.\n"
    "  - All queries strictly enforce where={'project_id': project_id} to prevent cross-project data leakage."
)
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

slide6.notes_slide.notes_text_frame.text = (
    "Slide 6 explains our planned document parsing and RAG pipeline. "
    "We plan to support PDF, DOCX, CSV, and TXT, preserving page numbers so that every AI insight cites its original source."
)

# ==========================================
# SLIDE 7: LANGGRAPH MULTI-AGENT ORCHESTRATION
# ==========================================
slide7 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide7, "LangGraph Multi-Agent Orchestration Engine", "MODULES 3, 4, 5, 6")

c7_1 = create_card(slide7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.4))
tf = c7_1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.2)
p = tf.paragraphs[0]
p.text = "Module 3: Scope Extraction Agent"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf.add_paragraph()
p_sub.text = "• Extracts project goals, in-scope/out-of-scope declarations, and milestone deliverables.\n• Outputs structured Pydantic JSON; every item references source page & chunk ID."
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(4)

c7_2 = create_card(slide7, Inches(6.8), Inches(1.8), Inches(5.6), Inches(2.4))
tf = c7_2.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.2)
p = tf.paragraphs[0]
p.text = "Module 4: Risk & Schedule Slip Agent"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf.add_paragraph()
p_sub.text = "• Dual-engine design: deterministic deadline delta engine calculates negative float & slips.\n• LLM identifies qualitative risks; assigns Likelihood (1-5) and Impact (1-5) on a 5x5 matrix."
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(4)

c7_3 = create_card(slide7, Inches(0.8), Inches(4.4), Inches(5.6), Inches(2.4))
tf = c7_3.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.2)
p = tf.paragraphs[0]
p.text = "Module 5: Blocker & Action Items Agent"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf.add_paragraph()
p_sub.text = "• Parses standup notes and minutes to detect active blockers and assigned action items.\n• Anti-hallucination constraint: maps missing owners or due dates to 'UNKNOWN' rather than inventing names."
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(4)

c7_4 = create_card(slide7, Inches(6.8), Inches(4.4), Inches(5.6), Inches(2.4))
tf = c7_4.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.2)
p = tf.paragraphs[0]
p.text = "Module 6: Documentation Generation Agent"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf.add_paragraph()
p_sub.text = "• Synthesizes project artifacts: User Stories with acceptance criteria and tabular Risk Registers.\n• Mandatory disclaimer header: 'DRAFT - Generated by AI'; all claims cite ingested chunk IDs."
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(4)

slide7.notes_slide.notes_text_frame.text = (
    "Slide 7 describes our four specialized AI agents. "
    "These will be built in upcoming sprints using LangGraph: Scope Extraction, Risk & Schedule Slip Detection, Blocker Identification, and Documentation Generation."
)

# ==========================================
# SLIDE 8: HEALTH SCORING & CHAT ASSISTANT
# ==========================================
slide8 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide8, "Objective Health Scoring & Grounded Chatbot Assistant", "MODULES 7 & 8")

c8_1 = create_card(slide8, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf = c8_1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Module 7: Deterministic Health Formula"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf.add_paragraph()
p_sub.text = (
    "• Transparent Mathematical Scoring (0-100):\n"
    "  Health Score = 100 - [Ws·P(schedule) + Wr·P(risk) + Wb·P(blocker) + Wd·P(missing_data)]\n\n"
    "• Metric Weights:\n"
    "  - Ws = 0.35 (Schedule: Overdue tasks & negative float)\n"
    "  - Wr = 0.30 (Risk Severity: Critical & High severity risks)\n"
    "  - Wb = 0.20 (Blocker Volume: Active unresolved blockers)\n"
    "  - Wd = 0.15 (Documentation Coverage: Missing baseline specs)\n\n"
    "• Conservative Missing-Data Handling:\n"
    "  If a project uploads no risk register, the system penalizes missing data rather than treating absent documentation as 100% healthy."
)
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

c8_2 = create_card(slide8, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf = c8_2.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Module 8: Conversational Assistant"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf.add_paragraph()
p_sub.text = (
    "• Grounded Context Injection:\n"
    "  - Retrieves top-k matching chunks from ChromaDB for the active project.\n"
    "  - Injects retrieved text into strict system prompt with source coordinates.\n\n"
    "• Interactive Source Citations:\n"
    "  - Every factual answer appends verifiable citation badges (e.g., '[Charter.pdf, p. 4]').\n\n"
    "• Explicit Refusal Guardrail:\n"
    "  - When retrieval similarity falls below confidence threshold, the assistant states:\n"
    "    'I cannot find evidence regarding this in the uploaded project documents.'\n"
    "  - Completely prevents hallucinated answers on unaddressed topics."
)
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

slide8.notes_slide.notes_text_frame.text = (
    "Slide 8 outlines our health scoring formula and conversational assistant design. "
    "Health scoring is formulaic and transparent, while the conversational assistant is strictly grounded with refusal behavior when evidence is absent."
)

# ==========================================
# SLIDE 9: NINE-MODULE STATUS TABLE
# ==========================================
slide9 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide9, "Nine-Module Implementation Status Matrix", "IMPLEMENTATION AUDIT")

rows, cols = 10, 5
table_shape = slide9.shapes.add_table(rows, cols, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.1))
tbl = table_shape.table

tbl.columns[0].width = Inches(0.8)  # Mod #
tbl.columns[1].width = Inches(3.2)  # Name
tbl.columns[2].width = Inches(1.8)  # Status
tbl.columns[3].width = Inches(3.4)  # Verification
tbl.columns[4].width = Inches(2.533) # Sprint

headers = ["#", "Module Name", "Milestone 1 Status", "Physical Verification Performed", "Target Sprint"]
for c_idx, h in enumerate(headers):
    cell = tbl.cell(0, c_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLOR_NAVY
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER

matrix_data = [
    ("M01", "Document Ingestion & Parsing", "Planned", "Directory scan: 0 parser files found. Host lacks fitz/docx.", "Sprint 1 Setup"),
    ("M02", "RAG Pipeline & ChromaDB Indexing", "Planned", "Verified chromadb missing from environment; 0 indexers.", "Sprint 2 Target"),
    ("M03", "Scope & Deliverable Extraction", "Planned", "Checked for LangGraph graph definitions; 0 agent files.", "Sprint 2 Target"),
    ("M04", "Risk Detection & Schedule Slips", "Planned", "Checked for risk calculation formulas; 0 rule engines.", "Sprint 2 Target"),
    ("M05", "Blocker & Action Item Extraction", "Planned", "Scanned for entity extractors & schemas; 0 parsers.", "Sprint 2 Target"),
    ("M06", "Documentation Generation Agent", "Planned", "Scanned for report generators & templates; 0 builders.", "Sprint 3 Target"),
    ("M07", "Project Health Scoring Formula", "Planned", "Scanned for metric weight calculators; 0 scoring engines.", "Sprint 3 Target"),
    ("M08", "Conversational Project Assistant", "Planned", "Checked for /chat routes & memory buffers; 0 endpoints.", "Sprint 3 Target"),
    ("M09", "Insights & Risk React Dashboard", "Planned", "Node 22 present; verified 0 React components or configs.", "Sprint 3/4 Target")
]

for r_idx, row in enumerate(matrix_data):
    for c_idx, val in enumerate(row):
        cell = tbl.cell(r_idx + 1, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_WHITE if r_idx % 2 == 0 else COLOR_GRAY_CARD
        p = cell.text_frame.paragraphs[0]
        p.text = val
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_DARK
        if c_idx == 2:
            p.font.bold = True
            p.font.color.rgb = COLOR_AMBER
            p.alignment = PP_ALIGN.CENTER
        elif c_idx in (0, 4):
            p.alignment = PP_ALIGN.CENTER

slide9.notes_slide.notes_text_frame.text = (
    "Slide 9 displays our status matrix for all nine modules. "
    "At this early 3-4 day stage, all functional modules are marked Planned as we establish our foundation."
)

# ==========================================
# SLIDE 10: SIMPLIFIED AGILE PLANNING (3-4 DAYS SCOPE)
# ==========================================
slide10 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide10, "Agile Planning: Initial Setup & Planning (Days 1 to 4)", "AGILE FRAMEWORK")

c10_1 = create_card(slide10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf = c10_1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Product Backlog (6 Initial Stories)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf.add_paragraph()
p_sub.text = (
    "• Populated Deliverable: Agile_Template_Milestone1.xlsx\n\n"
    "• 6 Simple, Foundational User Stories:\n"
    "  - US-01: Set up project repository & environments (In Progress)\n"
    "  - US-02: Design system architecture & module boundaries (Completed)\n"
    "  - US-03: Define supported document formats & validation (In Progress)\n"
    "  - US-04: Prepare document upload & ingestion workflow (Planned)\n"
    "  - US-05: Plan RAG knowledge base & vector store (Planned)\n"
    "  - US-06: Design initial dashboard layout wireframes (Planned)\n\n"
    "• MoSCoW Prioritization:\n"
    "  Clear separation of Must Have setup tasks from future Should/Could Have features."
)
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

c10_2 = create_card(slide10, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf = c10_2.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Sprint 1 Backlog (7 Tasks, 22 Hours Total)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf.add_paragraph()
p_sub.text = (
    "• Realistic Initial Effort (Days 1 to 4):\n"
    "  - T-01: Repository & folder structure setup (2.0 hrs, Completed)\n"
    "  - T-02: Dependency survey & configuration (2.5 hrs, Completed)\n"
    "  - T-03: System architecture & data flow design (4.0 hrs, Completed)\n"
    "  - T-04: Initial API route design & schemas (3.5 hrs, In Progress)\n"
    "  - T-05: Document ingestion & validation design (3.0 hrs, In Progress)\n"
    "  - T-06: Basic test plan & test setup (3.0 hrs, Completed)\n"
    "  - T-07: Milestone 1 review documentation (4.0 hrs, Completed)\n\n"
    "• Total Initial Effort: 22.0 Hours across 4 days.\n"
    "• Stand-up Meeting: Day 1 kick-off recorded; upcoming meetings planned.\n"
    "• Retrospective: Sheet labeled 'Initial Sprint Retrospective - Pending'."
)
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

slide10.notes_slide.notes_text_frame.text = (
    "Slide 10 highlights our revised, realistic Agile workbook. "
    "We established six foundational user stories covering repository setup, architecture, and document formats. "
    "Our Sprint 1 backlog contains seven initial tasks totaling 22 hours across the first 3 to 4 days, "
    "representing a genuine, manageable early planning sprint."
)

# ==========================================
# SLIDE 11: SIMPLIFIED DEFECT TRACKING FRAMEWORK
# ==========================================
slide11 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide11, "Defect Tracking & Initial Quality Setup", "DEFECT TRACKER")

c11_1 = create_card(slide11, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
tf = c11_1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Lightweight Defect Register: Defect_Tracker_Milestone1.xlsx"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY

p_sub = tf.add_paragraph()
p_sub.text = (
    "• Practical Early-Stage Approach: No hypothetical or fabricated defects are logged.\n"
    "• The defect tracker is set up with standard categories (Logical, User Interface, Maintainability, Standards, Others).\n"
    "• Exactly 1 real observation from our initial repository inspection is logged with status OPEN; the tracker is clean and ready for QA testing during development."
)
p_sub.font.size = Pt(11.5)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

# Table inside card
rows, cols = 2, 6
def_table = slide11.shapes.add_table(rows, cols, Inches(1.0), Inches(3.6), Inches(11.333), Inches(2.2)).table
def_table.columns[0].width = Inches(0.6)  # ID
def_table.columns[1].width = Inches(1.8)  # Type
def_table.columns[2].width = Inches(3.8)  # Description
def_table.columns[3].width = Inches(3.2)  # Action Taken / Planned
def_table.columns[4].width = Inches(1.0)  # Status
def_table.columns[5].width = Inches(0.933) # Assignee

def_headers = ["ID", "Defect Type", "Observed Defect Description", "Action Taken / Planned Remediation", "Status", "Owner"]
for c_idx, h in enumerate(def_headers):
    cell = def_table.cell(0, c_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLOR_NAVY
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER

def_rows = [
    ("D-01", "Maintainability", "Workspace repository is not yet initialized in Git and lacks dedicated virtual environment.", "Documented in repository audit; scheduled Git initialization and virtual environment creation in initial setup tasks.", "Open", "Manish")
]

for r_idx, row in enumerate(def_rows):
    for c_idx, val in enumerate(row):
        cell = def_table.cell(r_idx + 1, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_WHITE
        p = cell.text_frame.paragraphs[0]
        p.text = val
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_TEXT_DARK
        if c_idx == 4:
            p.font.bold = True
            p.font.color.rgb = COLOR_RED
            p.alignment = PP_ALIGN.CENTER
        elif c_idx in (0, 5):
            p.alignment = PP_ALIGN.CENTER

slide11.notes_slide.notes_text_frame.text = (
    "Slide 11 shows our lightweight defect tracker. "
    "Rather than creating fake bugs, we logged the single real setup observation from our audit: "
    "that our Git repository and virtual environment were not yet initialized. "
    "The remaining rows are clean and formatted, ready for QA logging during upcoming development."
)

# ==========================================
# SLIDE 12: SIMPLIFIED UNIT TEST PLAN (7 RELEVANT TESTS)
# ==========================================
slide12 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide12, "Unit Test Plan: Initial Setup & Verification (7 Cases)", "TEST ENGINEERING")

c12_1 = create_card(slide12, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
tf = c12_1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Foundational Unit Test Specifications (Unit_Test_Plan_Milestone1.xlsx)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf.add_paragraph()
p_sub.text = (
    "• Focused Scope: 7 basic, relevant test cases designed to verify setup, servers, and initial validation.\n"
    "• Execution Status Truth: All 7 tests have Actual Result stated as 'Not executed' and Test Status marked 'Not Run' (highlighted amber).\n"
    "• No false claims of completed AI testing prior to code development."
)
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(6)

rows, cols = 8, 4
ut_table = slide12.shapes.add_table(rows, cols, Inches(1.0), Inches(3.2), Inches(11.333), Inches(3.2)).table
ut_table.columns[0].width = Inches(1.2)  # ID
ut_table.columns[1].width = Inches(3.8)  # Test Case Name
ut_table.columns[2].width = Inches(4.533) # Expected Result
ut_table.columns[3].width = Inches(1.8)  # Status

ut_headers = ["Test ID", "Test Case Name & Objective", "Expected Result", "Status"]
for c_idx, h in enumerate(ut_headers):
    cell = ut_table.cell(0, c_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLOR_NAVY
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER

ut_rows = [
    ("TC-01", "Frontend Dev Server Startup (npm run dev)", "Vite dev server starts and listens on http://localhost:5173", "Not Run"),
    ("TC-02", "FastAPI Backend Server Startup (uvicorn main:app)", "Uvicorn boots ASGI application on http://127.0.0.1:8000", "Not Run"),
    ("TC-03", "Backend Health Endpoint Response (GET /health)", "HTTP 200 OK returned with JSON {'status': 'ok'}", "Not Run"),
    ("TC-04", "Supported Document Format Identification (.pdf, .docx, .csv, .txt)", "Whitelisted extensions recognized and permitted for upload", "Not Run"),
    ("TC-05", "Invalid Document Format Rejection (.exe, .zip, .png)", "Disallowed file extensions rejected with HTTP 415 error", "Not Run"),
    ("TC-06", "ChromaDB Vector Store Local Connection", "Persistent client initializes and creates/connects to collection", "Not Run"),
    ("TC-07", "Automated Pytest Test Runner Discovery", "Pytest detects test files in tests/ and executes assertions", "Not Run")
]

for r_idx, row in enumerate(ut_rows):
    for c_idx, val in enumerate(row):
        cell = ut_table.cell(r_idx + 1, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_WHITE if r_idx % 2 == 0 else COLOR_GRAY_CARD
        p = cell.text_frame.paragraphs[0]
        p.text = val
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_DARK
        if c_idx == 3:
            p.font.bold = True
            p.font.color.rgb = COLOR_AMBER
            p.alignment = PP_ALIGN.CENTER
        elif c_idx == 0:
            p.alignment = PP_ALIGN.CENTER

slide12.notes_slide.notes_text_frame.text = (
    "Slide 12 covers our simplified Unit Test Plan. "
    "We defined seven foundational test cases covering frontend startup, backend startup, the health check endpoint, "
    "file format validation, invalid format rejection, ChromaDB initialization, and pytest test discovery. "
    "All seven are honestly marked 'Not Run' with actual results recorded as 'Not executed'."
)

# ==========================================
# SLIDE 13: TEST REPORT & GENUINE RESULTS
# ==========================================
slide13 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide13, "Milestone 1 Physical Verification & Command Outputs", "TEST EVIDENCE")

c13_1 = create_card(slide13, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf = c13_1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Actual Terminal Command Executions"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf.add_paragraph()
p_sub.text = (
    "1. Pytest Test Discovery:\n"
    "   Command: python -m pytest\n"
    "   Output: collected 0 items / no tests ran in 0.01s (Exit Code 1)\n\n"
    "2. Backend API Server Launch:\n"
    "   Command: python -m uvicorn main:app --port 8000\n"
    "   Output: ERROR: Could not import module 'main' (Exit Code 1)\n\n"
    "3. Frontend Test Runner:\n"
    "   Command: npm test\n"
    "   Output: Error: no test specified (Exit Code 1)\n\n"
    "4. Python Package Availability Check:\n"
    "   chromadb: NOT found  |  langgraph: NOT found\n"
    "   openpyxl: available  |  fastapi: available"
)
p_sub.font.size = Pt(10.5)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

c13_2 = create_card(slide13, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf = c13_2.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Evidence Artifacts for Faculty Inspection"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf.add_paragraph()
p_sub.text = (
    "• Genuine Deliverables Generated & Ready for Live Inspection:\n\n"
    "  1. MILESTONE1_REPOSITORY_AUDIT.md:\n"
    "     Complete forensic report of workspace C:\\Users\\manis\\Desktop\\SP.\n\n"
    "  2. MILESTONE1_MODULE_STATUS.md:\n"
    "     In-depth 9-module technical status and gap analysis.\n\n"
    "  3. MILESTONE1_TEST_REPORT.md:\n"
    "     Documented test results, raw outputs, and remediation roadmap.\n\n"
    "  4. Populated Excel Workbooks in milestone1_deliverables/:\n"
    "     Agile Backlog, Defect Tracker, and Unit Test Plan workbooks.\n\n"
    "  5. MILESTONE1_DEMO_GUIDE.md:\n"
    "     Step-by-step presentation script and faculty Q&A guide."
)
p_sub.font.size = Pt(10.5)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

slide13.notes_slide.notes_text_frame.text = (
    "Slide 13 provides the raw terminal logs from our verification tests, documented in MILESTONE1_TEST_REPORT.md. "
    "We ran pytest, uvicorn, and npm test directly from PowerShell to verify our baseline environment."
)

# ==========================================
# SLIDE 14: LIMITATIONS & TECHNICAL RISKS
# ==========================================
slide14 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide14, "Current Limitations & Technical Risk Management", "RISK ANALYSIS")

c14_1 = create_card(slide14, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf = c14_1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Observed Technical Limitations"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf.add_paragraph()
p_sub.text = (
    "1. Missing Version Control Repository:\n"
    "   - Workspace lacks .git directory; version control history must be initialized before multi-developer collaboration.\n\n"
    "2. Host Environment Package Gaps:\n"
    "   - Core packages (chromadb, langgraph, python-docx) must be installed within an isolated virtual environment (.venv).\n\n"
    "3. Absence of Sample Project Corpus:\n"
    "   - The workspace currently contains no sample project documents (PDF charters, SOWs, meeting minutes) to benchmark extraction accuracy.\n\n"
    "4. API & UI Non-Execution:\n"
    "   - Web server and dashboard cannot run until backend scaffolding and frontend Vite scaffolding are executed in Sprint 1."
)
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

c14_2 = create_card(slide14, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf = c14_2.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Risk Mitigation & Remediation Roadmap"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf.add_paragraph()
p_sub.text = (
    "• Mitigation for Version Control (Sprint 1):\n"
    "  Run git init, configure comprehensive .gitignore, and commit initial structure.\n\n"
    "• Mitigation for Dependencies (Sprint 1):\n"
    "  Create requirements.txt with pinned versions; build dedicated virtual environment.\n\n"
    "• Mitigation for Sample Corpus (Sprint 1):\n"
    "  Curate test_data/ folder containing realistic project artifacts across all 4 formats.\n\n"
    "• Mitigation for API & UI:\n"
    "  Follow sequenced Sprint Backlog to build Ingestion -> RAG -> Agents -> UI."
)
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

slide14.notes_slide.notes_text_frame.text = (
    "Slide 14 outlines our technical risk management. "
    "We have identified four primary constraints and scheduled concrete remediation tasks in our setup backlog."
)

# ==========================================
# SLIDE 15: CONCLUSION & ROADMAP
# ==========================================
slide15 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide15, "Conclusion & Next Milestone Plan", "CONCLUSION & NEXT STEPS")

c15_1 = create_card(slide15, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf = c15_1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Milestone 1 Deliverables Summary"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf.add_paragraph()
p_sub.text = (
    "• Physical Repository Audit Completed:\n"
    "  MILESTONE1_REPOSITORY_AUDIT.md documents exact workspace baseline.\n\n"
    "• Comprehensive Module Audit Completed:\n"
    "  MILESTONE1_MODULE_STATUS.md maps all 9 modules with technical plans.\n\n"
    "• Authentic Verification & Test Report:\n"
    "  MILESTONE1_TEST_REPORT.md logs command executions and defects.\n\n"
    "• Simplified Project Management Workbooks (3-4 Days Scope):\n"
    "  Agile Backlog, Defect Tracker, and Unit Test Plan populated realistically.\n\n"
    "• Faculty Demonstration Guide Ready:\n"
    "  MILESTONE1_DEMO_GUIDE.md provides step-by-step presentation scripts."
)
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

c15_2 = create_card(slide15, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0))
tf = c15_2.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Milestone 2 Prioritized Implementation Plan"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_sub = tf.add_paragraph()
p_sub.text = (
    "1. Setup & Ingestion Pipeline:\n"
    "   Build PDF, DOCX, CSV, TXT parsers with PyMuPDF and python-docx.\n\n"
    "2. ChromaDB RAG Vector Store:\n"
    "   Implement recursive chunking and project-isolated similarity retrieval.\n\n"
    "3. Scope & Risk Extraction Agents:\n"
    "   Deploy LangGraph agent workflows for deliverables and 5x5 risk matrix.\n\n"
    "4. Blocker Detection & Health Scoring:\n"
    "   Implement reproducible 0-100 mathematical health score formula.\n\n"
    "5. Conversational Assistant & React Dashboard:\n"
    "   Deploy grounded chat with citations and React KPI overview."
)
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXT_DARK
p_sub.space_before = Pt(8)

slide15.notes_slide.notes_text_frame.text = (
    "In conclusion, Milestone 1 establishes the initial planning, architecture design, and quality assurance framework "
    "for the AI Project Intelligence & Risk Advisor after our first 3 to 4 days of setup. "
    "Thank you, and I look forward to your questions and guidance."
)

prs.save(pptx_path)
print(f"Presentation saved successfully to: {pptx_path}")
