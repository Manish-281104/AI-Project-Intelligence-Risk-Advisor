import os
import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

output_dir = "milestone1_deliverables"
os.makedirs(output_dir, exist_ok=True)

# Common styling helpers
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
sub_header_fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
alt_row_fill = PatternFill(start_color="F2F5F9", end_color="F2F5F9", fill_type="solid")
border_thin = Side(style="thin", color="D9D9D9")
cell_border = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

# ==========================================
# 1. AGILE TEMPLATE
# ==========================================
def build_agile_template():
    wb = openpyxl.Workbook()
    # Sheet 1: Product Backlog
    ws_pb = wb.active
    ws_pb.title = "Product Backlog"
    
    pb_headers = [
        "Planned Sprint", "Actual Sprint", "US ID", 
        "User Story Description", "MOSCOW", "Dependency", 
        "Assignee", "Status"
    ]
    ws_pb.append(pb_headers)
    
    user_stories = [
        ("Sprint 1", "Sprint 1", "US-12", "As a project team, we want to establish the Milestone 1 system architecture, repository audit, agile sprint backlog, defect tracking register, and comprehensive unit test plan so that engineering governance is verified before coding begins.", "MUST HAVE", "none", "Team", "3- Completed"),
        ("Sprint 1", "TBD", "US-01", "As a project manager, I want to upload project documents in PDF, DOCX, CSV, and TXT formats so that the system extracts clean text while preserving document structural metadata (page numbers, table rows, timestamps).", "MUST HAVE", "none", "TBD", "1- New"),
        ("Sprint 1", "TBD", "US-02", "As a system administrator, I want uploaded files to be validated for format integrity, size limits, and corruption errors so that invalid or malicious documents are safely rejected.", "MUST HAVE", "US-01", "TBD", "1- New"),
        ("Sprint 1", "TBD", "US-03", "As a RAG pipeline engineer, I want extracted document text to be chunked recursively with configurable chunk size and overlap so that semantic context and metadata attributes are preserved.", "MUST HAVE", "US-01", "TBD", "1- New"),
        ("Sprint 1", "TBD", "US-04", "As a RAG pipeline engineer, I want text chunks to be embedded and indexed into ChromaDB with strict project-id metadata filters so that semantic retrieval is fast and isolated between projects.", "MUST HAVE", "US-03", "TBD", "1- New"),
        ("Sprint 2", "TBD", "US-05", "As a project manager, I want an AI agent to extract high-level scope, objectives, deliverables, and milestone schedules from uploaded documents with source page citations.", "MUST HAVE", "US-04", "TBD", "1- New"),
        ("Sprint 2", "TBD", "US-06", "As a risk officer, I want a dual-engine risk detection agent to calculate schedule slips deterministically and identify qualitative risks using an LLM with a 5x5 severity matrix.", "MUST HAVE", "US-05", "TBD", "1- New"),
        ("Sprint 2", "TBD", "US-07", "As a scrum master, I want an AI agent to identify blockers, decisions, and action items from meeting notes, mapping missing assignees/deadlines to 'UNKNOWN' rather than hallucinating.", "SHOULD HAVE", "US-04", "TBD", "1- New"),
        ("Sprint 3", "TBD", "US-08", "As a product owner, I want an automated documentation agent to synthesize user stories, risk registers, and status briefings with mandatory draft disclaimers and source citations.", "SHOULD HAVE", "US-05, US-06", "TBD", "1- New"),
        ("Sprint 3", "TBD", "US-09", "As an executive stakeholder, I want a transparent project health score (0-100) calculated mathematically from schedule adherence, risk severity, blocker volume, and documentation completeness.", "MUST HAVE", "US-06, US-07", "TBD", "1- New"),
        ("Sprint 3", "TBD", "US-10", "As a team member, I want a conversational project assistant grounded strictly in uploaded documents that cites source chunks and explicitly declines to answer when evidence is lacking.", "MUST HAVE", "US-04", "TBD", "1- New"),
        ("Sprint 4", "TBD", "US-11", "As a stakeholder, I want an interactive React dashboard showing Project Health, Risk Heatmap, Deliverables Gantt, Blocker list, and Conversational Chat drawer with error/loading states.", "MUST HAVE", "US-09, US-10", "TBD", "1- New")
    ]
    
    for row in user_stories:
        ws_pb.append(list(row))
        
    # Sheet 2: Sprint Backlog
    ws_sb = wb.create_sheet(title="Sprint Backlog")
    ws_sb.append(["NOTES:  Task sizing should be between 0.5 to 12 hours"] + [""] * 22)
    
    sb_headers = [
        "US ID", "Task ID", "Task Description", "Task Start Date", 
        "Task Completion Date", "Team Member", "Activity", "Status", 
        "Original Estimate Effort (In Hours)", "Day 1", "Day 2", "Day 3", 
        "Day 4", "Day 5", "Day 6", "Day 7", "Day 8", "Day 9", "Day 10", 
        "Day 11", "Day 12", "Day 13", "Day 14"
    ]
    ws_sb.append(sb_headers)
    
    # Summary Row
    ws_sb.append(["", "", "", "", "", "", "", "", "=SUM(I5:I18)", "=SUM(J5:J18)", "=SUM(K5:K18)", "=SUM(L5:L18)", "=SUM(M5:M18)", "=SUM(N5:N18)", "=SUM(O5:O18)", "=SUM(P5:P18)", "=SUM(Q5:Q18)", "=SUM(R5:R18)", "=SUM(S5:S18)", "=SUM(T5:T18)", "=SUM(U5:U18)", "=SUM(V5:V18)", "=SUM(W5:W18)"])
    ws_sb.append(["SPRINT 1 BACKLOG - Foundation & Ingestion Scaffolding"] + [""] * 22)
    
    tasks = [
        ("US-12", "T-01", "Inspect existing repository, execute audit commands, generate MILESTONE1_REPOSITORY_AUDIT.md", "2026-10-14", "2026-10-14", "Manish", "Analysis", "3- Completed", 4.0, 4.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-12", "T-02", "Audit host environment, verify Python, Node, Pytest, Uvicorn, and record gaps in test report", "2026-10-14", "2026-10-14", "Manish", "Verification", "3- Completed", 3.0, 0, 3.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-12", "T-03", "Populate Agile Backlog, Defect Tracker, and Unit Test Plan workbooks for AI Risk Advisor", "2026-10-14", "2026-10-14", "Manish", "Planning", "3- Completed", 6.0, 0, 0, 6.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-12", "T-04", "Develop Milestone 1 presentation slides and faculty demonstration script", "2026-10-14", "2026-10-14", "Manish", "Documentation", "3- Completed", 5.0, 0, 0, 0, 5.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-01", "T-05", "Initialize Git repository, configure .gitignore for Python/Node, setup virtual environment", "2026-10-15", "2026-10-15", "TBD", "Development", "1- New", 2.0, 0, 0, 0, 0, 2.0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-01", "T-06", "Scaffold FastAPI backend modular directory structure (api, core, services, schemas)", "2026-10-16", "2026-10-16", "TBD", "Architecture", "1- New", 4.0, 0, 0, 0, 0, 0, 4.0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-01", "T-07", "Implement PDF text parser using PyMuPDF (fitz) with per-page tracking and metadata extraction", "2026-10-17", "2026-10-18", "TBD", "Development", "1- New", 6.0, 0, 0, 0, 0, 0, 0, 3.0, 3.0, 0, 0, 0, 0, 0, 0),
        ("US-01", "T-08", "Implement DOCX document parser using python-docx for paragraphs, tables, and headings", "2026-10-19", "2026-10-19", "TBD", "Development", "1- New", 5.0, 0, 0, 0, 0, 0, 0, 0, 0, 5.0, 0, 0, 0, 0, 0),
        ("US-01", "T-09", "Implement CSV and TXT document parser using pandas and UTF-8 stream readers", "2026-10-20", "2026-10-20", "TBD", "Development", "1- New", 4.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4.0, 0, 0, 0, 0),
        ("US-02", "T-10", "Implement file upload validation service (MIME types, size limits, corrupted file detection)", "2026-10-21", "2026-10-21", "TBD", "Development", "1- New", 4.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4.0, 0, 0, 0),
        ("US-03", "T-11", "Implement recursive text chunking service with configurable chunk size (800) and overlap (150)", "2026-10-22", "2026-10-22", "TBD", "Development", "1- New", 5.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5.0, 0, 0),
        ("US-04", "T-12", "Setup ChromaDB persistent client and initialize collections with metadata schemas", "2026-10-23", "2026-10-23", "TBD", "Development", "1- New", 6.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6.0, 0),
        ("US-04", "T-13", "Implement embedding generation pipeline and project-isolated semantic similarity retriever", "2026-10-24", "2026-10-25", "TBD", "Development", "1- New", 8.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4.0, 4.0),
        ("US-01..04", "T-14", "Execute Sprint 1 integration test suite across document parsers and ChromaDB indexing", "2026-10-26", "2026-10-26", "TBD", "Unit Test", "1- New", 6.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6.0)
    ]
    
    for t in tasks:
        ws_sb.append(list(t))
        
    # Sheet 3: Stand up Meeting
    ws_su = wb.create_sheet(title="Stand up Meeting")
    ws_su.append(["Sprint ", "Day", "Impediments", "Action Taken"])
    
    su_rows = [
        ("Sprint 1", "Day 1", "Workspace contained no application source code, only legacy template spreadsheets.", "Executed comprehensive repository audit; documented baseline in MILESTONE1_REPOSITORY_AUDIT.md."),
        ("Sprint 1", "Day 2", "Host environment lacks core target dependencies (chromadb, langgraph, python-docx).", "Recorded dependencies in test report; structured isolated virtual environment and requirements.txt plan."),
        ("Sprint 1", "Day 3", "Uploaded templates contained legacy data from an unrelated student project.", "Cleaned and customized Agile Backlog, Defect Tracker, and Unit Test Plan for AI Risk Advisor."),
        ("Sprint 1", "Day 4", "Git version control was uninitialized in the repository directory.", "Created task T-05 to initialize git, setup .gitignore, and establish initial commit."),
        ("Sprint 1", "Day 5 (Planned)", "Selecting robust PDF parsing library that captures page coordinates.", "Evaluated PyMuPDF (fitz) vs pypdf; scheduled PyMuPDF for implementation in T-07.")
    ]
    for r in su_rows:
        ws_su.append(list(r))
        
    # Sheet 4: Retrospection
    ws_re = wb.create_sheet(title="Retrospection")
    ws_re.append(["SL #", "Sprint #", "Sprint start date", "Sprint end date", "Team member name ", "Start Doing", "Stop Doing ", "Continue Doing ", "Action taken"])
    
    re_rows = [
        (1, 1, "2026-10-14", "2026-10-26", "Manish", "Verifying all dependencies and file structures with automated commands before declaring status", "Assuming code exists based solely on project proposals or requirement descriptions", "Maintaining strict evidence-based auditing and modular task estimation (0.5 to 12 hours)", "Established Milestone 1 verification baseline, customized PM templates, and defined Milestone 2 build plan"),
        (2, 2, "2026-10-27", "2026-11-09", "Team", "To be updated upon Sprint 2 completion", "To be updated upon Sprint 2 completion", "To be updated upon Sprint 2 completion", "Sprint 2 planning scheduled"),
        (3, 3, "2026-11-10", "2026-11-23", "Team", "To be updated upon Sprint 3 completion", "To be updated upon Sprint 3 completion", "To be updated upon Sprint 3 completion", "Sprint 3 planning scheduled")
    ]
    for r in re_rows:
        ws_re.append(list(r))
        
    # Apply styling
    for sheet in wb.worksheets:
        for cell in sheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.border = cell_border
                cell.alignment = Alignment(vertical="center")
                
        # Column auto-width adjustment
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if "\n" in val_str:
                    val_str = max(val_str.split("\n"), key=len)
                if len(val_str) > max_len:
                    max_len = len(val_str)
            sheet.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 60)
            
    # Custom format for Sprint Backlog Row 2 & 4
    ws_sb["A1"].font = Font(name="Calibri", size=10, italic=True, bold=True, color="C00000")
    ws_sb["A1"].fill = PatternFill(fill_type=None)
    ws_sb["A4"].font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    ws_sb["A4"].fill = sub_header_fill
    
    agile_path = os.path.join(output_dir, "Agile_Template_Milestone1.xlsx")
    wb.save(agile_path)
    print(f"Saved: {agile_path}")

# ==========================================
# 2. DEFECT TRACKER TEMPLATE
# ==========================================
def build_defect_tracker():
    wb = openpyxl.Workbook()
    
    # Sheet 1: Defects
    ws_def = wb.active
    ws_def.title = "Defects"
    
    headers = [
        "Sl No", "Submitted By", "Submitted Date", "Description", 
        "Detected Sprint", "Assigned To", "Type Of Defect", "Action Taken", 
        "Action Taken Date", "Status(Open/Closed)", "Remarks"
    ]
    ws_def.append(headers)
    
    # Only real, verified defects discovered during code inspection and testing
    defects = [
        (1, "Manish (Audit)", datetime.datetime(2026, 10, 14), "Workspace repository is uninitialized in Git (git status returned fatal: not a git repository).", "Sprint 1", "Manish", "Maintainability", "Documented in MILESTONE1_REPOSITORY_AUDIT.md; created task T-05 in Sprint 1 to run git init and configure .gitignore.", datetime.datetime(2026, 10, 14), "Open", "Discovered during Milestone 1 physical repository audit."),
        (2, "Manish (Audit)", datetime.datetime(2026, 10, 14), "FastAPI web server fails startup: uvicorn main:app returned 'Could not import module main'.", "Sprint 1", "TBD", "Logical", "Logged in MILESTONE1_TEST_REPORT.md; scheduled backend project structure scaffolding in task T-06.", datetime.datetime(2026, 10, 14), "Open", "Entrypoint main.py is not yet implemented."),
        (3, "Manish (Audit)", datetime.datetime(2026, 10, 14), "Automated test suite (pytest) exits with code 1 due to zero collected test items.", "Sprint 1", "TBD", "Standards", "Created comprehensive unit test plan with 28 test cases; scheduled tests/ directory creation in Sprint 1.", datetime.datetime(2026, 10, 14), "Open", "Verification documented in MILESTONE1_TEST_REPORT.md."),
        (4, "Manish (Audit)", datetime.datetime(2026, 10, 14), "Host environment lacks core target AI packages: chromadb, langgraph, and python-docx are missing.", "Sprint 1", "TBD", "Maintainability", "Documented blocking dependencies in test report; drafted requirements.txt for isolated virtual environment installation.", datetime.datetime(2026, 10, 14), "Open", "Blocking RAG and agent orchestration until installed.")
    ]
    
    for d in defects:
        ws_def.append(list(d))
        
    # Add empty rows for incoming QA logging
    for i in range(5, 21):
        ws_def.append([i, "", None, "", "", "", "", "", None, "", ""])
        
    # Sheet 2: Defect Categories (Preserved from original template)
    ws_s2 = wb.create_sheet(title="Sheet2")
    categories = ["Logical", "User Interface", "Maintainability", "Standards", "Others"]
    for cat in categories:
        ws_s2.append([cat])
        
    # Apply styling
    for sheet in wb.worksheets:
        for cell in sheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.border = cell_border
                cell.alignment = Alignment(vertical="center")
                if isinstance(cell.value, datetime.datetime):
                    cell.number_format = "YYYY-MM-DD"
                    
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if "\n" in val_str:
                    val_str = max(val_str.split("\n"), key=len)
                if len(val_str) > max_len:
                    max_len = len(val_str)
            sheet.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 50)
            
    defect_path = os.path.join(output_dir, "Defect_Tracker_Milestone1.xlsx")
    wb.save(defect_path)
    print(f"Saved: {defect_path}")

# ==========================================
# 3. UNIT TEST PLAN TEMPLATE
# ==========================================
def build_unit_test_plan():
    wb = openpyxl.Workbook()
    ws_ut = wb.active
    ws_ut.title = "UT"
    
    # Preserving original columns and adding Test Status for explicit governance
    headers = [
        "Sl: No:", "Test Case Name", "Test Procedure", 
        "Condition to be tested", "Expected Result", 
        "Actual Result", "Test Status"
    ]
    ws_ut.append(headers)
    
    test_cases = [
        # Module 1: Ingestion
        (1, "UT-ING-01: PDF Document Text Extraction", 
         "Upload valid multi-page PDF project charter (sample_charter.pdf) to ingestion endpoint.", 
         "File is a standard text PDF with 5 pages and sectional headings.", 
         "Text extracted cleanly for all 5 pages; page numbers 1-5 preserved in chunk metadata.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
        
        (2, "UT-ING-02: DOCX Table and Paragraph Parsing", 
         "Upload DOCX meeting minutes containing embedded risk tables to ingestion service.", 
         "File contains both paragraph text and structured 4-column tables.", 
         "Tables converted into serialized text format with row and column preservation; paragraph order intact.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        (3, "UT-ING-03: CSV Sprint Data Parsing", 
         "Upload CSV sprint backlog (sprint_tasks.csv) with task IDs, estimates, and assignees.", 
         "Standard comma-separated text file with header row and 50 task rows.", 
         "All 50 rows ingested; column mappings preserved in metadata dictionary.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        (4, "UT-ING-04: TXT Raw File Ingestion", 
         "Upload plain text notes (notes.txt) with UTF-8 encoding.", 
         "Plain text file with newline line breaks.", 
         "Text parsed without character encoding corruption; line index preserved.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        (5, "UT-ING-05: Unsupported File Extension Validation", 
         "Attempt upload of executable file (.exe) or archive (.zip).", 
         "User submits file outside whitelist (PDF, DOCX, CSV, TXT).", 
         "HTTP 415 Unsupported Media Type returned with descriptive error message; file rejected.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        (6, "UT-ING-06: Corrupted and Password-Protected File Handling", 
         "Upload a password-protected PDF and a truncated/corrupted DOCX file.", 
         "File cannot be decrypted or parsed by PyMuPDF/python-docx.", 
         "Graceful error caught; HTTP 422 returned with clear diagnostic; system remains stable.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        # Module 2: RAG Pipeline
        (7, "UT-RAG-01: Recursive Chunking with Overlap", 
         "Pass 5,000-character project specification text through recursive character splitter.", 
         "Chunk size = 800 characters, overlap = 150 characters.", 
         "Text split into ~7-8 overlapping chunks; chunk indices and parent document ID preserved.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        (8, "UT-RAG-02: ChromaDB Indexing and Vector Storage", 
         "Generate embeddings for chunk list and store in ChromaDB collection.", 
         "ChromaDB local persistence directory initialized; collection schema verified.", 
         "All chunks embedded; vectors and metadata dictionaries stored in ChromaDB without loss.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        (9, "UT-RAG-03: Semantic Similarity Retrieval with Citations", 
         "Query ChromaDB with semantic prompt: 'What are the hardware deliverables for Sprint 2?'.", 
         "Collection contains matching chunks from project charter.", 
         "Top-k chunks returned with cosine similarity score > 0.70; source file and page returned.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        (10, "UT-RAG-04: Multi-Tenant Project Isolation Filter", 
         "Query project A with query matching document text existing only in project B.", 
         "Two distinct projects (Project_01 and Project_02) indexed in ChromaDB.", 
         "Zero chunks from Project_02 returned when querying with filter where={'project_id': 'Project_01'}.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        # Module 3: Scope Extraction
        (11, "UT-SCP-01: Deliverable and Milestone Extraction", 
         "Run Scope Extraction Agent against ingested SOW document.", 
         "Document contains explicit milestone schedule and deliverable lists.", 
         "Structured JSON produced matching Pydantic schema with deliverable names, milestones, and target dates.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        (12, "UT-SCP-02: Scope Claim Source Traceability", 
         "Verify every extracted deliverable in UT-SCP-01 has a corresponding source citation.", 
         "Deliverables extracted from document text.", 
         "Every deliverable item references valid document ID, page number, and original sentence span.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        # Module 4: Risk Detection
        (13, "UT-RSK-01: Deterministic Schedule Slip Detection", 
         "Run risk agent against task list where target date (2026-10-10) is prior to current date (2026-10-14).", 
         "Task status is 'In Progress' with target date in the past.", 
         "Deterministic engine flags task as 'OVERDUE' with negative float calculated (-4 days).", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        (14, "UT-RSK-02: 5x5 Qualitative Risk Severity Matrix", 
         "Pass identified technical dependency risk with Likelihood=4 and Impact=4 to risk calculator.", 
         "Calculated risk exposure = Likelihood * Impact.", 
         "Risk score = 16; categorized as 'HIGH RISK' according to standard severity bands.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        # Module 5: Blockers & Action Items
        (15, "UT-BLK-01: Blocker Extraction with Unknown Handling", 
         "Parse meeting notes stating: 'API authentication is blocked pending firewall access approval.'", 
         "Meeting notes mention blocker but omit assignee and target resolution date.", 
         "Blocker extracted; owner assigned as 'UNKNOWN'; due date assigned as 'UNKNOWN'; no hallucination.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        # Module 6: Documentation Generation
        (16, "UT-DOC-01: Automated User Story and Risk Register Synthesis", 
         "Trigger Documentation Generation Agent for Sprint 1 deliverables.", 
         "Structured deliverables and risks available in project state.", 
         "Markdown document generated containing user stories with acceptance criteria and tabular risk register.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        (17, "UT-DOC-02: Mandatory AI Draft Disclaimer and Provenance", 
         "Inspect generated documentation artifact header and footnotes.", 
         "Artifact synthesized by LLM agent.", 
         "Header contains: 'DRAFT - Generated by AI Project Intelligence'; all claims mapped to chunk citations.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        # Module 7: Project Health Scoring
        (18, "UT-HLT-01: Mathematical Health Score Formula Reproducibility", 
         "Calculate health score for project with: 2 overdue tasks (penalty=10), 1 critical risk (penalty=15).", 
         "Formula: Health = 100 - (0.35*SchedulePenalty + 0.30*RiskPenalty + 0.20*BlockerPenalty + 0.15*MissingDataPenalty).", 
         "Score calculated deterministically to exactly 92.0 / 100; verified identical across repeated runs.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        (19, "UT-HLT-02: Conservative Missing Data Penalty Handling", 
         "Calculate health score when project charter is uploaded but risk register is completely missing.", 
         "Sparse documentation state.", 
         "System applies 15-point missing documentation penalty; does not default unrecorded risk to 100% healthy.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        # Module 8: Conversational Assistant
        (20, "UT-CHT-01: Grounded Conversational Q&A with Citations", 
         "Submit user question: 'What is the budget for the cloud infrastructure in Milestone 2?'.", 
         "Document contains budget breakdown on Page 12 of financial proposal.", 
         "Assistant provides accurate dollar amount and appends citation '[Page 12, Financial_Proposal.pdf]'.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        (21, "UT-CHT-02: Grounded Fallback on Insufficient Evidence", 
         "Submit out-of-domain question: 'What is the CEO salary of our cloud vendor?'.", 
         "No relevant chunks in project knowledge base (retrieval similarity < threshold).", 
         "Assistant responds: 'I cannot find evidence regarding this in the uploaded project documents.' No hallucination.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        # Module 9: Dashboard Integration
        (22, "UT-DSH-01: React Health KPI Dial and Risk Matrix Rendering", 
         "Load Dashboard overview view with mock API payload containing health score and risk items.", 
         "API returns valid JSON schema for project KPIs.", 
         "Health score dial renders with proper color tier (Green/Yellow/Red); risk items plotted on 5x5 grid.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        (23, "UT-DSH-02: File Upload Progress and Error Boundary Display", 
         "Simulate failed file upload due to network error in React Document Hub.", 
         "Backend returns 500 or network drops during upload.", 
         "Error alert displayed cleanly with retry button; UI does not crash or display blank screen.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        # Security & Infrastructure
        (24, "UT-SEC-01: Unauthorized Project Cross-Access Prevention", 
         "Client authenticated to Project A attempts GET request for /api/v1/project/Project_B/health.", 
         "User lacks authorization token for Project B.", 
         "HTTP 403 Forbidden returned; zero project data exposed.", 
         "Not executed (Implementation scheduled for Milestone 2)", "Not Run"),
         
        # Milestone 1 Physical Verification Tests (Actually Executed)
        (25, "UT-M1-01: Automated Pytest Discovery Verification", 
         "Execute python -m pytest in repository root to detect existing test suites.", 
         "Root directory inspected for tests/ folder and test_*.py files.", 
         "Pytest executed successfully and reports test session outcome.", 
         "Executed: Pytest collected 0 items and returned exit code 1 (no test files present on disk).", "Failed"),
         
        (26, "UT-M1-02: Backend ASGI Server Boot Verification", 
         "Execute python -m uvicorn main:app in repository root to test API startup.", 
         "Repository inspected for FastAPI entrypoint main.py.", 
         "Uvicorn boots ASGI server on designated port.", 
         "Executed: Uvicorn returned exit code 1 with error: 'Could not import module main'.", "Failed"),
         
        (27, "UT-M1-03: Frontend Script Execution Verification", 
         "Execute npm test in repository root to test frontend test configuration.", 
         "Repository inspected for package.json.", 
         "npm test executes test script defined in package.json.", 
         "Executed: npm test returned exit code 1 (no package.json found in workspace).", "Failed"),
         
        (28, "UT-M1-04: Project Management Template Format Integrity", 
         "Programmatically parse uploaded Excel workbooks using openpyxl and xlrd.", 
         "Three workbooks (.xls and .xlsx) inspected for sheet integrity and cell readability.", 
         "All workbooks parsed successfully without corruption; sheets and rows readable.", 
         "Executed: All 3 workbooks loaded and verified readable; structure mapped successfully.", "Passed")
    ]
    
    for tc in test_cases:
        ws_ut.append(list(tc))
        
    # Apply styling
    for cell in ws_ut[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
    for row in ws_ut.iter_rows(min_row=2):
        status_val = row[6].value
        for cell in row:
            cell.border = cell_border
            cell.alignment = Alignment(vertical="center")
            
        # Highlight status column
        status_cell = row[6]
        if status_val == "Passed":
            status_cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
            status_cell.font = Font(name="Calibri", size=11, bold=True, color="006100")
        elif status_val == "Failed":
            status_cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
            status_cell.font = Font(name="Calibri", size=11, bold=True, color="9C0006")
        elif status_val == "Not Run":
            status_cell.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
            status_cell.font = Font(name="Calibri", size=11, bold=True, color="9C6500")
            
    for col in ws_ut.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if "\n" in val_str:
                val_str = max(val_str.split("\n"), key=len)
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws_ut.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)
        
    ut_path = os.path.join(output_dir, "Unit_Test_Plan_Milestone1.xlsx")
    wb.save(ut_path)
    print(f"Saved: {ut_path}")

if __name__ == "__main__":
    build_agile_template()
    build_defect_tracker()
    build_unit_test_plan()
    print("All 3 templates successfully generated!")
