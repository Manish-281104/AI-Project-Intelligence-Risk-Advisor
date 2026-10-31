import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

output_dir = "milestone2_deliverables"
os.makedirs(output_dir, exist_ok=True)
pptx_path = os.path.join(output_dir, "Milestone2_Presentation.pptx")

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette Constants
COLOR_NAVY = RGBColor(15, 23, 42)          # Slate 900
COLOR_BLUE_DARK = RGBColor(30, 58, 138)    # Blue 900
COLOR_BLUE_ACCENT = RGBColor(14, 165, 233) # Sky 500
COLOR_TEAL = RGBColor(13, 148, 136)        # Teal 600
COLOR_GRAY_LIGHT = RGBColor(248, 250, 252) # Slate 50
COLOR_GRAY_CARD = RGBColor(241, 245, 249)  # Slate 100
COLOR_TEXT_DARK = RGBColor(15, 23, 42)
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_GREEN = RGBColor(22, 101, 52)
COLOR_RED = RGBColor(153, 27, 27)
COLOR_AMBER = RGBColor(180, 83, 9)

def add_header(slide, title_text, category_text="MILESTONE 2 REVIEW • 31 OCTOBER 2026"):
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
p2.text = "Milestone 2 Review: Autonomous Multi-Agent Intelligence, Multi-Format Ingestion & RAG"
p2.font.size = Pt(20)
p2.font.color.rgb = COLOR_BLUE_ACCENT
p2.space_before = Pt(12)

p3 = tf1.add_paragraph()
p3.text = "Final Year B.Tech Major Project Review  |  Milestone 2 End Date: 31 October 2026"
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
p5.text = "Scope: Core Engineering, Autonomous Scope/Risk/Blocker Agents, RapidOCR Fallback, Dynamic Identity & 35 Passing Tests"
p5.font.size = Pt(12)
p5.font.color.rgb = COLOR_BLUE_ACCENT
p5.space_before = Pt(8)

slide1.notes_slide.notes_text_frame.text = (
    "Good morning respected evaluators. Today I present Milestone 2 of our project: "
    "AI Project Intelligence & Risk Advisor, concluding on October 31, 2026. "
    "In this milestone, we moved from planning to working software: building 3 autonomous agents, "
    "multi-file ingestion with OCR fallback, dynamic workspace isolation, and 35 verified automated tests."
)

# ==========================================
# SLIDE 2: EXECUTIVE SUMMARY
# ==========================================
slide2 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide2, "Milestone 2 Executive Summary & Verification Highlights")

cards_s2 = [
    ("Autonomous Multi-Agent Core", "Three specialized agents (Scope, Risk, Blocker) operating concurrently via POST /api/agents/analyze-all with Pydantic schemas and strict evidence citations.", COLOR_TEAL),
    ("Multi-Format Ingestion & OCR", "PDF, DOCX, CSV with delimiter sniffing, and TXT parsing. Fully integrated RapidOCR (ONNX Runtime) fallback for scanned/image-only PDFs with blank page filtering.", COLOR_BLUE_DARK),
    ("Dynamic Identity & Zero Bleed", "Dynamic project identity resolution eliminating hardcoded project bias. Strict single-workspace isolation preventing data bleed across domains (tested Campus Event vs Library).", COLOR_NAVY),
    ("100% Verified Quality Assurance", "All 35 automated pytest tests passing in 5.71s (10 API, 8 chunking, 10 agents, 2 workspace, 1 ground truth, 3 comprehensive, 1 domain test). 11 defects closed.", COLOR_GREEN),
]

for i, (title, desc, color) in enumerate(cards_s2):
    left = Inches(0.8 + (i % 2) * 5.95)
    top = Inches(1.8 + (i // 2) * 2.5)
    c = create_card(slide2, left, top, Inches(5.7), Inches(2.2), COLOR_GRAY_CARD, color)
    tf = c.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = color
    p_desc = tf.add_paragraph()
    p_desc.text = desc
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = COLOR_TEXT_DARK
    p_desc.space_before = Pt(8)

slide2.notes_slide.notes_text_frame.text = (
    "Milestone 2 delivers verified working capabilities. We have achieved multi-format ingestion, "
    "scanned PDF OCR fallback, dynamic project detection, three autonomous agents, and 100% test pass rate."
)

# ==========================================
# SLIDE 3: MILESTONE 1 VS MILESTONE 2
# ==========================================
slide3 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide3, "Evolution: Milestone 1 (Oct 14) vs Milestone 2 (Oct 31)")

c3_1 = create_card(slide3, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0))
tf = c3_1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Milestone 1 Baseline (Oct 14, 2026)"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_TEXT_MUTED
p_body = tf.add_paragraph()
p_body.text = (
    "• Initial Setup & Scaffolding Scope (3-4 Days Effort)\n"
    "• Module 1 (Ingestion) partially implemented; single-file upload only\n"
    "• Module 9 (Dashboard) partially implemented with developmental labels\n"
    "• Modules 2-8 marked Planned; no agents or vector store active\n"
    "• 0 automated tests in workspace (pytest exited code 1)\n"
    "• Scanned image-only PDFs failed extraction\n"
    "• 1 initial setup defect logged (Defect 1: Git & venv setup)\n"
    "• Workspace: C:\\Users\\manis\\Desktop\\SP"
)
p_body.font.size = Pt(11)
p_body.font.color.rgb = COLOR_TEXT_DARK
p_body.space_before = Pt(8)

c3_2 = create_card(slide3, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), border_color=COLOR_GREEN)
tf = c3_2.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Milestone 2 Verified Reality (Oct 31, 2026)"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_GREEN
p_body = tf.add_paragraph()
p_body.text = (
    "• Full Core Engineering & Working Software Scope\n"
    "• Multi-file drag-and-drop batch upload with staging queue\n"
    "• RapidOCR (ONNX Runtime) fallback pipeline for scanned PDFs\n"
    "• Persistent vector store & TF-IDF cosine semantic retriever\n"
    "• 3 Autonomous Agents: Scope, Risk, and Blocker Agents active\n"
    "• Dynamic Project Identity & Workspace Isolation (0% bleed)\n"
    "• 35 Automated Pytest Tests Passing (100% pass rate in 5.71s)\n"
    "• 11 Defect Tracker items verified and Closed\n"
    "• Production Frontend: React + TypeScript + Vite (2.25s clean build)"
)
p_body.font.size = Pt(11)
p_body.font.color.rgb = COLOR_TEXT_DARK
p_body.space_before = Pt(8)

slide3.notes_slide.notes_text_frame.text = (
    "Comparing Milestone 1 and Milestone 2 clearly demonstrates our engineering velocity. "
    "In Milestone 1, we had zero tests and no agents. In Milestone 2, we have 35 passing tests, "
    "three fully functional agents, OCR fallback, and production-grade software."
)

# ==========================================
# SLIDE 4: SYSTEM ARCHITECTURE
# ==========================================
slide4 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide4, "Milestone 2 Verified System Architecture")

layers = [
    ("Presentation Layer", "React 18 + TypeScript + Vite | Drag-and-drop batch upload, staging queue, chunk viewer, tabbed AI advisory views (Scope, Risk, Blocker).", COLOR_BLUE_DARK),
    ("API & Routing Layer", "FastAPI (Python 3.13) | REST API endpoints: /api/documents/upload, /api/agents/scope, /api/agents/risks, /api/agents/blockers, /api/agents/analyze-all, /api/project/workspace.", COLOR_NAVY),
    ("Extraction & Ingestion Engine", "PyMuPDF (PDF) + python-docx (DOCX) + csv parser (delimiter sniffing) + UTF-8 txt | RapidOCR (ONNX Runtime) fallback for image-only pages.", COLOR_TEAL),
    ("Multi-Agent Intelligence Core", "Scope Agent (Goals, sub-goals, scope, deliverables) | Risk Agent (Schedule deltas, 5x5 matrix, delivery forecast) | Blocker Agent (Action items, UNKNOWN owners, decisions).", COLOR_BLUE_ACCENT),
    ("Storage & Persistence", "Local isolated storage (backend/uploads/) | JSON Registry & Workspace state (backend/data/) | Vector Store with project_id isolation.", COLOR_TEXT_MUTED)
]

for i, (layer_name, layer_desc, color) in enumerate(layers):
    top = Inches(1.8 + i * 1.0)
    c = create_card(slide4, Inches(0.8), top, Inches(11.733), Inches(0.85), COLOR_GRAY_CARD, color)
    tf = c.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.15)
    p = tf.paragraphs[0]
    p.text = layer_name
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = color
    p_desc = tf.add_paragraph()
    p_desc.text = layer_desc
    p_desc.font.size = Pt(10)
    p_desc.font.color.rgb = COLOR_TEXT_DARK

slide4.notes_slide.notes_text_frame.text = (
    "Our architecture is layered cleanly between React frontend, FastAPI backend, "
    "multi-format extraction engine, multi-agent reasoning, and isolated storage."
)

# ==========================================
# SLIDE 5: MULTI-FORMAT INGESTION & OCR
# ==========================================
slide5 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide5, "Multi-Format Ingestion & Scanned PDF OCR Fallback Pipeline")

cards_s5 = [
    ("Native Text PDF Extraction", "PyMuPDF (fitz) extracts text stream per page with coordinate provenance ('Page 1', 'Page 2'). Caches font and layout coordinates.", COLOR_BLUE_DARK),
    ("Scanned PDF OCR Fallback", "RapidOCR (ONNX Runtime) automatically triggered when extracted characters fall below threshold (<60 chars). Renders page to 200 DPI pixmap and runs OCR. Blank pages rejected.", COLOR_RED),
    ("DOCX & CSV Parsing", "python-docx parses paragraphs, tables, and headers. CSV parser sniffs delimiters (comma, semicolon, tab, pipe) and preserves row coordinates ('Row 1-5').", COLOR_TEAL),
    ("Batch Ingestion & Validation", "POST /api/documents/upload accepts multiple files. Validates mime types, size limits (25MB), detects corrupted %PDF signatures, and rejects empty files.", COLOR_NAVY)
]

for i, (title, desc, color) in enumerate(cards_s5):
    left = Inches(0.8 + (i % 2) * 5.95)
    top = Inches(1.8 + (i // 2) * 2.5)
    c = create_card(slide5, left, top, Inches(5.7), Inches(2.2), COLOR_GRAY_CARD, color)
    tf = c.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = color
    p_desc = tf.add_paragraph()
    p_desc.text = desc
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = COLOR_TEXT_DARK
    p_desc.space_before = Pt(8)

slide5.notes_slide.notes_text_frame.text = (
    "Ingestion handles four distinct file types. When users upload scanned or image-only PDFs, "
    "the system automatically invokes RapidOCR without failing, ensuring complete document resilience."
)

# ==========================================
# SLIDE 6: DYNAMIC IDENTITY & WORKSPACE ISOLATION
# ==========================================
slide6 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide6, "Dynamic Project Identity & Zero Cross-Bleed Isolation")

c6_1 = create_card(slide6, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0))
tf = c6_1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Dynamic Project Identity Resolution"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_body = tf.add_paragraph()
p_body.text = (
    "• Zero Hardcoded Names: Automatically discovers project name from document metadata and Section 1 Overview.\n\n"
    "• 1 Primary Goal + 5 Sub-Goals: Resolves single overarching objective and supporting sub-goals.\n\n"
    "• Universal Domain Support: Validated across Campus Event Management, Hospital ICU, Library Management, E-Commerce, and Software Systems.\n\n"
    "• Generic File Inheritance: Documents without explicit titles safely inherit active workspace identity."
)
p_body.font.size = Pt(11)
p_body.font.color.rgb = COLOR_TEXT_DARK
p_body.space_before = Pt(8)

c6_2 = create_card(slide6, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), border_color=COLOR_TEAL)
tf = c6_2.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Cross-Project Conflict & Workspace Isolation"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL
p_body = tf.add_paragraph()
p_body.text = (
    "• Conflict Detection (HTTP 409): Ingesting documents from a different project into an established workspace triggers HTTP 409 Conflict with descriptive payload.\n\n"
    "• 1-Click Workspace Reinitialization: User can archive current workspace and initialize a clean, isolated project workspace.\n\n"
    "• Zero Cross-Bleed Verified: Switching between Campus Event Portal and Community Library System verified in test_dynamic_project_switching_and_zero_bleed with 0% token contamination."
)
p_body.font.size = Pt(11)
p_body.font.color.rgb = COLOR_TEXT_DARK
p_body.space_before = Pt(8)

slide6.notes_slide.notes_text_frame.text = (
    "One of the biggest flaws in naive AI tools is cross-project bleed. Our platform dynamically detects "
    "project identity, enforces HTTP 409 conflict detection, and guarantees zero cross-project bleed."
)

# ==========================================
# SLIDE 7: AGENT 1 - SCOPE & DELIVERABLES
# ==========================================
slide7 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide7, "Agent 1: Scope & Deliverable Extraction Agent")

c7_1 = create_card(slide7, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0))
tf = c7_1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Core Extraction Capabilities"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_BLUE_DARK
p_body = tf.add_paragraph()
p_body.text = (
    "• Primary Goal Discovery: Extracts the genuine project objective from Section 1 Overview, filtering out table fragments and dependency codes.\n\n"
    "• Supporting Sub-Goals: Discovers up to 5 structured sub-goals (SG-01 to SG-05).\n\n"
    "• Scope Boundary Classification: Clearly demarcates In-Scope features from Out-of-Scope limitations.\n\n"
    "• Deliverables & Milestones: Extracts deliverable names, target milestone schedules, and task dependencies."
)
p_body.font.size = Pt(11)
p_body.font.color.rgb = COLOR_TEXT_DARK
p_body.space_before = Pt(8)

c7_2 = create_card(slide7, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), border_color=COLOR_GREEN)
tf = c7_2.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Anti-Hallucination & Provenance Rigor"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_GREEN
p_body = tf.add_paragraph()
p_body.text = (
    "• Strict UNKNOWN Fallback: When deliverable owners or target dates are omitted in source documents, the agent strictly outputs 'UNKNOWN'. Zero name or date fabrication.\n\n"
    "• Missing Information Auditing: Explicitly catalogs missing requirements and data gaps in missing_information.\n\n"
    "• Verbatim Sentence Citations: Every deliverable includes exact document filename, page coordinate, and chunk reference."
)
p_body.font.size = Pt(11)
p_body.font.color.rgb = COLOR_TEXT_DARK
p_body.space_before = Pt(8)

slide7.notes_slide.notes_text_frame.text = (
    "The Scope Agent extracts goals, deliverables, and boundaries. Crucially, it adheres to our strict anti-hallucination standard: "
    "any unassigned owner or deadline is reported strictly as UNKNOWN without guessing."
)

# ==========================================
# SLIDE 8: AGENT 2 - RISK DETECTION & FORECASTING
# ==========================================
slide8 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide8, "Agent 2: Risk Detection & Delivery Forecasting Agent")

cards_s8 = [
    ("Deterministic Schedule Engine", "Calculates calendar day deltas between target milestone dates and project reference date (Oct 28/31, 2026). Flags overdue items with exact negative float days.", COLOR_RED),
    ("5x5 Qualitative Severity Matrix", "Evaluates Likelihood (1-5) and Impact (1-5). High x High maps to Critical, High x Medium maps to High. Discloses full matrix methodology.", COLOR_AMBER),
    ("Evidence vs Recommendation Separation", "Enforces a strict boundary: supporting_evidence contains verbatim document quotes; recommended_mitigation is explicitly prefixed '[AI Recommendation]'.", COLOR_TEAL),
    ("Honest Delivery Forecasting", "Provides qualitative project outlook (Critical, High, Elevated, Moderate, Low). Explicitly discloses absence of synthetic burn-down metrics when velocity logs are absent.", COLOR_BLUE_DARK)
]

for i, (title, desc, color) in enumerate(cards_s8):
    left = Inches(0.8 + (i % 2) * 5.95)
    top = Inches(1.8 + (i // 2) * 2.5)
    c = create_card(slide8, left, top, Inches(5.7), Inches(2.2), COLOR_GRAY_CARD, color)
    tf = c.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = color
    p_desc = tf.add_paragraph()
    p_desc.text = desc
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = COLOR_TEXT_DARK
    p_desc.space_before = Pt(8)

slide8.notes_slide.notes_text_frame.text = (
    "The Risk Agent pairs deterministic mathematical date checks with qualitative matrix scoring. "
    "It clearly separates document evidence from AI recommendations."
)

# ==========================================
# SLIDE 9: AGENT 3 - BLOCKER & ACTION ITEMS
# ==========================================
slide9 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide9, "Agent 3: Blocker & Action Item Identification Agent")

c9_1 = create_card(slide9, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0))
tf = c9_1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Operational Impediment Extraction"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_body = tf.add_paragraph()
p_body.text = (
    "• Active Blocker Detection: Extracts critical roadblocks, dependency bottlenecks, and technical impediments from meeting minutes and status notes.\n\n"
    "• Action Item Register: Extracts discrete tasks, responsible parties, priority levels (Critical, High, Medium, Low), and target dates.\n\n"
    "• Decision Governance: Extracts approved architectural/technical decisions and highlights pending unresolved decisions requiring leadership signoff."
)
p_body.font.size = Pt(11)
p_body.font.color.rgb = COLOR_TEXT_DARK
p_body.space_before = Pt(8)

c9_2 = create_card(slide9, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), border_color=COLOR_BLUE_ACCENT)
tf = c9_2.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Anti-Hallucination & Deduplication"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_BLUE_ACCENT
p_body = tf.add_paragraph()
p_body.text = (
    "• Strict UNKNOWN Assignees: Tasks without assigned names are mapped to 'UNKNOWN'; unassigned_count is incremented without fabricating stakeholders.\n\n"
    "• Cross-Document Deduplication: Merges identical blockers mentioned across meeting minutes and project charters into consolidated records with combined citations.\n\n"
    "• Overdue Action Tracking: Calculates overdue status relative to document reporting date."
)
p_body.font.size = Pt(11)
p_body.font.color.rgb = COLOR_TEXT_DARK
p_body.space_before = Pt(8)

slide9.notes_slide.notes_text_frame.text = (
    "The Blocker Agent provides full visibility into open impediments, assigned action items, and pending decisions. "
    "It consolidates duplicate issues across multiple documents."
)

# ==========================================
# SLIDE 10: RAG RETRIEVAL & EVIDENCE CITATIONS
# ==========================================
slide10 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide10, "RAG Pipeline & Traceable Evidence Grounding")

cards_s10 = [
    ("Boundary-Aware Chunking", "Splits documents into 500-char target chunks with 100-char overlap, strictly respecting sentence and paragraph boundaries. Preserves row/page coordinates.", COLOR_BLUE_DARK),
    ("Vector Space & TF-IDF Cosine", "Indexes document chunks into persistent JSON catalog with TF-IDF cosine ranking and 384-dimensional dense vectors. Requires zero heavy Windows compilation.", COLOR_TEAL),
    ("Project Workspace Isolation", "Retriever queries strictly enforce project_id metadata filtering, guaranteeing that semantic searches never retrieve chunks from prior projects.", COLOR_NAVY),
    ("Sentence-Level Citations", "Every single insight generated by the 3 agents cites source filename, page coordinate ('Page 2'), or table row ('Row 1-5') with verbatim evidence quotes.", COLOR_GREEN)
]

for i, (title, desc, color) in enumerate(cards_s10):
    left = Inches(0.8 + (i % 2) * 5.95)
    top = Inches(1.8 + (i // 2) * 2.5)
    c = create_card(slide10, left, top, Inches(5.7), Inches(2.2), COLOR_GRAY_CARD, color)
    tf = c.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = color
    p_desc = tf.add_paragraph()
    p_desc.text = desc
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = COLOR_TEXT_DARK
    p_desc.space_before = Pt(8)

slide10.notes_slide.notes_text_frame.text = (
    "Our RAG pipeline ensures strict evidence grounding. Every insight can be verified against the exact "
    "source document sentence or table row."
)

# ==========================================
# SLIDE 11: FRONTEND DASHBOARD
# ==========================================
slide11 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide11, "Production Frontend Interface (React + TypeScript + Vite)")

cards_s11 = [
    ("Multi-File Staging Dropzone", "Drag-and-drop dropzone supporting multiple file selection. Displays file format badges, human-readable file sizes, and individual file removal buttons before upload.", COLOR_BLUE_DARK),
    ("Per-File Upload Status & Progress", "Batch upload reports per-file processing status. Independent success/failure reporting prevents a single invalid file from aborting valid documents.", COLOR_TEAL),
    ("Extracted Text Chunk Viewer", "Expandable chunk cards render coordinate provenance (Page/Row), character and word counts, snippet previews, and 1-click copy-to-clipboard functionality.", COLOR_NAVY),
    ("Tabbed AI Advisory View", "AgentAnalysisView renders clean tabs for Scope, Risks, and Blockers with summary metric pills, severity badges, verbatim evidence cards, and type filters.", COLOR_GREEN)
]

for i, (title, desc, color) in enumerate(cards_s11):
    left = Inches(0.8 + (i % 2) * 5.95)
    top = Inches(1.8 + (i // 2) * 2.5)
    c = create_card(slide11, left, top, Inches(5.7), Inches(2.2), COLOR_GRAY_CARD, color)
    tf = c.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = color
    p_desc = tf.add_paragraph()
    p_desc.text = desc
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = COLOR_TEXT_DARK
    p_desc.space_before = Pt(8)

slide11.notes_slide.notes_text_frame.text = (
    "The frontend is built with React 18 and Vite. It provides a clean, responsive interface "
    "with drag-and-drop batch upload and tabbed advisory views."
)

# ==========================================
# SLIDE 12: QUALITY ASSURANCE & DEFECT TRACKER
# ==========================================
slide12 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide12, "Quality Assurance & Verified Defect Management (11/11 Closed)")

c12_1 = create_card(slide12, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
tf = c12_1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Summary of Verified Closed Defects in Defect_Tracker_Milestone2.xlsx"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_body = tf.add_paragraph()
p_body.text = (
    "• Defect 1 [UI / Closed]: Removed developmental milestone labels and banners from App.tsx.\n"
    "• Defect 2 [UI / Closed]: Extracted text chunks visible in frontend chunk viewer with coordinates.\n"
    "• Defect 3 [Logical / Closed]: Added frontend multi-file staging and backend independent batch upload processing.\n"
    "• Defect 4 [Maintainability / Closed]: Implemented persistent JSON catalog (documents_registry.json) surviving restarts.\n"
    "• Defect 5 [Standards / Closed]: Enforced strict UNKNOWN mapping for unstated owners and deadlines.\n"
    "• Defect 6 [Logical / Closed]: Blank scanned PDF rejection with actionable HTTP 400 error.\n"
    "• Defect 7 [Logical / Closed]: Persistent ProjectWorkspace grouping multi-batch uploads under one project.\n"
    "• Defect 8 [Standards / Closed]: Cross-project consistency validation raising HTTP 409 Conflict.\n"
    "• Defect 9 [Logical / Closed]: Section 1 Overview goal priority and action-item-specific unassigned counts.\n"
    "• Defect 10 [Logical / Closed]: Integrated RapidOCR (ONNX Runtime) fallback for scanned image-only PDFs.\n"
    "• Defect 11 [Logical / Closed]: Dynamic project identity resolution eliminating cross-project context bleed.\n\n"
    "Defect Status: 11 Verified Defects Logged  |  11 Verified Resolved & Retested  |  0 Open Defects"
)
p_body.font.size = Pt(11)
p_body.font.color.rgb = COLOR_TEXT_DARK
p_body.space_before = Pt(8)

slide12.notes_slide.notes_text_frame.text = (
    "In accordance with software engineering governance, our Defect Tracker records 11 genuine defects "
    "identified and resolved during development. All 11 are retested, verified, and closed."
)

# ==========================================
# SLIDE 13: AUTOMATED TESTING RESULTS
# ==========================================
slide13 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide13, "Automated Test Execution & Verification Evidence")

cards_s13 = [
    ("test_api.py (10 Tests)", "10/10 Passed | Health checks, module catalog, format uploads (PDF, DOCX, CSV, TXT), empty file rejection, unsupported extension rejection, corrupt PDF rejection.", COLOR_BLUE_DARK),
    ("test_chunking.py (8 Tests)", "8/8 Passed | Boundary splitting, overlap verification, multipage PDFs, CSV row tagging, DOCX paragraph mapping, 0-text rejection.", COLOR_TEAL),
    ("test_milestone2_agents.py (10 Tests)", "10/10 Passed | Batch uploads, mixed batch partial success, catalog persistence, deletion, Scope Agent, Risk Agent, Blocker Agent, analyze-all endpoint.", COLOR_NAVY),
    ("Comprehensive & Domain Tests (7 Tests)", "7/7 Passed | Scanned PDF OCR fallback, dynamic project switching with zero bleed, CSV delimiters, persistent workspace, 10-criteria ground truth benchmark.", COLOR_GREEN)
]

for i, (title, desc, color) in enumerate(cards_s13):
    left = Inches(0.8 + (i % 2) * 5.95)
    top = Inches(1.8 + (i // 2) * 2.5)
    c = create_card(slide13, left, top, Inches(5.7), Inches(2.2), COLOR_GRAY_CARD, color)
    tf = c.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = color
    p_desc = tf.add_paragraph()
    p_desc.text = desc
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = COLOR_TEXT_DARK
    p_desc.space_before = Pt(8)

slide13.notes_slide.notes_text_frame.text = (
    "Our automated test suite comprises 35 unit and integration tests across 8 modules. "
    "All 35 tests pass with 100% success in 5.71 seconds."
)

# ==========================================
# SLIDE 14: BENCHMARK DEMONSTRATION WORKFLOW
# ==========================================
slide14 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide14, "Milestone 2 Ground Truth Benchmark Demonstration")

c14_1 = create_card(slide14, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
tf = c14_1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "10/10 Acceptance Criteria Validated on AI_Project_Agent_Test_Sample_Document.docx"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_GREEN
p_body = tf.add_paragraph()
p_body.text = (
    "1. Primary Goal: Correctly extracted from Section 1 Overview without selecting dependency codes (DEP-01).\n"
    "2. Scope Sub-Goals: Extracted 5 supporting sub-goals (SG-01 to SG-05) with clear boundaries.\n"
    "3. Deliverables: Exactly 6 distinct deliverables extracted with verified source citations.\n"
    "4. Milestones: Exactly 6 chronological milestones identified with target completion dates.\n"
    "5. Risks: Exactly 3 documented project risks detected with Likelihood x Impact ratings.\n"
    "6. Active Blockers: Critical server provisioning blocker identified with resolution action steps.\n"
    "7. Action Items: Exactly 5 action items extracted with assigned owners and target deadlines.\n"
    "8. Decisions: Exactly 1 pending architectural decision and approved decisions captured.\n"
    "9. Unassigned Count: Evaluated strictly against action items = 0 unassigned (zero hallucination).\n"
    "10. Overdue Count: Accurately evaluated relative to project reporting date = 0 overdue."
)
p_body.font.size = Pt(11)
p_body.font.color.rgb = COLOR_TEXT_DARK
p_body.space_before = Pt(8)

slide14.notes_slide.notes_text_frame.text = (
    "We tested the full system against our standardized benchmark test document. "
    "All 10 ground truth acceptance criteria passed with zero hallucination."
)

# ==========================================
# SLIDE 15: CONCLUSION & MILESTONE 3 ROADMAP
# ==========================================
slide15 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide15, "Milestone 2 Conclusion & Milestone 3 Roadmap")

c15_1 = create_card(slide15, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0), border_color=COLOR_GREEN)
tf = c15_1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Milestone 2 Completed Deliverables (31 Oct 2026)"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_GREEN
p_body = tf.add_paragraph()
p_body.text = (
    "• Multi-Format Document Ingestion (PDF, DOCX, CSV, TXT)\n"
    "• RapidOCR (ONNX Runtime) Fallback for Scanned PDFs\n"
    "• Dynamic Project Identity & Zero Cross-Bleed Isolation\n"
    "• Scope & Deliverable Extraction Agent\n"
    "• Risk Detection & Delivery Forecasting Agent\n"
    "• Blocker & Action Item Identification Agent\n"
    "• Unified Multi-Agent Analysis API (/api/agents/analyze-all)\n"
    "• Interactive React 18 + TypeScript + Vite Dashboard\n"
    "• 35 Automated Pytest Tests Passing (100% Pass Rate)\n"
    "• 11 Verified Closed Defects in Defect Tracker\n"
    "• Milestone 2 Deliverables Package & Audit Documentation"
)
p_body.font.size = Pt(10)
p_body.font.color.rgb = COLOR_TEXT_DARK
p_body.space_before = Pt(8)

c15_2 = create_card(slide15, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
tf = c15_2.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
p = tf.paragraphs[0]
p.text = "Upcoming Milestone 3 Planned Scope"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY
p_body = tf.add_paragraph()
p_body.text = (
    "1. Module 6: Documentation Generation Agent\n"
    "   • Automated synthesis of Gherkin-format user stories, draft risk registers, and executive briefing reports.\n\n"
    "2. Module 7: Composite Project Health Scoring Engine\n"
    "   • Deterministic 0-100 mathematical formula combining schedule adherence (0.35), risk density (0.30), blocker volume (0.20), and documentation completeness (0.15).\n\n"
    "3. Module 8: Conversational Project Intelligence Assistant\n"
    "   • Natural language Q&A assistant with interactive chunk citations and strict refusal guardrails."
)
p_body.font.size = Pt(10)
p_body.font.color.rgb = COLOR_TEXT_DARK
p_body.space_before = Pt(8)

slide15.notes_slide.notes_text_frame.text = (
    "In conclusion, Milestone 2 successfully completes core engineering, multi-format ingestion, "
    "scanned PDF OCR fallback, dynamic workspace isolation, and three autonomous agents as of October 31, 2026. "
    "Thank you, and I welcome your feedback and questions."
)

prs.save(pptx_path)
print(f"Milestone 2 Presentation saved successfully to: {pptx_path}")
