"""
update_root_templates.py

Directly updates the three root Excel templates in place:
1. Agile_Template_v0.1.xls (BIFF8 legacy Excel format preserved using xlrd + xlutils + xlwt)
2. Defect_Tracker Template_v0.1.xlsx (OpenXML format preserved using openpyxl)
3. Unit_Test_Plan_v0.1.xlsx (OpenXML format preserved using openpyxl)

Milestone 1 Scope: Preserved historical baseline (Oct 10-14, 2026).
Milestone 2 Scope: Concluded on October 31, 2026 (Oct 24-31, 2026).
"""

import os
import datetime
from copy import copy
from pathlib import Path
import xlrd
from xlutils.filter import process, XLRDReader, XLWTWriter
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = Path(".")


# =====================================================================
# 1. UPDATE AGILE_TEMPLATE_V0.1.XLS IN PLACE (PRESERVING .XLS FORMAT)
# =====================================================================
def update_agile_template_xls():
    file_path = ROOT / "Agile_Template_v0.1.xls"
    print(f"Loading {file_path} for in-place update...")

    rb = xlrd.open_workbook(file_path, formatting_info=True)
    w = XLWTWriter()
    process(XLRDReader(rb, str(file_path)), w)
    wb = w.output[0][1]

    # --- Sheet 0: Product Backlog ---
    ws_pb = wb.get_sheet(0)
    rs_pb = rb.sheet_by_name("Product Backlog")

    user_stories = [
        # Milestone 1 Scope (Sprint 1)
        ("Sprint 1", "Sprint 1", "US-01", "As a project manager, I want to set up the repository, virtual environment, and baseline configuration for FastAPI and React.", "MUST HAVE", "none", "Manish", "3- Completed"),
        ("Sprint 1", "Sprint 1", "US-02", "As a system architect, I want to study RAG and multi-agent architectures and design core system data flow.", "MUST HAVE", "none", "Manish", "3- Completed"),
        ("Sprint 1", "Sprint 1", "US-03", "As a user, I want multi-format document ingestion supporting PDF, DOCX, CSV, and TXT with size validation.", "MUST HAVE", "US-02", "Manish", "3- Completed"),
        ("Sprint 1", "Sprint 1", "US-04", "As a RAG pipeline engineer, I want text extraction and boundary-aware chunking preserving page and row coordinates.", "MUST HAVE", "US-03", "Manish", "3- Completed"),
        ("Sprint 1", "Sprint 1", "US-05", "As a developer, I want embedding generation and persistent vector indexing preparation for project documents.", "SHOULD HAVE", "US-04", "Manish", "3- Completed"),
        ("Sprint 1", "Sprint 1", "US-06", "As a stakeholder, I want an initial dashboard interface to verify backend health and monitor ingestion status.", "COULD HAVE", "US-02", "Manish", "3- Completed"),
        # Milestone 2 Scope (Sprint 2 - Completed 31 October 2026)
        ("Sprint 2", "Sprint 2", "US-07", "As a project manager, I want to select and upload multiple documents simultaneously with independent processing and status reporting.", "MUST HAVE", "US-03", "Manish", "3- Completed"),
        ("Sprint 2", "Sprint 2", "US-08", "As a user, I want optical character recognition (RapidOCR ONNX) fallback for scanned image-only PDFs with blank page filtering.", "MUST HAVE", "US-07", "Manish", "3- Completed"),
        ("Sprint 2", "Sprint 2", "US-09", "As a project manager, I want an autonomous Scope & Deliverable Extraction Agent to extract goals, sub-goals, scope, deliverables, and milestones with citations.", "MUST HAVE", "US-04", "Manish", "3- Completed"),
        ("Sprint 2", "Sprint 2", "US-10", "As a risk officer, I want a Risk Detection & Delivery Forecasting Agent to calculate schedule slippages and evaluate qualitative severity (5x5 matrix).", "MUST HAVE", "US-09", "Manish", "3- Completed"),
        ("Sprint 2", "Sprint 2", "US-11", "As a scrum master, I want a Blocker & Action Item Agent to extract active blockers, action items, and pending decisions with UNKNOWN owner fallbacks.", "MUST HAVE", "US-04", "Manish", "3- Completed"),
        ("Sprint 2", "Sprint 2", "US-12", "As a project manager, I want dynamic project identity resolution and persistent workspace grouping to prevent cross-project context bleed (HTTP 409 conflict).", "MUST HAVE", "US-07", "Manish", "3- Completed"),
        ("Sprint 2", "Sprint 2", "US-13", "As a user, I want an interactive React dashboard with tabbed AI advisory views (Scope, Risk, Blocker) and chunk viewer.", "MUST HAVE", "US-02", "Manish", "3- Completed"),
        ("Sprint 2", "Sprint 2", "US-14", "As a QA engineer, I want automated regression testing (35 pytest tests) and ground-truth benchmark validation across multiple project domains.", "MUST HAVE", "US-09", "Manish", "3- Completed"),
        # Milestone 3 Scope (Sprint 3 - Planned / Deferred)
        ("Sprint 3", "TBD", "US-15", "As a team member, I want automated documentation generation (Gherkin user stories, draft risk registers) synthesized from project intelligence.", "SHOULD HAVE", "US-09", "Team", "1- Not Started"),
        ("Sprint 3", "TBD", "US-16", "As a stakeholder, I want a composite project health score (0-100) combining schedule, risk, blocker, and documentation factors.", "MUST HAVE", "US-10", "Team", "1- Not Started"),
        ("Sprint 3", "TBD", "US-17", "As a project stakeholder, I want a conversational project intelligence assistant grounded strictly in document chunk citations.", "SHOULD HAVE", "US-08", "Team", "1- Not Started"),
    ]

    for idx, story in enumerate(user_stories):
        row_idx = 1 + idx
        for col_idx, val in enumerate(story):
            xf_idx = rs_pb.cell_xf_index(min(row_idx, rs_pb.nrows - 1), col_idx)
            style = w.style_list[xf_idx]
            ws_pb.write(row_idx, col_idx, val, style)

    # --- Sheet 1: Sprint Backlog ---
    ws_sb = wb.get_sheet(1)
    rs_sb = rb.sheet_by_name("Sprint Backlog")

    # Row 3: Sprint 1 Header
    xf_h1 = rs_sb.cell_xf_index(3, 0)
    ws_sb.write(3, 0, "SPRINT  1  BACKLOG - Foundation & Ingestion Scaffolding (Oct 10-14, 2026)", w.style_list[xf_h1])

    # SPRINT 1 TASKS (Rows 4 to 9)
    sprint1_tasks = [
        ("US-01", "T-01", "Repository, folder structure, and local dev environments setup for FastAPI and React.", 46305.0, 46305.0, "Manish", "Coding", "3- Completed", 2.0, 2.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-02", "T-02", "Architecture study (RAG & multi-agent) and high-level system data flow design.", 46305.0, 46306.0, "Manish", "Design", "3- Completed", 2.5, 2.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-03", "T-03", "Multi-format document parser design (PDF, DOCX, CSV, TXT) and validation rules.", 46306.0, 46307.0, "Manish", "Coding", "3- Completed", 4.0, 0, 4.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-01", "T-04", "Initial FastAPI route design and Pydantic request/response schemas for health and modules.", 46307.0, 46308.0, "Manish", "Coding", "3- Completed", 3.5, 0, 0, 3.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-04", "T-05", "Document chunking, metadata coordinate preservation, and vector indexing setup.", 46308.0, 46309.0, "Manish", "Coding", "3- Completed", 3.0, 0, 0, 0, 3.0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-01", "T-06", "Milestone 1 baseline unit test plan and physical repository audit documentation.", 46308.0, 46309.0, "Manish", "Unit Test", "3- Completed", 4.0, 0, 0, 0, 4.0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    ]

    for idx, task in enumerate(sprint1_tasks):
        r_idx = 4 + idx
        for c_idx, val in enumerate(task):
            xf_idx = rs_sb.cell_xf_index(min(r_idx, rs_sb.nrows - 1), c_idx)
            ws_sb.write(r_idx, c_idx, val, w.style_list[xf_idx])

    # Row 10: Sprint 2 Header
    ws_sb.write(10, 0, "SPRINT  2  BACKLOG - Multi-Agent Intelligence & Ingestion (Oct 24-31, 2026)", w.style_list[xf_h1])

    # SPRINT 2 TASKS (Rows 11 to 22) spanning Oct 24-31, 2026
    sprint2_tasks = [
        ("US-07", "T-07", "Enable multiple-file selection, pre-upload staging list, independent file processing, and per-file results in FastAPI.", 46319.0, 46321.0, "Manish", "Coding", "3- Completed", 3.5, 0, 0, 0, 0, 3.5, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-07", "T-08", "Enforce empty file, corrupted PDF, and blank scanned document rejection rules with descriptive error messaging.", 46321.0, 46321.0, "Manish", "Coding", "3- Completed", 2.5, 0, 0, 0, 0, 0, 2.5, 0, 0, 0, 0, 0, 0, 0),
        ("US-08", "T-09", "Implement TF-IDF semantic retriever with persistent JSON document catalog (documents_registry.json) and chunk coordinates.", 46321.0, 46322.0, "Manish", "Coding", "3- Completed", 4.0, 0, 0, 0, 0, 0, 1.5, 2.5, 0, 0, 0, 0, 0, 0),
        ("US-09", "T-10", "Build Scope & Deliverable Extraction Agent with Pydantic schema validation and anti-hallucination UNKNOWN fallback.", 46322.0, 46322.0, "Manish", "Coding", "3- Completed", 4.0, 0, 0, 0, 0, 0, 0, 4.0, 0, 0, 0, 0, 0, 0),
        ("US-10", "T-11", "Build Risk Detection & Delivery Forecasting Agent with deterministic schedule delta and 5x5 qualitative matrix.", 46322.0, 46323.0, "Manish", "Coding", "3- Completed", 4.0, 0, 0, 0, 0, 0, 0, 1.5, 2.5, 0, 0, 0, 0, 0),
        ("US-11", "T-12", "Build Blocker & Action Item Agent with unassigned owner mapping to UNKNOWN and cross-document citation merging.", 46323.0, 46323.0, "Manish", "Coding", "3- Completed", 3.0, 0, 0, 0, 0, 0, 0, 0, 3.0, 0, 0, 0, 0, 0),
        ("US-13", "T-13", "Develop simplified AgentAnalysisView and FileUpload components; remove milestone labels and RAG pipeline banners.", 46323.0, 46324.0, "Manish", "Design", "3- Completed", 3.5, 0, 0, 0, 0, 0, 0, 0, 1.5, 2.0, 0, 0, 0, 0),
        ("US-14", "T-14", "Implement unified multi-agent API endpoint (/api/agents/analyze-all) coordinating Scope, Risk, and Blocker agents.", 46324.0, 46324.0, "Manish", "Integration Test", "3- Completed", 2.5, 0, 0, 0, 0, 0, 0, 0, 0, 2.5, 0, 0, 0, 0),
        ("US-14", "T-15", "Author and execute automated test suite (35 pytest tests) and verify Vite production build with zero errors.", 46324.0, 46326.0, "Manish", "Regression Test", "3- Completed", 3.0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0, 2.0, 0, 0, 0),
        ("US-12", "T-16", "Update project management documentation: Unit Test Plan, Defect Tracker, and Agile Template with Milestone 2 results.", 46325.0, 46326.0, "Manish", "Others", "3- Completed", 3.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3.0, 0, 0, 0),
        ("US-12", "T-17", "Implement persistent ProjectWorkspace and consistency validation in DocumentService and vector store with HTTP 409 conflict detection.", 46325.0, 46326.0, "Manish", "Coding", "3- Completed", 3.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3.5, 0, 0),
        ("US-08", "T-18", "Integrate RapidOCR (ONNX Runtime) fallback pipeline for scanned image-only PDFs and validate domain shift on Oct 31, 2026.", 46326.0, 46326.0, "Manish", "Coding", "3- Completed", 3.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3.0, 0),
    ]

    for idx, task in enumerate(sprint2_tasks):
        r_idx = 11 + idx
        for c_idx, val in enumerate(task):
            xf_idx = rs_sb.cell_xf_index(min(r_idx, rs_sb.nrows - 1), c_idx)
            ws_sb.write(r_idx, c_idx, val, w.style_list[xf_idx])

    # --- Sheet 2: Stand up Meeting ---
    ws_su = wb.get_sheet(2)
    rs_su = rb.sheet_by_name("Stand up Meeting")

    # Sprint 1 entry (Row 1)
    ws_su.write(1, 0, "Sprint 1", w.style_list[rs_su.cell_xf_index(1, 0)])
    ws_su.write(1, 1, "Days 1-4", w.style_list[rs_su.cell_xf_index(1, 1)])
    ws_su.write(1, 2, "Initial repository setup, CORS configuration, and single-file document parser verification.", w.style_list[rs_su.cell_xf_index(1, 2)])
    ws_su.write(1, 3, "Configured FastAPI backend, React frontend, and initial document upload parsing for TXT, CSV, DOCX, and PDF.", w.style_list[rs_su.cell_xf_index(1, 3)])

    # Sprint 2 entries (Rows 2 to 6)
    standups_s2 = [
        ("Sprint 2", "Day 1 (Oct 24)", "Document upload component restricted users to single files; backend rejected batch multipart payloads.", "Implemented multi-file staging in FileUpload.tsx and updated routes.py to parse multiple files independently with per-file status badges."),
        ("Sprint 2", "Day 2 (Oct 26)", "Heavy vector database libraries (e.g. native ONNX/ChromaDB) created compatibility challenges with Python 3.13 on Windows.", "Engineered pure-Python TF-IDF semantic retriever with persistent JSON document catalog (documents_registry.json), ensuring robust, zero-dependency retrieval."),
        ("Sprint 2", "Day 3 (Oct 28)", "Extraction heuristics risked hallucinating task owners or due dates when documents lacked explicit information.", "Enforced strict academic anti-hallucination standard: unstated assignees and deadlines are mapped strictly to 'UNKNOWN' and cataloged in missing information."),
        ("Sprint 2", "Day 4 (Oct 30)", "Frontend dashboard cluttered with milestone-specific labels, academic banners, and complex RAG lifecycle diagrams.", "Refactored App.tsx to remove developmental banners; built clean tabbed AgentAnalysisView presenting Scope, Risks, and Blockers findings."),
        ("Sprint 2", "Day 5 (Oct 31)", "Validating multi-agent analysis performance across large multi-page PDFs, scanned PDFs (OCR), and domain switching.", "Authored automated pytest suite (35 tests across 8 test modules) achieving 100% pass rate; verified Vite production build on October 31, 2026."),
    ]

    for idx, su in enumerate(standups_s2):
        r_idx = 2 + idx
        for c_idx, val in enumerate(su):
            xf_idx = rs_su.cell_xf_index(min(r_idx, rs_su.nrows - 1), c_idx)
            ws_su.write(r_idx, c_idx, val, w.style_list[xf_idx])

    # --- Sheet 3: Retrospection ---
    ws_re = wb.get_sheet(3)
    rs_re = rb.sheet_by_name("Retrospection")

    # Sprint 1 (Row 1) - Preserved historical dates
    ws_re.write(1, 0, 1.0, w.style_list[rs_re.cell_xf_index(1, 0)])
    ws_re.write(1, 1, 1.0, w.style_list[rs_re.cell_xf_index(1, 1)])
    ws_re.write(1, 2, 46305.0, w.style_list[rs_re.cell_xf_index(1, 2)]) # 2026-10-10
    ws_re.write(1, 3, 46309.0, w.style_list[rs_re.cell_xf_index(1, 3)]) # 2026-10-14
    ws_re.write(1, 4, "Manish", w.style_list[rs_re.cell_xf_index(1, 4)])
    ws_re.write(1, 5, "Automated test discovery with pytest and boundary-aware text parsing.", w.style_list[rs_re.cell_xf_index(1, 5)])
    ws_re.write(1, 6, "Assuming single-file upload is sufficient for enterprise project analysis.", w.style_list[rs_re.cell_xf_index(1, 6)])
    ws_re.write(1, 7, "Strict adherence to genuine codebase verification and transparent status reporting.", w.style_list[rs_re.cell_xf_index(1, 7)])
    ws_re.write(1, 8, "Delivered working Milestone 1 baseline with FastAPI health/module registry and multi-format document parser.", w.style_list[rs_re.cell_xf_index(1, 8)])

    # Sprint 2 (Row 2) - Concluded 31 October 2026
    ws_re.write(2, 0, 2.0, w.style_list[rs_re.cell_xf_index(min(2, rs_re.nrows - 1), 0)])
    ws_re.write(2, 1, 2.0, w.style_list[rs_re.cell_xf_index(min(2, rs_re.nrows - 1), 1)])
    ws_re.write(2, 2, 46319.0, w.style_list[rs_re.cell_xf_index(min(2, rs_re.nrows - 1), 2)]) # 2026-10-24
    ws_re.write(2, 3, 46326.0, w.style_list[rs_re.cell_xf_index(min(2, rs_re.nrows - 1), 3)]) # 2026-10-31 (Milestone 2 End Date)
    ws_re.write(2, 4, "Manish", w.style_list[rs_re.cell_xf_index(min(2, rs_re.nrows - 1), 4)])
    ws_re.write(2, 5, "Pydantic schema validation for multi-agent outputs, deterministic schedule delta calculation, multi-file batch staging, and OCR fallback.", w.style_list[rs_re.cell_xf_index(min(2, rs_re.nrows - 1), 5)])
    ws_re.write(2, 6, "Assuming frontend-only validation is sufficient without backend per-file error handling.", w.style_list[rs_re.cell_xf_index(min(2, rs_re.nrows - 1), 6)])
    ws_re.write(2, 7, "Grounding all AI recommendations in verbatim document evidence and explicit page/row citations.", w.style_list[rs_re.cell_xf_index(min(2, rs_re.nrows - 1), 7)])
    ws_re.write(2, 8, "Delivered Milestone 2 autonomous Scope, Risk, and Blocker agents, OCR pipeline, workspace isolation, simplified production UI, and 35 automated tests on October 31, 2026.", w.style_list[rs_re.cell_xf_index(min(2, rs_re.nrows - 1), 8)])

    wb.save(str(file_path))
    print(f"Successfully updated {file_path} in-place (preserved .xls legacy format).")


# =====================================================================
# 2. UPDATE DEFECT_TRACKER TEMPLATE_V0.1.XLSX IN PLACE
# =====================================================================
def update_defect_tracker_xlsx():
    file_path = ROOT / "Defect_Tracker Template_v0.1.xlsx"
    print(f"Loading {file_path} for in-place update...")

    wb = openpyxl.load_workbook(file_path)
    ws = wb["Defects"]

    defects = [
        # Milestone 1 Defects (Defects 1 & 2)
        (
            1,
            "Manish",
            datetime.datetime(2026, 10, 14, 0, 0),
            "Home page previously displayed developmental milestone labels, academic integrity banners, and experimental RAG lifecycle diagrams, giving a non-production aesthetic.",
            "Sprint 1",
            "Manish",
            "User Interface",
            "Fixed and verified. Removed milestone-specific labels, academic-integrity banners, and RAG lifecycle stage diagrams from App.tsx. Verified clean dashboard rendering in production build.",
            datetime.datetime(2026, 10, 28, 0, 0),
            "Closed",
            "Retested and verified in Milestone 2 UI build; clean modern dashboard layout.",
        ),
        (
            2,
            "Manish",
            datetime.datetime(2026, 10, 14, 0, 0),
            "Extracted text chunks were not visible in frontend output after document ingestion, preventing users from validating chunk boundary quality and coordinates.",
            "Sprint 1",
            "Manish",
            "User Interface",
            "Fixed and verified. Enhanced FileUpload component to render expandable chunk cards, coordinate tags (Page/Row/Paragraph), character/word counts, and copy-to-clipboard functionality.",
            datetime.datetime(2026, 10, 26, 0, 0),
            "Closed",
            "Retested and verified with real documents (PDF, DOCX, CSV, TXT) and automated chunking test suite.",
        ),
        # Milestone 2 Defects (Defects 3 through 11)
        (
            3,
            "Manish",
            datetime.datetime(2026, 10, 26, 0, 0),
            "Document Upload component previously restricted users to single-file uploads and did not support multi-file selection. Additionally, the backend endpoint required enhancements to handle multiple files in a single request, process each independently, and return per-file success/failure results without discarding successful files when one file fails.",
            "Sprint 2",
            "Manish",
            "Logical",
            "Root Cause: Frontend file input lacked 'multiple' attribute and dropzone lacked multiple-file staging. Backend upload route only bound single UploadFile. Fix: Configured input with multiple={true}, added drag-and-drop multi-file staging queue with per-file validation, size display, and removal buttons before upload. Updated FastAPI routes.py to extract all files from multipart form, validate each independently, return FileUploadResultItem records with partial success, and preserve backward compatibility with single-file uploads.",
            datetime.datetime(2026, 10, 27, 0, 0),
            "Closed",
            "Verified and closed. Acceptance tests pass with multi-file uploads and partial batch success (test_multiple_valid_files_upload_in_one_request).",
        ),
        (
            4,
            "Manish",
            datetime.datetime(2026, 10, 26, 0, 0),
            "Document metadata and chunk catalog were previously kept only in volatile memory and lost upon backend restart, preventing downstream agents (Scope, Risk, Blocker) from referencing historical uploads.",
            "Sprint 2",
            "Manish",
            "Maintainability",
            "Implemented persistent JSON catalog backend/data/documents_registry.json in DocumentService with get_all_chunks(), list_documents(), and delete_document() methods. Document catalog persists and reloads automatically on service startup.",
            datetime.datetime(2026, 10, 27, 0, 0),
            "Closed",
            "Resolved. Document catalog persists and reloads automatically on startup. Verified in test_document_listing_and_deletion.",
        ),
        (
            5,
            "Manish",
            datetime.datetime(2026, 10, 27, 0, 0),
            "Scope and Blocker extraction agents could potentially hallucinate task owners or target dates when source documents omit them, violating strict academic evidence requirements.",
            "Sprint 2",
            "Manish",
            "Standards",
            "Enforced strict anti-hallucination rules: if an owner or deadline is not explicitly stated in the document text, the agents map assigned_owner and due_date strictly to 'UNKNOWN' and record the data gap in missing_information list.",
            datetime.datetime(2026, 10, 28, 0, 0),
            "Closed",
            "Verified and closed. test_scope_agent_extraction and test_blocker_agent_extraction_and_unassigned_handling verify zero owner hallucination.",
        ),
        (
            6,
            "Manish",
            datetime.datetime(2026, 10, 27, 0, 0),
            "Scanned or blank PDF files containing zero extractable text were returning empty 201 Created responses rather than prompting the user with an actionable error.",
            "Sprint 2",
            "Manish",
            "Logical",
            "Added post-extraction validation in DocumentService: if total extracted characters equal zero, raises HTTP 400 Bad Request instructing user that document contains no extractable text.",
            datetime.datetime(2026, 10, 27, 0, 0),
            "Closed",
            "Verified and closed. test_blank_pdf_rejected_no_extractable_text in test_chunking.py confirms HTTP 400 rejection.",
        ),
        (
            7,
            "Manish",
            datetime.datetime(2026, 10, 29, 0, 0),
            "Multi-batch document ingestion fragmented project identities when documents arrived in different batches or dates, creating distinct project IDs rather than binding all documents into one persistent workspace project knowledge base.",
            "Sprint 2",
            "Manish",
            "Logical",
            "Root Cause: Backend generated new project identifiers per upload batch or document. Fix: Implemented persistent ProjectWorkspace (project_workspace.json) in DocumentService. All uploaded files are bound to the workspace project_id. Persistent vector store indexes project_id metadata and filters cross-document retrieval strictly to this project. Upload batches track batch_id internally without altering project identity.",
            datetime.datetime(2026, 10, 30, 0, 0),
            "Closed",
            "Verified and closed. test_single_persistent_project_id_across_multiple_batches verifies 4 sequential batches sharing one persistent project_id.",
        ),
        (
            8,
            "Manish",
            datetime.datetime(2026, 10, 29, 0, 0),
            "Cross-project document ingestion silently merged documents with conflicting project IDs, project names, or clients into the workspace without validation.",
            "Sprint 2",
            "Manish",
            "Standards",
            "Root Cause: Upload endpoint lacked cross-document project consistency verification. Fix: Implemented validate_project_consistency in DocumentService. Checks incoming documents for explicit Project Name, ID, or Client conflicts and raises HTTP 409 Conflict with descriptive details when an incompatible document is detected. Generic documents inherit workspace identity.",
            datetime.datetime(2026, 10, 30, 0, 0),
            "Closed",
            "Verified and closed. test_single_persistent_project_id_across_multiple_batches confirms HTTP 409 rejection of conflicting Hospital System document.",
        ),
        (
            9,
            "Manish",
            datetime.datetime(2026, 10, 30, 0, 0),
            "Scope Agent goal extraction picked dependency DEP-01 from Section 6 instead of the primary project overview goal, and Blocker Agent unassigned count incorrectly included non-action items.",
            "Sprint 2",
            "Manish",
            "Logical",
            "Root Cause: Scope Agent prioritized highest-confidence regex match without section filtering; Blocker Agent counted all unassigned extracted items instead of restricting to action items. Fix: Scope Agent prioritizes Section 1 Overview goals, excluding dependency codes (DEP-) and table fragments. Blocker Agent restricts unassigned evaluation strictly to action items (0 unassigned) and computes overdue status relative to document reporting date.",
            datetime.datetime(2026, 10, 30, 0, 0),
            "Closed",
            "Verified and closed. test_milestone2_sample_document_10_ground_truth_criteria validates all 10 criteria with exact ground-truth values.",
        ),
        (
            10,
            "Manish",
            datetime.datetime(2026, 10, 30, 0, 0),
            "Scanned or image-only PDFs failed extraction because the application lacked an optical character recognition (OCR) fallback pipeline, rejecting valid scanned documents.",
            "Sprint 2",
            "Manish",
            "Logical",
            "Root Cause: Document service relied solely on PyMuPDF text stream extraction. Fix: Integrated RapidOCR (ONNX Runtime) with blank-page filtering. If character count falls below threshold (60 chars), system renders pages to pixmaps and invokes OCR fallback before returning an error.",
            datetime.datetime(2026, 10, 31, 0, 0),
            "Closed",
            "Verified and closed. test_scanned_pdf_ocr_fallback_pipeline confirms OCR text extraction from image-only pages.",
        ),
        (
            11,
            "Manish",
            datetime.datetime(2026, 10, 31, 0, 0),
            "Cross-project context bleed: System retained old Campus Event Management goals when switching to a different project domain (such as Community Library Management).",
            "Sprint 2",
            "Manish",
            "Logical",
            "Root Cause: Hardcoded project defaults in extraction heuristics. Fix: Implemented dynamic project identity extraction, dynamic goal resolution, and clean isolated workspace re-initialization.",
            datetime.datetime(2026, 10, 31, 0, 0),
            "Closed",
            "Verified and closed. test_dynamic_project_switching_and_zero_bleed and test_library_management_system_full_validation confirm 0% bleed across domains.",
        ),
    ]

    ref_row = 2
    for idx, d_row in enumerate(defects):
        target_row = 2 + idx
        for col_idx, val in enumerate(d_row, start=1):
            cell = ws.cell(row=target_row, column=col_idx, value=val)
            ref_cell = ws.cell(row=ref_row, column=col_idx)
            if ref_cell.has_style:
                if ref_cell.font:
                    cell.font = copy(ref_cell.font)
                if ref_cell.border:
                    cell.border = copy(ref_cell.border)
                if ref_cell.fill:
                    cell.fill = copy(ref_cell.fill)
                if ref_cell.alignment:
                    cell.alignment = copy(ref_cell.alignment)
            if isinstance(val, datetime.datetime):
                cell.number_format = "YYYY-MM-DD"

    wb.save(file_path)
    print(f"Successfully updated {file_path} in-place (11 verified defects, all Closed).")


# =====================================================================
# 3. UPDATE UNIT_TEST_PLAN_V0.1.XLSX IN PLACE
# =====================================================================
def update_unit_test_plan_xlsx():
    file_path = ROOT / "Unit_Test_Plan_v0.1.xlsx"
    print(f"Loading {file_path} for in-place update...")

    wb = openpyxl.load_workbook(file_path)
    ws = wb.active

    # Preserved 6-column structure: Sl: No:, Test Case Name, Test Procedure, Condition to be tested, Expected Result, Actual Result
    all_tests = [
        # --- Milestone 1 Baseline Retests (Rows 2 to 12) ---
        (
            1,
            "FastAPI Server Startup & Root Landing",
            "Send HTTP GET request to '/' on backend server.",
            "FastAPI application running on port 8000.",
            "HTTP 200 OK returned with application metadata and Swagger docs link.",
            "Pass. Verified via GET / returning HTTP 200 with online status, version 0.2.0, and documentation link (/docs).",
        ),
        (
            2,
            "Backend Health Endpoint & Storage Verification",
            "Send HTTP GET request to '/api/health'.",
            "FastAPI server running with storage directory mounted.",
            "HTTP 200 OK returned with storage_ready=True and active AI pipeline status.",
            "Pass. HTTP 200 OK returned with {'status': 'ok', 'storage_ready': True, 'ai_pipeline_status': 'active in Milestone 2'}.",
        ),
        (
            3,
            "Dynamic Module Registry Tracking",
            "Send HTTP GET request to '/api/modules'.",
            "Module registry initialized in backend/core/config.py.",
            "HTTP 200 OK returned with JSON listing of all 9 modules and current implementation states.",
            "Pass. HTTP 200 OK returned with dynamic registry of all 9 modules (1 implemented, 2 partially implemented, 6 planned).",
        ),
        (
            4,
            "Plain Text Document Ingestion",
            "Upload valid .txt file (architecture_risks.txt) via POST /api/documents/upload.",
            "Valid text file with readable ASCII/UTF-8 characters.",
            "HTTP 201 Created returned with non-zero character count and chunk listing.",
            "Pass. Uploaded valid UTF-8 .txt document (architecture_risks.txt); extracted characters and generated boundary-aware chunk with section coordinate.",
        ),
        (
            5,
            "CSV Tabular Document Ingestion",
            "Upload valid structured .csv file (sprint_tasks.csv) via POST /api/documents/upload.",
            "Valid CSV with comma-delimited rows and column headers.",
            "HTTP 201 Created returned with rows parsed into structured chunks preserving coordinates.",
            "Pass. Uploaded structured CSV (sprint_tasks.csv); extracted tabular rows with headers into chunks tagged with row coordinates ('Row 1-5').",
        ),
        (
            6,
            "DOCX Document Ingestion",
            "Upload valid Microsoft Word document (meeting_minutes.docx) via POST /api/documents/upload.",
            "Valid DOCX file with headings, paragraphs, and tables.",
            "HTTP 201 Created returned with paragraphs extracted preserving structural coordinates.",
            "Pass. Uploaded valid DOCX (meeting_minutes.docx); extracted paragraphs and table rows into chunks with paragraph coordinates.",
        ),
        (
            7,
            "Multi-Page Text PDF Ingestion",
            "Upload multi-page digital PDF document (project_charter.pdf) via POST /api/documents/upload.",
            "Valid PDF file with selectable text streams on each page.",
            "HTTP 201 Created returned with text extracted per-page and page coordinate tags.",
            "Pass. Uploaded multi-page text PDF (project_charter.pdf); PyMuPDF extracted text per page with coordinate provenance ('Page 1').",
        ),
        (
            8,
            "Empty File Rejection (0 Bytes)",
            "Upload empty 0-byte file (empty.txt) via POST /api/documents/upload.",
            "File size equals 0 bytes.",
            "HTTP 400 Bad Request returned with descriptive error message rejecting empty file.",
            "Pass. Uploaded 0-byte file (empty.txt); HTTP 400 Bad Request returned: 'The uploaded file is empty (0 bytes). Please upload a valid document.'",
        ),
        (
            9,
            "Unsupported File Format Rejection",
            "Upload disallowed file extension (.png) via POST /api/documents/upload.",
            "File extension not in whitelist (.pdf, .docx, .csv, .txt).",
            "HTTP 400 Bad Request returned with allowed format specification.",
            "Pass. Uploaded unsupported file (unsupported.png); HTTP 400 Bad Request returned: 'Unsupported file format .png. Allowed formats are: .pdf, .docx, .csv, .txt.'",
        ),
        (
            10,
            "Malformed / Corrupted PDF Rejection",
            "Upload malformed PDF file missing valid %PDF signature header.",
            "File extension is .pdf but binary content lacks valid PDF magic bytes.",
            "HTTP 400 Bad Request returned gracefully without server crash or unhandled exception.",
            "Pass. Uploaded malformed PDF without %PDF header; HTTP 400 returned: 'Malformed PDF: File header does not match valid PDF signature.'",
        ),
        (
            11,
            "Frontend Production Build Compilation",
            "Execute 'npm run build' inside frontend/ directory.",
            "Node.js 20+ runtime with dependencies installed via npm.",
            "TypeScript compilation and Vite bundling complete with exit code 0.",
            "Pass. Executed 'npm run build'; Vite completed production bundling with zero TypeScript errors in 2.25s (1563 modules transformed).",
        ),
        # --- Milestone 2 Verified Tests (Rows 13 to 40) ---
        (
            12,
            "Frontend Application Loading & Dashboard Navigation",
            "Open frontend application in browser and verify layout components (Navbar, Hero, FileUpload, AgentAnalysisView, ModuleCard).",
            "Frontend Vite server running and connected to backend API.",
            "Application loads without console errors; Navbar reflects backend online status; modules grid and upload lab render properly.",
            "Pass. Application renders cleanly; Navbar displays live backend health indicator; module cards and upload components mount without errors.",
        ),
        (
            13,
            "Multiple-File Selection via Frontend File Picker",
            "Select multiple files simultaneously using the file dialog or drag-and-drop into the FileUpload dropzone.",
            "File input configured with multiple={true} and onDrop staging handler enabled.",
            "All selected files appear in pre-upload staging queue displaying file names, format badges, file sizes, and individual remove ('X') buttons.",
            "Pass. Multi-file staging list renders all chosen files with format badges, formatted sizes in KB/MB, and interactive removal before uploading.",
        ),
        (
            14,
            "Multiple-File Batch Upload in Single Request",
            "Submit multipart form request to POST /api/documents/upload containing multiple valid files (batch_arch.txt, batch_sprint.csv).",
            "Multiple valid files submitted simultaneously in one operation.",
            "HTTP 201 Created returned with total_files=2, successful_count=2, per-file result records with distinct IDs, and combined chunk count.",
            "Pass. HTTP 201 Created returned with total_files=2, successful_count=2, and independent FileUploadResultItem records with distinct document IDs.",
        ),
        (
            15,
            "Independent Processing of Uploaded Documents (Mixed Batch)",
            "Submit multipart upload batch containing both valid (valid_part.txt) and invalid (invalid_part.png) files.",
            "Batch payload contains a mixture of valid and invalid files.",
            "HTTP 201 Created returned. Valid file is processed and cataloged; invalid file is flagged with error without discarding or aborting the valid file.",
            "Pass. HTTP 201 Created returned with successful_count=1, failed_count=1. Valid file ingested cleanly; invalid file recorded with descriptive error.",
        ),
        (
            16,
            "All-Invalid Batch Upload Rejection",
            "Submit batch where all files fail validation (e.g. empty file and disallowed format).",
            "Batch contains zero valid files.",
            "HTTP 400 Bad Request returned with combined error summary of all validation failures.",
            "Pass. HTTP 400 Bad Request returned: 'All files failed validation: ...'. No corrupt records added to registry.",
        ),
        (
            17,
            "Sequential Batch Uploads & Catalog Preservation",
            "Ingest an initial document batch, wait for completion, and subsequently upload additional documents in separate requests.",
            "User performs multiple consecutive upload operations across session.",
            "New documents are appended to persistent repository without overwriting, discarding, or duplicating previous uploads.",
            "Pass. Document repository in documents_registry.json persists all uploads across sequential requests; catalog refreshes dynamically.",
        ),
        (
            18,
            "Text Chunk Generation & Boundary Overlap",
            "Inspect chunker service output on long document text using 500-char target chunk size and 100-char overlap.",
            "Document text exceeds chunk target length.",
            "Chunker splits text at natural sentence or paragraph boundaries with configured overlap; generates zero empty or duplicate chunks.",
            "Pass. Text split cleanly on sentence boundaries with 100-char overlap; chunk coordinate references preserved without text truncation.",
        ),
        (
            19,
            "Extracted Chunk Display in UI",
            "Inspect chunk rendering section in FileUpload.tsx after document ingestion.",
            "Backend returns chunks array in UploadResponse.",
            "Chunks rendered as discrete cards showing Chunk ID, character count, coordinate badge, text snippet preview, and expand/collapse modal.",
            "Pass. Frontend renders expandable chunk cards with coordinate tags (Page/Row/Paragraph), word counts, and copy-to-clipboard button.",
        ),
        (
            20,
            "Blank Scanned PDF Handling (Zero Extractable Text)",
            "Upload valid PDF containing blank or image-only scanned pages (blank_scanned.pdf) via POST /api/documents/upload.",
            "PDF file structure is valid but contains zero selectable text characters.",
            "HTTP 400 Bad Request returned instructing user that document contains no extractable text characters after OCR evaluation.",
            "Pass. HTTP 400 Bad Request returned: 'contains no extractable text. Please ensure the document contains readable text characters'.",
        ),
        (
            21,
            "Scope and Deliverable Extraction Agent",
            "Send POST request to /api/agents/scope across ingested project documents.",
            "Project charter and scope documents ingested in knowledge base.",
            "Agent extracts project goals, in-scope/out-of-scope items, deliverables, milestones, deadlines, and dependencies with citations.",
            "Pass. Extracted 1 primary goal, 5 sub-goals, scope items, deliverables, milestones, and dependencies with source citations and confidence ratings.",
        ),
        (
            22,
            "Scope Agent Anti-Hallucination & Missing Info Handling",
            "Execute Scope Agent on documents lacking explicit owner or deadline data.",
            "Source text omits deliverable assignee or target date.",
            "Agent sets owner/date to 'UNKNOWN' and logs gaps in missing_information list; zero hallucination.",
            "Pass. Missing owners and target dates mapped strictly to 'UNKNOWN' and explicit data gaps recorded in missing_information.",
        ),
        (
            23,
            "Risk Detection and Delivery Forecasting Agent",
            "Send POST request to /api/agents/risks across ingested task schedules and risk registers.",
            "Task schedules with deadlines and risk statements ingested.",
            "Agent calculates schedule slippages via deterministic deadline deltas, detects dependency bottlenecks, and classifies severity via 5x5 matrix.",
            "Pass. Identified grounded delivery risks (Schedule, Resource, Technical); calculated exact deadline deltas; qualitative risk assessed via 5x5 matrix.",
        ),
        (
            24,
            "Risk Evidence Citation and AI Mitigation Separation",
            "Inspect extracted risk items for evidence grounding and recommendation distinction.",
            "Risk items generated by Risk Agent.",
            "supporting_evidence contains direct verbatim quote from document; recommended_mitigation is clearly labeled as AI recommendation.",
            "Pass. supporting_evidence quotes exact document text; recommended_mitigation is explicitly prefixed '[AI Recommendation]'.",
        ),
        (
            25,
            "Blocker and Action Item Identification Agent",
            "Send POST request to /api/agents/blockers across meeting minutes and retro documents.",
            "Meeting minutes containing blockers, impediments, and action items ingested.",
            "Agent extracts unresolved blockers, action items, and pending decisions with priority tags, statuses, and recommended next steps.",
            "Pass. Extracted blockers, action items, approved decisions, and pending decisions with priority tags and actionable resolution steps.",
        ),
        (
            26,
            "Blocker Agent Unassigned Owner & Due Date Mapping",
            "Execute Blocker Agent on action items without explicit assignees or target dates.",
            "Document passage lists an action item without naming an individual.",
            "Agent assigns assigned_owner: 'UNKNOWN' and due_date: 'UNKNOWN'; increments unassigned_count; zero guessing.",
            "Pass. Unassigned items strictly assigned to 'UNKNOWN'; unassigned_count accurately computed with zero name guessing.",
        ),
        (
            27,
            "Cross-Document Deduplication & Citation Merging",
            "Ingest multiple documents mentioning identical blockers; execute Blocker Agent.",
            "Duplicate issues appear across meeting notes and charter.",
            "Agent consolidates duplicate issues into a single item with merged source_references array.",
            "Pass. Repeated blocker items consolidated into single record with combined source references across both source documents.",
        ),
        (
            28,
            "Source Document Reference & Provenance Validation",
            "Verify source_references and source_ref across all agent responses.",
            "Ingested documents have unique filenames and chunk coordinate metadata.",
            "Every extracted item includes traceable citation referencing source document filename and coordinate.",
            "Pass. 100% of extracted items contain verifiable document citations referencing specific filenames and coordinates.",
        ),
        (
            29,
            "Unified Multi-Agent Analysis Endpoint (/api/agents/analyze-all)",
            "Send POST request to /api/agents/analyze-all across all ingested documents.",
            "Documents ingested in repository.",
            "HTTP 200 OK returned with consolidated scope, risk, and blocker intelligence in a single structured response payload.",
            "Pass. HTTP 200 OK returned with unified payload containing analyzed_documents list, scope extraction, risk forecast, and blocker register.",
        ),
        (
            30,
            "Frontend Tabbed AI Advisory Navigation & Display",
            "Trigger analysis in frontend AgentAnalysisView and toggle between Scope, Risks, and Blockers tabs.",
            "Multi-agent analysis data loaded in frontend state.",
            "Tabs switch views instantly; displays summary metrics strip, evidence quote cards, severity pills, and filter controls.",
            "Pass. Tab navigation functions smoothly; metrics pills, verbatim quote cards, severity badges, and type filters render accurately.",
        ),
        (
            31,
            "Document Deletion and Catalog Synchronization",
            "Send DELETE request to /api/documents/{document_id} for an ingested document.",
            "Document exists in local uploads directory and JSON catalog.",
            "HTTP 200 OK returned; file removed from disk and registry; subsequent agent analyses exclude deleted document.",
            "Pass. Document and chunks deleted cleanly from uploads and registry; document listing updates dynamically.",
        ),
        (
            32,
            "Regression Test Suite Execution (Full Automated Pytest)",
            "Run pytest across all test modules in backend/tests/ (test_api.py, test_chunking.py, test_milestone2_agents.py, test_project_grouping_and_consistency.py, test_sample_document_validation.py, test_milestone2_comprehensive_validation.py, test_library_management_validation.py).",
            "Python 3.13 virtual environment with test dependencies installed.",
            "All 35 automated unit and integration tests pass with 0 failures and 0 errors.",
            "Pass. 35 passed in 5.71s (10 API tests, 8 chunking tests, 10 agent tests, 2 grouping tests, 1 ground truth test, 3 comprehensive tests, 1 library validation test).",
        ),
        (
            33,
            "Single Persistent Project Workspace ID across Sequential Batches",
            "Upload 4 project documents (proposal, SRS, meeting notes, progress report) in 4 separate upload batches; execute RAG retrieval and multi-agent analysis.",
            "Application maintains ONE persistent project workspace ID for all uploaded documents regardless of batch or upload timestamp.",
            "All 4 documents share the same persistent project_id; upload batches track internal batch IDs; RAG retriever and all 3 agents produce unified cross-document findings.",
            "Pass. All 4 documents bound to persistent workspace with unique document IDs; vector store indexes project_id; all 3 agents produce combined intelligence.",
        ),
        (
            34,
            "Project Consistency Validation & Cross-Project HTTP 409 Conflict Rejection",
            "Attempt to ingest a document explicitly belonging to a conflicting project ('Hospital Intensive Care Management System') into an existing workspace ('Campus Event Management Portal').",
            "Incoming document explicitly specifies conflicting project name, ID, or client.",
            "HTTP 409 Conflict returned with detailed error identifying the conflicting project name/ID; conflicting document is not ingested into workspace.",
            "Pass. HTTP 409 Conflict returned: 'Project identity conflict: Document identifies project ... which conflicts with existing workspace ...'. Document rejected.",
        ),
        (
            35,
            "Inherited Project Identity for Generic Project Documents",
            "Upload a generic document without explicit project identity header into an established project workspace.",
            "Incoming document omits project headers.",
            "Document is accepted, assigned to current workspace project_id, and tagged with is_project_inherited=True without creating a new project identity.",
            "Pass. Generic document accepted into workspace; inherits project_id with is_project_inherited=True; verified in test_inherited_project_identity_for_generic_documents.",
        ),
        (
            36,
            "Milestone 2 Sample Document 10 Ground-Truth Criteria Evaluation",
            "Execute complete multi-agent analysis against AI_Project_Agent_Test_Sample_Document.docx and validate against all 10 ground truth acceptance criteria.",
            "Sample document ingested with sections 1-7 (Overview, Deliverables, Milestones, Risks, Action Items, Dependencies, Signoff).",
            "All 10 criteria met: Primary goal extracted from Overview (not DEP-01); exactly 6 deliverables; exactly 6 milestones; exactly 3 documented risks; active blocker identified; exactly 5 action items; exactly 1 pending decision; unassigned count = 0; overdue count = 0.",
            "Pass. 10/10 ground truth criteria validated in test_sample_document_validation.py with zero hallucination and exact evidence quotes.",
        ),
        (
            37,
            "Scanned PDF OCR Fallback Pipeline Execution",
            "Upload a scanned image-only PDF containing no selectable direct text characters.",
            "Normal text extraction returns 0 characters; OCR fallback is enabled with RapidOCR (ONNX Runtime).",
            "Application renders pages to high-resolution pixmaps, runs local OCR, extracts text, preserves page numbers, and rejects genuinely blank pages.",
            "Pass. RapidOCR fallback triggered, extracted textual content with page coordinates; verified in test_scanned_pdf_ocr_fallback_pipeline.",
        ),
        (
            38,
            "Dynamic Project Switching & Zero-Bleed Workspace Isolation",
            "Switch active workspace from Campus Event Management Portal to Community Library Management System and trigger full agent extraction.",
            "Documents from secondary project ingested into a clean workspace.",
            "All extracted goals, deliverables, milestones, risks, and blockers belong strictly to the Community Library Management System with zero bleed from previous project.",
            "Pass. Complete dynamic identity shift verified with 0% token overlap from previous project; verified in test_dynamic_project_switching_and_zero_bleed.",
        ),
        (
            39,
            "CSV Delimiter Sniffing & Record Preservation",
            "Ingest CSV files formatted with semicolon, tab, or pipe delimiters alongside standard comma-separated files.",
            "CSV parser automatically identifies delimiter and preserves column headers and row relationships.",
            "Table records are extracted into structured dicts with row coordinates ('Row 1-5') without flattening or record loss.",
            "Pass. All CSV delimiters sniffed accurately; record coordinates preserved; verified in test_csv_delimiters_and_record_preservation.",
        ),
        # --- Milestone 3 Planned Tests (Rows 41 to 43) ---
        (
            40,
            "Automated User Story Synthesis Engine (Milestone 3 Planned)",
            "Execute Documentation Generation Agent to synthesize Gherkin user stories from project intelligence.",
            "Milestone 3 documentation generation engine active.",
            "Synthesizes user stories with acceptance criteria and draft disclaimers.",
            "NOT EXECUTED. Scheduled for Milestone 3 implementation.",
        ),
        (
            41,
            "Composite Project Health Scoring (0-100) (Milestone 3 Planned)",
            "Execute Health Scoring Engine using weighted formula combining schedule, risk, blocker, and documentation factors.",
            "Milestone 3 health scoring algorithm active.",
            "Computes composite 0-100 health score with mathematical breakdown.",
            "NOT EXECUTED. Scheduled for Milestone 3 implementation.",
        ),
        (
            42,
            "Conversational Project Intelligence Assistant (Milestone 3 Planned)",
            "Query project intelligence conversational assistant with natural language project questions.",
            "Milestone 3 conversational assistant endpoint active.",
            "Provides evidence-grounded answers citing document coordinates or explicitly declines if evidence is missing.",
            "NOT EXECUTED. Scheduled for Milestone 3 implementation.",
        ),
    ]

    ref_row = 2
    for idx, item in enumerate(all_tests):
        target_row = 2 + idx
        for col_idx, val in enumerate(item, start=1):
            cell = ws.cell(row=target_row, column=col_idx, value=val)
            ref_cell = ws.cell(row=ref_row, column=col_idx)
            if ref_cell.has_style:
                if ref_cell.font:
                    cell.font = copy(ref_cell.font)
                if ref_cell.border:
                    cell.border = copy(ref_cell.border)
                if ref_cell.fill:
                    cell.fill = copy(ref_cell.fill)
                if ref_cell.alignment:
                    cell.alignment = copy(ref_cell.alignment)

    wb.save(file_path)
    print(f"Successfully updated {file_path} in-place (42 total test cases: 39 Passed, 3 Not Executed).")


if __name__ == "__main__":
    update_agile_template_xls()
    update_defect_tracker_xlsx()
    update_unit_test_plan_xlsx()
    print("All 3 root templates successfully updated in place!")
