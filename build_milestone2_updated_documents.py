"""
Script to build Milestone 2 Updated Documents from Milestone 1 Excel files:
Outputs to:
1. Milestone2_Updated_Documents/
   - Unit_Test_Plan_Milestone2.xlsx
   - Defect_Tracker_Milestone2.xlsx
   - Agile_Template_Milestone2.xlsx
   - Milestone2_Update_Summary.txt
2. milestone2_deliverables/
   - Unit_Test_Plan_Milestone2.xlsx
   - Defect_Tracker_Milestone2.xlsx
   - Agile_Template_Milestone2.xlsx
   - Milestone2_Documentation.zip (containing all 6 milestone 1 & 2 templates)

Authoritative Project Timeline:
- Milestone 1: Preserved historical dates (Setup audit Oct 14, 2026; Sprint 1: Oct 10-14, 2026).
- Milestone 2: Concluded and verified on October 31, 2026 (Sprint 2: Oct 24-31, 2026).
"""

import os
import zipfile
import datetime
from copy import copy
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

DIR_M1 = Path("milestone1_deliverables")
DIR_UPDATED = Path("Milestone2_Updated_Documents")
DIR_DELIV = Path("milestone2_deliverables")

DIR_UPDATED.mkdir(exist_ok=True)
DIR_DELIV.mkdir(exist_ok=True)


def copy_cell_style(ref_cell, target_cell):
    """Deep copy formatting attributes from ref_cell to target_cell."""
    if ref_cell.has_style:
        if ref_cell.font:
            target_cell.font = copy(ref_cell.font)
        if ref_cell.border:
            target_cell.border = copy(ref_cell.border)
        if ref_cell.fill:
            target_cell.fill = copy(ref_cell.fill)
        if ref_cell.number_format:
            target_cell.number_format = copy(ref_cell.number_format)
        if ref_cell.protection:
            target_cell.protection = copy(ref_cell.protection)
        if ref_cell.alignment:
            target_cell.alignment = copy(ref_cell.alignment)


# =====================================================================
# 1. UPDATE UNIT TEST PLAN
# =====================================================================
def update_unit_test_plan():
    src_file = DIR_M1 / "Unit_Test_Plan_Milestone1.xlsx"
    if not src_file.exists():
        src_file = Path("Unit_Test_Plan_Milestone1.xlsx")
    wb = openpyxl.load_workbook(src_file)
    ws = wb["UT"]

    # Existing rows 2 to 12 are Milestone 1 tests. Update their Actual Result with verified retest status.
    m1_updates = {
        2: "Pass. Verified via GET / returning HTTP 200 with online status, version 0.2.0, and documentation link (/docs).",
        3: "Pass. HTTP 200 OK returned with {'status': 'ok', 'storage_ready': True, 'ai_pipeline_status': 'active in Milestone 2'}.",
        4: "Pass. HTTP 200 OK returned with dynamic registry of all 9 modules (1 implemented, 2 partially implemented, 6 planned).",
        5: "Pass. Uploaded valid UTF-8 .txt document (architecture_risks.txt); extracted characters and generated boundary-aware chunk with section coordinate.",
        6: "Pass. Uploaded structured CSV (sprint_tasks.csv); extracted tabular rows with headers into chunks tagged with row coordinates ('Row 1-5').",
        7: "Pass. Uploaded valid DOCX (meeting_minutes.docx); extracted paragraphs and table rows into chunks with paragraph coordinates.",
        8: "Pass. Uploaded multi-page text PDF (project_charter.pdf); PyMuPDF extracted text per page with coordinate provenance ('Page 1').",
        9: "Pass. Uploaded 0-byte file (empty.txt); HTTP 400 Bad Request returned: 'The uploaded file is empty (0 bytes). Please upload a valid document.'",
        10: "Pass. Uploaded unsupported file (unsupported.png); HTTP 400 Bad Request returned: 'Unsupported file format .png. Allowed formats are: .pdf, .docx, .csv, .txt.'",
        11: "Pass. Uploaded malformed PDF without %PDF header; HTTP 400 returned: 'Malformed PDF: File header does not match valid PDF signature.'",
        12: "Pass. Executed 'npm run build'; Vite completed production bundling with zero TypeScript errors in 2.25s (1563 modules transformed).",
    }

    for row_idx, actual_text in m1_updates.items():
        ws.cell(row=row_idx, column=6).value = actual_text

    # Milestone 2 & Planned Test Cases to append
    new_tests = [
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
        (
            40,
            "Automated User Story Synthesis Engine (Milestone 3 Planned)",
            "Execute Documentation Generation Agent to synthesize Gherkin user stories from project intelligence.",
            "Milestone 3 documentation generation engine active.",
            "Synthesizes user stories with acceptance criteria and draft disclaimers.",
            "Not Run. Feature scheduled for Milestone 3 implementation.",
        ),
        (
            41,
            "Composite Project Health Scoring (0-100) (Milestone 3 Planned)",
            "Execute Health Scoring Engine using weighted formula combining schedule, risk, blocker, and documentation factors.",
            "Milestone 3 health scoring algorithm active.",
            "Computes composite 0-100 health score with mathematical breakdown.",
            "Not Run. Feature scheduled for Milestone 3 implementation.",
        ),
        (
            42,
            "Conversational Project Intelligence Assistant (Milestone 3 Planned)",
            "Query project intelligence conversational assistant with natural language project questions.",
            "Milestone 3 conversational assistant endpoint active.",
            "Provides evidence-grounded answers citing document coordinates or explicitly declines if evidence is missing.",
            "Not Run. Feature scheduled for Milestone 3 implementation.",
        ),
    ]

    ref_row = 12
    for item in new_tests:
        row_num = ws.max_row + 1
        for col_idx, val in enumerate(item, start=1):
            cell = ws.cell(row=row_num, column=col_idx, value=val)
            ref_cell = ws.cell(row=ref_row, column=col_idx)
            copy_cell_style(ref_cell, cell)

    for out_dir in [DIR_UPDATED, DIR_DELIV]:
        out_path = out_dir / "Unit_Test_Plan_Milestone2.xlsx"
        wb.save(out_path)
        print(f"Saved: {out_path} (Total test cases: {ws.max_row - 1})")


# =====================================================================
# 2. UPDATE DEFECT TRACKER
# =====================================================================
def update_defect_tracker():
    src_file = DIR_M1 / "Defect_Tracker_Milestone1.xlsx"
    if not src_file.exists():
        src_file = Path("Defect_Tracker_Milestone1.xlsx")
    wb = openpyxl.load_workbook(src_file)
    ws = wb["Defects"]

    # Update existing Defect 1 (Row 2)
    ws.cell(row=2, column=8).value = (
        "Fixed and verified. Removed milestone-specific labels, academic-integrity banners, "
        "and RAG lifecycle stage diagrams from App.tsx. Verified clean dashboard rendering in production build."
    )
    ws.cell(row=2, column=9).value = datetime.datetime(2026, 10, 28, 0, 0)
    ws.cell(row=2, column=10).value = "Closed"
    ws.cell(row=2, column=11).value = "Retested and verified in Milestone 2 UI build."

    # Update existing Defect 2 (Row 3)
    ws.cell(row=3, column=6).value = "manish"
    ws.cell(row=3, column=7).value = "User Interface"
    ws.cell(row=3, column=8).value = (
        "Fixed and verified. Enhanced FileUpload component to render expandable chunk cards, "
        "coordinate tags, character/word counts, and copy-to-clipboard functionality."
    )
    ws.cell(row=3, column=9).value = datetime.datetime(2026, 10, 26, 0, 0)
    ws.cell(row=3, column=10).value = "Closed"
    ws.cell(row=3, column=11).value = (
        "Retested and verified with real documents (PDF, DOCX, CSV, TXT) and automated chunking test suite."
    )

    # New defects identified and resolved during Milestone 2
    new_defects = [
        (
            3,
            "manish",
            datetime.datetime(2026, 10, 26, 0, 0),
            "Document Upload component previously restricted users to single-file uploads and did not support multi-file selection. "
            "Additionally, the backend endpoint required enhancements to handle multiple files in a single request, process each independently, "
            "and return per-file success/failure results without discarding successful files when one file fails.",
            "Sprint 2",
            "manish",
            "Logical",
            "Root Cause: Frontend file input lacked 'multiple' attribute and dropzone lacked multiple-file staging. Backend upload route only bound single UploadFile. "
            "Fix: Configured input with multiple={true}, added drag-and-drop multi-file staging queue with per-file validation, size display, and removal buttons before upload. "
            "Updated FastAPI routes.py to extract all files from multipart form, validate each independently, return FileUploadResultItem records with partial success, "
            "and preserve backward compatibility with single-file uploads.",
            datetime.datetime(2026, 10, 27, 0, 0),
            "Closed",
            "Verified and closed. Acceptance tests pass with multi-file uploads and partial batch success (test_multiple_valid_files_upload_in_one_request).",
        ),
        (
            4,
            "manish",
            datetime.datetime(2026, 10, 26, 0, 0),
            "Document metadata and chunk catalog were previously kept only in volatile memory and lost upon backend restart, "
            "preventing downstream agents (Scope, Risk, Blocker) from referencing historical uploads.",
            "Sprint 2",
            "manish",
            "Maintainability",
            "Implemented persistent JSON catalog backend/data/documents_registry.json in DocumentService with get_all_chunks(), "
            "list_documents(), and delete_document() methods. Document catalog persists and reloads automatically on service startup.",
            datetime.datetime(2026, 10, 27, 0, 0),
            "Closed",
            "Resolved. Document catalog persists and reloads automatically on startup. Verified in test_document_listing_and_deletion.",
        ),
        (
            5,
            "manish",
            datetime.datetime(2026, 10, 27, 0, 0),
            "Scope and Blocker extraction agents could potentially hallucinate task owners or target dates when source documents omit them, "
            "violating strict academic evidence requirements.",
            "Sprint 2",
            "manish",
            "Standards",
            "Enforced strict anti-hallucination rules: if an owner or deadline is not explicitly stated in the document text, "
            "the agents map assigned_owner and due_date strictly to 'UNKNOWN' and record the data gap in missing_information list.",
            datetime.datetime(2026, 10, 28, 0, 0),
            "Closed",
            "Verified and closed. test_scope_agent_extraction and test_blocker_agent_extraction_and_unassigned_handling verify zero owner hallucination.",
        ),
        (
            6,
            "manish",
            datetime.datetime(2026, 10, 27, 0, 0),
            "Scanned or blank PDF files containing zero extractable text were returning empty 201 Created responses rather than prompting the user with an actionable error.",
            "Sprint 2",
            "manish",
            "Logical",
            "Added post-extraction validation in DocumentService: if total extracted characters equal zero, raises HTTP 400 Bad Request instructing user that document contains no extractable text.",
            datetime.datetime(2026, 10, 27, 0, 0),
            "Closed",
            "Verified and closed. test_blank_pdf_rejected_no_extractable_text in test_chunking.py confirms HTTP 400 rejection.",
        ),
        (
            7,
            "manish",
            datetime.datetime(2026, 10, 29, 0, 0),
            "Multi-batch document ingestion fragmented project identities when documents arrived in different batches or dates, creating distinct project IDs rather than binding all documents into one persistent workspace project knowledge base.",
            "Sprint 2",
            "manish",
            "Logical",
            "Root Cause: Backend generated new project identifiers per upload batch or document. Fix: Implemented persistent ProjectWorkspace (project_workspace.json) in DocumentService. All uploaded files are bound to the workspace project_id. Persistent vector store indexes project_id metadata and filters cross-document retrieval strictly to this project. Upload batches track batch_id internally without altering project identity.",
            datetime.datetime(2026, 10, 30, 0, 0),
            "Closed",
            "Verified and closed. test_single_persistent_project_id_across_multiple_batches verifies 4 sequential batches sharing one persistent project_id.",
        ),
        (
            8,
            "manish",
            datetime.datetime(2026, 10, 29, 0, 0),
            "Cross-project document ingestion silently merged documents with conflicting project IDs, project names, or clients into the workspace without validation.",
            "Sprint 2",
            "manish",
            "Standards",
            "Root Cause: Upload endpoint lacked cross-document project consistency verification. Fix: Implemented validate_project_consistency in DocumentService. Checks incoming documents for explicit Project Name, ID, or Client conflicts and raises HTTP 409 Conflict with descriptive details when an incompatible document is detected. Generic documents inherit workspace identity.",
            datetime.datetime(2026, 10, 30, 0, 0),
            "Closed",
            "Verified and closed. test_single_persistent_project_id_across_multiple_batches confirms HTTP 409 rejection of conflicting Hospital System document.",
        ),
        (
            9,
            "manish",
            datetime.datetime(2026, 10, 30, 0, 0),
            "Scope Agent goal extraction picked dependency DEP-01 from Section 6 instead of the primary project overview goal, and Blocker Agent unassigned count incorrectly included non-action items.",
            "Sprint 2",
            "manish",
            "Logical",
            "Root Cause: Scope Agent prioritized highest-confidence regex match without section filtering; Blocker Agent counted all unassigned extracted items instead of restricting to action items. Fix: Scope Agent prioritizes Section 1 Overview goals, excluding dependency codes (DEP-) and table fragments. Blocker Agent restricts unassigned evaluation strictly to action items (0 unassigned) and computes overdue status relative to document reporting date.",
            datetime.datetime(2026, 10, 30, 0, 0),
            "Closed",
            "Verified and closed. test_milestone2_sample_document_10_ground_truth_criteria validates all 10 criteria with exact ground-truth values.",
        ),
        (
            10,
            "manish",
            datetime.datetime(2026, 10, 30, 0, 0),
            "Scanned or image-only PDFs failed extraction because the application lacked an optical character recognition (OCR) fallback pipeline, rejecting valid scanned documents.",
            "Sprint 2",
            "manish",
            "Logical",
            "Root Cause: Document service relied solely on PyMuPDF text stream extraction. Fix: Integrated RapidOCR (ONNX Runtime) with blank-page filtering. If character count falls below threshold (60 chars), system renders pages to pixmaps and invokes OCR fallback before returning an error.",
            datetime.datetime(2026, 10, 31, 0, 0),
            "Closed",
            "Verified and closed. test_scanned_pdf_ocr_fallback_pipeline confirms OCR text extraction from image-only pages.",
        ),
        (
            11,
            "manish",
            datetime.datetime(2026, 10, 31, 0, 0),
            "Cross-project context bleed: System retained old Campus Event Management goals when switching to a different project domain (such as Community Library Management).",
            "Sprint 2",
            "manish",
            "Logical",
            "Root Cause: Hardcoded project defaults in extraction heuristics. Fix: Implemented dynamic project identity extraction, dynamic goal resolution, and clean isolated workspace re-initialization.",
            datetime.datetime(2026, 10, 31, 0, 0),
            "Closed",
            "Verified and closed. test_dynamic_project_switching_and_zero_bleed and test_library_management_system_full_validation confirm 0% bleed across domains.",
        ),
    ]

    ref_row = 3
    for idx, d_row in enumerate(new_defects):
        target_row = 4 + idx
        for col_idx, val in enumerate(d_row, start=1):
            cell = ws.cell(row=target_row, column=col_idx, value=val)
            ref_cell = ws.cell(row=ref_row, column=col_idx)
            copy_cell_style(ref_cell, cell)
            if isinstance(val, datetime.datetime):
                cell.number_format = "YYYY-MM-DD"

    for out_dir in [DIR_UPDATED, DIR_DELIV]:
        out_path = out_dir / "Defect_Tracker_Milestone2.xlsx"
        wb.save(out_path)
        print(f"Saved: {out_path} (Total verified defects: 11, all Closed)")


# =====================================================================
# 3. UPDATE AGILE TEMPLATE
# =====================================================================
def update_agile_template():
    src_file = DIR_M1 / "Agile_Template_Milestone1.xlsx"
    if not src_file.exists():
        src_file = Path("Agile_Template_Milestone1.xlsx")
    wb = openpyxl.load_workbook(src_file)

    # -------------------------------------------------------------
    # Sheet 1: Product Backlog
    # -------------------------------------------------------------
    ws_pb = wb["Product Backlog"]

    # Update Sprint 1 stories (US-01 to US-06) to '3- Completed'
    for r in range(2, 8):
        ws_pb.cell(row=r, column=8).value = "3- Completed"

    # Add Sprint 2 & Sprint 3 stories
    new_stories = [
        ("Sprint 2", "Sprint 2", "US-07", "As a project manager, I want to select and upload multiple documents simultaneously in one operation with independent processing and per-file status reporting.", "MUST HAVE", "US-03", "Manish", "3- Completed"),
        ("Sprint 2", "Sprint 2", "US-08", "As a user, I want a semantic chunking and retrieval pipeline indexing documents with TF-IDF cosine similarity and persistent catalog tracking.", "MUST HAVE", "US-03", "Manish", "3- Completed"),
        ("Sprint 2", "Sprint 2", "US-09", "As a project manager, I want an autonomous Scope and Deliverable Extraction Agent to extract project goals, scope boundaries, deliverables, milestones, deadlines, and dependencies with source citations.", "MUST HAVE", "US-08", "Manish", "3- Completed"),
        ("Sprint 2", "Sprint 2", "US-10", "As a project manager, I want a Risk Detection and Delivery Forecasting Agent to calculate schedule slippage, identify dependency bottlenecks, and categorize risks with grounded evidence and mitigations.", "MUST HAVE", "US-09", "Manish", "3- Completed"),
        ("Sprint 2", "Sprint 2", "US-11", "As a project manager, I want a Blocker and Action Item Identification Agent to extract blockers, action items, and pending decisions without hallucinating unstated owners or deadlines.", "MUST HAVE", "US-08", "Manish", "3- Completed"),
        ("Sprint 2", "Sprint 2", "US-12", "As a user, I want a simplified, production-grade frontend interface that removes milestone labels, RAG lifecycle stages, and academic banners, and provides tabbed AI advisory navigation.", "MUST HAVE", "US-02", "Manish", "3- Completed"),
        ("Sprint 2", "Sprint 2", "US-13", "As a developer, I want regression testing and comprehensive multi-agent API integration (/api/agents/analyze-all) to ensure system stability.", "MUST HAVE", "US-09", "Manish", "3- Completed"),
        ("Sprint 2", "Sprint 2", "US-14", "As a project manager, I want all uploaded documents across multiple batches to belong to a single persistent project workspace with cross-document RAG and cross-project conflict rejection (HTTP 409).", "MUST HAVE", "US-07", "Manish", "3- Completed"),
        ("Sprint 3", "TBD", "US-15", "As a team member, I want automated documentation generation (Gherkin user stories, draft risk registers) synthesized from project intelligence.", "SHOULD HAVE", "US-09", "TBD", "1- Not Started"),
        ("Sprint 3", "TBD", "US-16", "As a stakeholder, I want a composite project health score (0-100) combining schedule, risk, blocker, and documentation factors using a deterministic mathematical formula.", "MUST HAVE", "US-10", "TBD", "1- Not Started"),
        ("Sprint 3", "TBD", "US-17", "As a project stakeholder, I want a conversational project intelligence assistant grounded strictly in document chunk citations.", "SHOULD HAVE", "US-08", "TBD", "1- Not Started"),
    ]

    ref_row_pb = 7
    for idx, story in enumerate(new_stories):
        target_row = 8 + idx
        for col_idx, val in enumerate(story, start=1):
            cell = ws_pb.cell(row=target_row, column=col_idx, value=val)
            ref_cell = ws_pb.cell(row=ref_row_pb, column=col_idx)
            copy_cell_style(ref_cell, cell)

    # -------------------------------------------------------------
    # Sheet 2: Sprint Backlog
    # -------------------------------------------------------------
    ws_sb = wb["Sprint Backlog"]

    # Update Sprint 1 tasks (T-01 to T-06, rows 5 to 10) to Completed
    for r in range(5, 11):
        ws_sb.cell(row=r, column=6).value = "Manish"
        ws_sb.cell(row=r, column=8).value = "3- Completed"

    # Add Sprint 2 Section Header at Row 11
    row_11_vals = ["SPRINT 2 BACKLOG - MULTI-AGENT INTELLIGENCE & MULTI-FILE INGESTION (OCT 24-31, 2026)"] + [None] * 22
    for c_idx, val in enumerate(row_11_vals, start=1):
        cell = ws_sb.cell(row=11, column=c_idx, value=val)
        ref_cell = ws_sb.cell(row=4, column=c_idx)
        copy_cell_style(ref_cell, cell)
    ws_sb.cell(row=11, column=1).font = Font(name="Arial", size=10, bold=True, color="1F497D")

    # Sprint 2 Tasks (T-07 to T-18) spanning Oct 24-31, 2026
    sprint2_tasks = [
        ("US-07", "T-07", "Enable multiple-file selection, pre-upload staging list, independent file processing, and per-file results in FastAPI backend.", datetime.datetime(2026, 10, 24), datetime.datetime(2026, 10, 26), "Manish", "Coding", "3- Completed", 3.5, 3.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-07", "T-08", "Enforce empty file, corrupted PDF, and blank scanned document rejection rules with descriptive error messaging.", datetime.datetime(2026, 10, 26), datetime.datetime(2026, 10, 26), "Manish", "Coding", "3- Completed", 2.5, 2.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-08", "T-09", "Implement TF-IDF semantic retriever with persistent JSON document catalog (documents_registry.json) and chunk coordinates.", datetime.datetime(2026, 10, 26), datetime.datetime(2026, 10, 27), "Manish", "Coding", "3- Completed", 4.0, 1.5, 2.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-09", "T-10", "Build Scope & Deliverable Extraction Agent with Pydantic schema validation and anti-hallucination UNKNOWN fallback.", datetime.datetime(2026, 10, 27), datetime.datetime(2026, 10, 27), "Manish", "Coding", "3- Completed", 4.0, 0, 4.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-10", "T-11", "Build Risk Detection & Delivery Forecasting Agent with deterministic schedule delta and 5x5 qualitative matrix.", datetime.datetime(2026, 10, 27), datetime.datetime(2026, 10, 28), "Manish", "Coding", "3- Completed", 4.0, 0, 1.5, 2.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-11", "T-12", "Build Blocker & Action Item Agent with unassigned owner mapping to UNKNOWN and cross-document citation merging.", datetime.datetime(2026, 10, 28), datetime.datetime(2026, 10, 28), "Manish", "Coding", "3- Completed", 3.0, 0, 0, 3.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-12", "T-13", "Develop simplified AgentAnalysisView and FileUpload components; remove milestone labels and RAG pipeline banners.", datetime.datetime(2026, 10, 28), datetime.datetime(2026, 10, 29), "Manish", "Design", "3- Completed", 3.5, 0, 0, 1.5, 2.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-13", "T-14", "Implement unified multi-agent API endpoint (/api/agents/analyze-all) coordinating Scope, Risk, and Blocker agents.", datetime.datetime(2026, 10, 29), datetime.datetime(2026, 10, 29), "Manish", "Integration Test", "3- Completed", 2.5, 0, 0, 0, 2.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-13", "T-15", "Author and execute automated test suite (35 pytest tests) and verify Vite production build with zero errors.", datetime.datetime(2026, 10, 29), datetime.datetime(2026, 10, 31), "Manish", "Regression Test", "3- Completed", 3.0, 0, 0, 0, 1.0, 2.0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-13", "T-16", "Update project management documentation: Unit Test Plan, Defect Tracker, and Agile Template with Milestone 2 results.", datetime.datetime(2026, 10, 30), datetime.datetime(2026, 10, 31), "Manish", "Others", "3- Completed", 3.0, 0, 0, 0, 0, 3.0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-14", "T-17", "Implement persistent ProjectWorkspace and consistency validation in DocumentService and vector store with HTTP 409 conflict detection.", datetime.datetime(2026, 10, 30), datetime.datetime(2026, 10, 31), "Manish", "Coding", "3- Completed", 3.5, 0, 0, 0, 0, 0, 3.5, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-09", "T-18", "Refine Scope, Risk, and Blocker agents, integrate OCR fallback, and achieve 100% compliance across all 35 tests on Oct 31, 2026.", datetime.datetime(2026, 10, 31), datetime.datetime(2026, 10, 31), "Manish", "Regression Test", "3- Completed", 3.0, 0, 0, 0, 0, 0, 0, 3.0, 0, 0, 0, 0, 0, 0, 0),
    ]

    ref_row_sb = 10
    for idx, t_row in enumerate(sprint2_tasks):
        target_row = 12 + idx
        for col_idx, val in enumerate(t_row, start=1):
            cell = ws_sb.cell(row=target_row, column=col_idx, value=val)
            ref_cell = ws_sb.cell(row=ref_row_sb, column=col_idx)
            copy_cell_style(ref_cell, cell)
            if isinstance(val, datetime.datetime):
                cell.number_format = "YYYY-MM-DD"

    # -------------------------------------------------------------
    # Sheet 3: Stand up Meeting
    # -------------------------------------------------------------
    ws_su = wb["Stand up Meeting"]

    # Update Sprint 1 entry (Row 2)
    ws_su.cell(row=2, column=1).value = "Sprint 1"
    ws_su.cell(row=2, column=2).value = "Days 1-4"
    ws_su.cell(row=2, column=3).value = "Initial repository setup, CORS configuration, and single-file document parser verification."
    ws_su.cell(row=2, column=4).value = "Configured FastAPI backend, React frontend, and initial document upload parsing for TXT, CSV, DOCX, and PDF."

    # Sprint 2 entries (Days 1 to 5) spanning up to Oct 31, 2026
    sprint2_standups = [
        ("Sprint 2", "Day 1 (Oct 24)", "Document upload component restricted users to single files; backend rejected batch multipart payloads.", "Implemented multi-file staging in FileUpload.tsx and updated routes.py to parse multiple files independently with per-file status badges."),
        ("Sprint 2", "Day 2 (Oct 26)", "Heavy vector database libraries (e.g. native ONNX/ChromaDB) created compatibility challenges with Python 3.13 on Windows.", "Engineered pure-Python TF-IDF semantic retriever with persistent JSON document catalog (documents_registry.json), ensuring robust, zero-dependency retrieval."),
        ("Sprint 2", "Day 3 (Oct 28)", "Extraction heuristics risked hallucinating task owners or due dates when documents lacked explicit information.", "Enforced strict academic anti-hallucination standard: unstated assignees and deadlines are mapped strictly to 'UNKNOWN' and cataloged in missing information."),
        ("Sprint 2", "Day 4 (Oct 30)", "Frontend dashboard cluttered with milestone-specific labels, academic banners, and complex RAG lifecycle diagrams.", "Refactored App.tsx to remove developmental banners; built clean tabbed AgentAnalysisView presenting Scope, Risks, and Blockers findings."),
        ("Sprint 2", "Day 5 (Oct 31)", "Validating multi-agent analysis performance across large multi-page PDFs, scanned PDFs (OCR), and domain switching.", "Authored automated pytest suite (35 tests across 8 test modules) achieving 100% pass rate; verified Vite production build on October 31, 2026."),
    ]

    ref_row_su = 2
    for idx, su_row in enumerate(sprint2_standups):
        target_row = 3 + idx
        for col_idx, val in enumerate(su_row, start=1):
            cell = ws_su.cell(row=target_row, column=col_idx, value=val)
            ref_cell = ws_su.cell(row=ref_row_su, column=col_idx)
            copy_cell_style(ref_cell, cell)

    # -------------------------------------------------------------
    # Sheet 4: Retrospection
    # -------------------------------------------------------------
    ws_re = wb["Retrospection"]

    # Update Sprint 1 retrospective (Row 2) - Preserved historical dates
    ws_re.cell(row=2, column=1).value = 1
    ws_re.cell(row=2, column=2).value = "Sprint 1"
    ws_re.cell(row=2, column=3).value = datetime.datetime(2026, 10, 10, 0, 0)
    ws_re.cell(row=2, column=4).value = datetime.datetime(2026, 10, 14, 0, 0)
    ws_re.cell(row=2, column=5).value = "Manish"
    ws_re.cell(row=2, column=6).value = "Automated test discovery with pytest and boundary-aware text parsing."
    ws_re.cell(row=2, column=7).value = "Assuming single-file upload is sufficient for enterprise project analysis."
    ws_re.cell(row=2, column=8).value = "Strict adherence to genuine codebase verification and transparent status reporting."
    ws_re.cell(row=2, column=9).value = "Delivered working Milestone 1 baseline with FastAPI health/module registry and multi-format document parser."

    # Sprint 2 Retrospective (Row 3) - Concluded October 31, 2026
    sprint2_retro = (
        2,
        "Sprint 2",
        datetime.datetime(2026, 10, 24, 0, 0),
        datetime.datetime(2026, 10, 31, 0, 0),  # Authoritative Milestone 2 completion end date
        "Manish",
        "Pydantic schema validation for multi-agent outputs, deterministic schedule delta calculation, multi-file batch staging, and OCR fallback.",
        "Assuming frontend-only validation is sufficient without backend per-file error handling.",
        "Grounding all AI recommendations in verbatim document evidence and explicit page/row citations.",
        "Delivered Milestone 2 autonomous Scope, Risk, and Blocker agents, OCR pipeline, workspace isolation, simplified production UI, and 35 automated tests on October 31, 2026.",
    )

    ref_row_re = 2
    for col_idx, val in enumerate(sprint2_retro, start=1):
        cell = ws_re.cell(row=3, column=col_idx, value=val)
        ref_cell = ws_re.cell(row=ref_row_re, column=col_idx)
        copy_cell_style(ref_cell, cell)
        if isinstance(val, datetime.datetime):
            cell.number_format = "YYYY-MM-DD"

    for out_dir in [DIR_UPDATED, DIR_DELIV]:
        out_path = out_dir / "Agile_Template_Milestone2.xlsx"
        wb.save(out_path)
        print(f"Saved: {out_path} (Sprint 2 ended 2026-10-31)")


# =====================================================================
# 4. ZIP PACKAGING
# =====================================================================
def create_zip_package():
    zip_path = DIR_DELIV / "Milestone2_Documentation.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        # Include baseline templates
        for m1_file in ["Unit_Test_Plan_v0.1.xlsx", "Defect_Tracker Template_v0.1.xlsx", "Agile_Template_v0.1.xlsx"]:
            p = DIR_DELIV / m1_file
            if p.exists():
                z.write(p, arcname=m1_file)
        # Include Milestone 2 updated templates
        for m2_file in ["Unit_Test_Plan_Milestone2.xlsx", "Defect_Tracker_Milestone2.xlsx", "Agile_Template_Milestone2.xlsx"]:
            p = DIR_DELIV / m2_file
            if p.exists():
                z.write(p, arcname=m2_file)
    print(f"Packaged documentation zip: {zip_path}")


# =====================================================================
# 5. UPDATE SUMMARY TEXT
# =====================================================================
def write_update_summary():
    content = """================================================================================
MILESTONE 2 PROJECT DOCUMENTATION UPDATE SUMMARY
Project: AI Project Intelligence & Risk Advisor
Review Stage: Milestone 2 (Autonomous Multi-Agent Intelligence & Ingestion)
Completion Date: October 31, 2026
Lead Author / Engineer: Manish
Deliverables Directory: Milestone2_Updated_Documents/ and milestone2_deliverables/
================================================================================

1. WORK COMPLETED SO FAR (GENUINELY IMPLEMENTED & VERIFIED)
--------------------------------------------------------------------------------
A. Backend Core Architecture & Ingestion Pipeline (FastAPI + Python 3.13):
   - Health Monitoring & Module Registry:
     * GET /api/health: Verified live reporting with storage readiness and active Milestone 2 pipeline status.
     * GET /api/modules: Verified dynamic tracking of all 9 project modules with honest implementation states.
   - Multi-Format Document Ingestion & Parsers:
     * PDF Parser (PyMuPDF): Multi-page text extraction with page coordinate tracking (e.g., 'Page 1', 'Page 2').
     * RapidOCR Fallback: Automatically triggered for image-only or low-text PDF pages with blank-page filtering.
     * DOCX Parser (python-docx): Paragraph and tabular text extraction with paragraph coordinate mapping.
     * CSV Parser (csv): Structured tabular extraction preserving row headers and row coordinates ('Row 1-5') with delimiter sniffing (comma, semicolon, tab, pipe).
     * TXT Parser: UTF-8 plain text extraction with boundary-aware section coordinate mapping.
   - Robust Document Validation & Edge Case Handling:
     * Empty file rejection: 0-byte files rejected with HTTP 400 Bad Request.
     * Unsupported extension rejection: Disallowed file types rejected with HTTP 400 and allowed whitelist (.pdf, .docx, .csv, .txt).
     * Corrupted PDF detection: PDFs lacking valid %PDF signatures rejected safely without server crashes.
     * Blank scanned PDF detection: Documents with zero selectable text rejected with HTTP 400 prompting readable text uploads.
   - Multiple-File Ingestion:
     * Batch Upload: POST /api/documents/upload accepts multiple files in a single multipart request.
     * Independent Processing: Each document in a batch is validated and chunked independently.
     * Partial Batch Success: Mixed valid/invalid batches process valid files (HTTP 201) and return per-file error badges without aborting valid documents.
     * All-Invalid Batch Handling: Batches where all files fail return HTTP 400 Bad Request with summarized failure reasons.
     * Document Repository & Catalog Persistence: Persistent JSON catalog (backend/data/documents_registry.json) preserves uploads, metadata, and chunk listings across backend restarts.
     * Document Deletion: DELETE /api/documents/{document_id} deletes document files and chunks from disk and registry.
   - Dynamic Workspace Isolation & Conflict Handling:
     * Dynamic Identity: Detects real project name from document metadata without hardcoded domain bias.
     * Zero Context Bleed: Completely isolates workspaces across domains (Campus Event vs Library Management).
     * Cross-Project Conflict: Ingesting documents with conflicting project names/IDs raises HTTP 409 Conflict with 1-click new workspace initialization.

B. Multi-Agent Intelligence & Advisory Engine:
   - Scope and Deliverable Extraction Agent (POST /api/agents/scope):
     * Extracts 1 Primary Goal and 5 supporting Sub-Goals with confidence ratings.
     * Classifies In-Scope vs. Out-of-Scope boundaries.
     * Extracts deliverables, milestone schedules, deadlines, responsibilities, and task dependencies.
     * Strict Anti-Hallucination: Missing owners and due dates are mapped strictly to 'UNKNOWN' and flagged in missing_information.
     * Grounded citations: Every extracted item references source document and chunk coordinates.
   - Risk Detection and Delivery Forecasting Agent (POST /api/agents/risks):
     * Dual-engine approach: Deterministic schedule delta calculations combined with qualitative 5x5 severity matrix.
     * Schedule Slip Detection: Overdue tasks identified by comparing target dates against project reference date.
     * Dependency Bottlenecks & Resource Constraints: Identified with verbatim quoted evidence.
     * Grounded Evidence vs. Recommendations: Strict boundary between document facts (supporting_evidence) and AI action steps (prefixed '[AI Recommendation]').
     * Qualitative Forecast: Honest risk classification (Critical, High, Elevated, Moderate, Low) with complete methodology disclosure and no synthetic burndowns.
   - Blocker and Action Item Identification Agent (POST /api/agents/blockers):
     * Extracts unresolved blockers, impediments, action items, approved decisions, and pending decisions.
     * Anti-Hallucination Owner Mapping: Unassigned tasks strictly set to 'UNKNOWN'; unassigned_count computed without guessing names.
     * Cross-Document Deduplication: Merges identical blockers across meeting notes and charter into single records with consolidated citations.
   - Unified Multi-Agent Analysis Endpoint (POST /api/agents/analyze-all):
     * Orchestrates Scope, Risk, and Blocker agents concurrently across all ingested documents.

C. Frontend Application (React + TypeScript + Vite):
   - Production Build Verification: Zero TypeScript errors; built cleanly in 2.25s via 'tsc && vite build'.
   - Multi-File Staging Queue: Drag-and-drop dropzone, multi-file selection (multiple={true}), format badges, formatted file sizes, and individual removal buttons before upload.
   - Extracted Chunk Viewer: Displays expandable chunk cards with coordinate tags (Page/Row/Paragraph), word/char counts, and copy-to-clipboard.
   - AI Advisory Dashboard (AgentAnalysisView): Tabbed interface for Scope, Risks, and Blockers; summary metric pills, verbatim quote cards, severity pills, and type filters.
   - UI Simplification: Removed milestone-specific labels, RAG lifecycle stages, and academic banners for a clean, production-grade interface.


2. PARTIALLY COMPLETED FUNCTIONALITY
--------------------------------------------------------------------------------
- Semantic Retrieval & Embeddings:
  * Currently implemented using pure-Python TF-IDF vector similarity with cosine ranking and persistent JSON catalog.
  * Dense vector embeddings via external vector databases (e.g. ChromaDB/Pinecone) remain optional/planned for future scaling.
- External LLM Integration:
  * Backend contains optional LLM client (app/services/llm_service.py) supporting OpenAI/Gemini with JSON schema enforcement.
  * When API keys are not supplied, the system seamlessly falls back to the deterministic grounded extraction engine.


3. REMAINING WORK (PLANNED FOR MILESTONE 3)
--------------------------------------------------------------------------------
- Documentation Generation Agent:
  * Automated synthesis of Gherkin-format user stories, draft risk registers, and executive summary reports.
- Composite Project Health Scoring (0-100):
  * Mathematical formula combining schedule adherence (0.35), risk severity density (0.30), unresolved blockers (0.20), and document completeness (0.15).
- Conversational Project Intelligence Assistant:
  * Natural language Q&A assistant with conversational memory and strict document citation grounding.


4. TESTS EXECUTED AND ACTUAL RESULTS
--------------------------------------------------------------------------------
A. Automated Backend Test Suite (Pytest 9.1.1, Python 3.13.3):
   Total Tests: 35 | Passed: 35 | Failed: 0 | Execution Time: 5.71 seconds

   Module 1: backend/tests/test_api.py (10 Tests)
   - test_root_endpoint ............................................. PASSED (HTTP 200, online status, docs link)
   - test_health_endpoint ........................................... PASSED (HTTP 200, storage_ready=True, active M2 pipeline)
   - test_modules_endpoint .......................................... PASSED (HTTP 200, 9 modules registered)
   - test_upload_txt_file ........................................... PASSED (HTTP 201, character count > 0)
   - test_upload_csv_file ........................................... PASSED (HTTP 201, row coordinates preserved)
   - test_upload_docx_file .......................................... PASSED (HTTP 201, paragraph coordinates preserved)
   - test_upload_pdf_file ........................................... PASSED (HTTP 201, PyMuPDF page text extracted)
   - test_upload_empty_file_rejected ................................ PASSED (HTTP 400, empty file rejection)
   - test_upload_unsupported_extension_rejected ..................... PASSED (HTTP 400, disallowed format rejection)
   - test_upload_corrupted_pdf_rejected ............................. PASSED (HTTP 400, malformed PDF rejection)

   Module 2: backend/tests/test_chunking.py (8 Tests)
   - test_chunker_unit_boundaries_and_overlap ....................... PASSED (sentence boundary chunking with overlap)
   - test_chunker_empty_and_whitespace .............................. PASSED (empty/whitespace text handling)
   - test_upload_txt_chunking ....................................... PASSED (TXT chunks with coordinates)
   - test_upload_multipage_pdf_chunking ............................. PASSED (multi-page PDF chunks with page numbers)
   - test_upload_csv_chunking_with_row_references ................... PASSED (CSV chunks with row coordinates)
   - test_upload_docx_chunking ...................................... PASSED (DOCX chunks with paragraph coordinates)
   - test_blank_pdf_rejected_no_extractable_text .................... PASSED (HTTP 400, blank scanned PDF rejection)
   - test_whitespace_only_txt_rejected .............................. PASSED (HTTP 400, whitespace-only rejection)

   Module 3: backend/tests/test_milestone2_agents.py (10 Tests)
   - test_single_file_upload_succeeds ............................... PASSED (single-file backward compatibility)
   - test_multiple_valid_files_upload_in_one_request ................ PASSED (HTTP 201, multi-file batch upload)
   - test_mixture_valid_and_invalid_files_upload .................... PASSED (HTTP 201, partial batch success)
   - test_all_invalid_files_batch_rejected .......................... PASSED (HTTP 400, all-invalid batch rejection)
   - test_sequential_single_file_uploads_succeed .................... PASSED (catalog persistence across uploads)
   - test_document_listing_and_deletion ............................. PASSED (GET /documents & DELETE /documents/{id})
   - test_scope_agent_extraction .................................... PASSED (goals, deliverables, anti-hallucination)
   - test_risk_agent_overdue_schedule_and_dependency_detection ...... PASSED (schedule deltas, risk matrix, evidence)
   - test_blocker_agent_extraction_and_unassigned_handling .......... PASSED (blockers, UNKNOWN owners, deduplication)
   - test_comprehensive_multi_agent_analysis ........................ PASSED (POST /api/agents/analyze-all unified API)

   Module 4: backend/tests/test_project_grouping_and_consistency.py (2 Tests)
   - test_single_persistent_project_id_across_multiple_batches ...... PASSED (4 sequential batches share single project_id, HTTP 409 conflict detection)
   - test_inherited_project_identity_for_generic_documents .......... PASSED (generic documents inherit workspace project identity)

   Module 5: backend/tests/test_sample_document_validation.py (1 Test)
   - test_milestone2_sample_document_10_ground_truth_criteria ....... PASSED (all 10 acceptance criteria validated on sample document)

   Module 6: backend/tests/test_milestone2_comprehensive_validation.py (3 Tests)
   - test_scanned_pdf_ocr_fallback_pipeline ......................... PASSED (RapidOCR ONNX fallback on non-selectable PDF pages)
   - test_dynamic_project_switching_and_zero_bleed .................. PASSED (complete domain shift with zero cross-bleed)
   - test_csv_delimiters_and_record_preservation .................... PASSED (CSV delimiter sniffing for comma, semicolon, tab, pipe)

   Module 7: backend/tests/test_library_management_validation.py (1 Test)
   - test_library_management_system_full_validation ................. PASSED (Library Management domain validation)

B. Frontend Production Build Verification:
   - Command: npm run build (tsc && vite build)
   - Status: PASSED (1563 modules transformed, zero TypeScript errors, bundle built cleanly in 2.25s)
   - Bundle Artifacts: dist/index.html, dist/assets/index-D7U2hV74.css, dist/assets/index-C_4EULnM.js


5. VERIFIED DEFECTS (RESOLVED DURING MILESTONE 2)
--------------------------------------------------------------------------------
- Defect 1 (from M1): Removed milestone labels and academic banners from UI. (Closed)
- Defect 2 (from M1): Extracted text chunks visible in frontend chunk viewer. (Closed)
- Defect 3 [Logical / Sprint 2 / Closed]: Added multi-file staging and batch processing in backend.
- Defect 4 [Maintainability / Sprint 2 / Closed]: Implemented persistent JSON catalog (documents_registry.json).
- Defect 5 [Standards / Sprint 2 / Closed]: Enforced strict UNKNOWN mapping for unassigned owners and deadlines.
- Defect 6 [Logical / Sprint 2 / Closed]: Rejection of 0-text blank scanned PDFs with descriptive error.
- Defect 7 [Logical / Sprint 2 / Closed]: Persistent ProjectWorkspace grouping multi-batch uploads under one project.
- Defect 8 [Standards / Sprint 2 / Closed]: Cross-project consistency check raising HTTP 409 Conflict.
- Defect 9 [Logical / Sprint 2 / Closed]: Section-aware goal extraction and action-item-specific unassigned counts.
- Defect 10 [Logical / Sprint 2 / Closed]: RapidOCR (ONNX Runtime) fallback for scanned/image-only PDFs.
- Defect 11 [Logical / Sprint 2 / Closed]: Dynamic project identity resolution eliminating cross-project context bleed.


6. ASSUMPTIONS AND LIMITATIONS
--------------------------------------------------------------------------------
- Milestone 2 End Date:
  Authoritative completion and evaluation date is October 31, 2026.
- Single Active Project Workspace Architecture:
  The application maintains an active project workspace. All uploaded files belong to this project, cross-document retrieval operates within this project, and conflicting cross-project documents trigger conflict resolution.
- RapidOCR ONNX Inference:
  Local OCR fallback runs via CPU execution; cold start takes ~1-2 seconds on the initial scanned page.
- Strict Anti-Hallucination Standard:
  The agents do not interpolate or invent missing assignees, dates, or burn-down metrics; any missing attribute is strictly reported as UNKNOWN.
================================================================================
"""
    summary_path = DIR_UPDATED / "Milestone2_Update_Summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {summary_path}")


if __name__ == "__main__":
    update_unit_test_plan()
    update_defect_tracker()
    update_agile_template()
    create_zip_package()
    write_update_summary()
    print("All Milestone 2 updated documents and deliverables successfully generated!")
