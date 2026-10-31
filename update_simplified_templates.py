import os
import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

output_dir = "milestone1_deliverables"
os.makedirs(output_dir, exist_ok=True)

# Styling
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
sub_header_fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
border_thin = Side(style="thin", color="D9D9D9")
cell_border = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

# ==========================================
# 1. SIMPLIFIED AGILE TEMPLATE (3-4 DAYS SCOPE)
# ==========================================
def build_simplified_agile():
    wb = openpyxl.Workbook()
    
    # Sheet 1: Product Backlog (6 simple stories)
    ws_pb = wb.active
    ws_pb.title = "Product Backlog"
    
    pb_headers = [
        "Planned Sprint", "Actual Sprint", "US ID", 
        "User Story Description", "MOSCOW", "Dependency", 
        "Assignee", "Status"
    ]
    ws_pb.append(pb_headers)
    
    user_stories = [
        ("Sprint 1", "Sprint 1", "US-01", "Set up project repository, folder structure, and local development environments for frontend and backend.", "MUST HAVE", "none", "Manish", "In Progress"),
        ("Sprint 1", "Sprint 1", "US-02", "Design system architecture, core module boundaries, and high-level data flow between ingestion, RAG, and UI.", "MUST HAVE", "none", "Manish", "Completed"),
        ("Sprint 1", "Sprint 1", "US-03", "Define supported document formats (PDF, DOCX, CSV, TXT) and file validation constraints.", "MUST HAVE", "US-02", "Team", "In Progress"),
        ("Sprint 1", "TBD", "US-04", "Prepare the document upload workflow and basic file ingestion pipeline.", "MUST HAVE", "US-03", "Team", "Planned"),
        ("Sprint 2", "TBD", "US-05", "Plan the RAG knowledge base, chunking strategy, and ChromaDB vector store configuration.", "SHOULD HAVE", "US-04", "Team", "Planned"),
        ("Sprint 2", "TBD", "US-06", "Design initial dashboard layout wireframes and user interaction flow for project insights.", "COULD HAVE", "US-02", "Team", "Planned")
    ]
    
    for row in user_stories:
        ws_pb.append(list(row))
        
    # Sheet 2: Sprint Backlog (7 tasks, 3-4 days effort)
    ws_sb = wb.create_sheet(title="Sprint Backlog")
    ws_sb.append(["NOTES:  Task sizing should be between 0.5 to 12 hours (3-4 Days Initial Setup Sprint)"] + [""] * 22)
    
    sb_headers = [
        "US ID", "Task ID", "Task Description", "Task Start Date", 
        "Task Completion Date", "Team Member", "Activity", "Status", 
        "Original Estimate Effort (In Hours)", "Day 1", "Day 2", "Day 3", 
        "Day 4", "Day 5", "Day 6", "Day 7", "Day 8", "Day 9", "Day 10", 
        "Day 11", "Day 12", "Day 13", "Day 14"
    ]
    ws_sb.append(sb_headers)
    
    # Summary formula row
    ws_sb.append(["", "", "", "", "", "", "", "", "=SUM(I5:I11)", "=SUM(J5:J11)", "=SUM(K5:K11)", "=SUM(L5:L11)", "=SUM(M5:M11)", "=SUM(N5:N11)", "=SUM(O5:O11)", "=SUM(P5:P11)", "=SUM(Q5:Q11)", "=SUM(R5:R11)", "=SUM(S5:S11)", "=SUM(T5:T11)", "=SUM(U5:U11)", "=SUM(V5:V11)", "=SUM(W5:W11)"])
    ws_sb.append(["SPRINT 1 BACKLOG - Initial Planning & Setup (Days 1 to 4)"] + [""] * 22)
    
    tasks = [
        ("US-01", "T-01", "Repository and folder setup: inspect workspace, define backend/frontend folder structure.", "2026-10-14", "2026-10-14", "Manish", "Setup", "Completed", 2.0, 2.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-01", "T-02", "Dependency survey & configuration: audit Python, Node, and draft requirements/config files.", "2026-10-14", "2026-10-14", "Manish", "Configuration", "Completed", 2.5, 2.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-02", "T-03", "System architecture design: map data flow between ingestion, ChromaDB, and agents.", "2026-10-15", "2026-10-15", "Manish", "Design", "Completed", 4.0, 0, 4.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-03", "T-04", "Initial API route design: define basic endpoints for file upload and health check.", "2026-10-15", "2026-10-16", "Team", "Design", "In Progress", 3.5, 0, 1.5, 2.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-03", "T-05", "Document ingestion design: specify parsing requirements for PDF, DOCX, CSV, and TXT.", "2026-10-16", "2026-10-16", "Team", "Design", "In Progress", 3.0, 0, 0, 3.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-01", "T-06", "Basic testing setup: prepare initial unit test plan covering setup and basic health checks.", "2026-10-16", "2026-10-17", "Manish", "Testing", "Completed", 3.0, 0, 0, 1.0, 2.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("US-02", "T-07", "Milestone 1 documentation: compile audit report, agile backlog, and presentation materials.", "2026-10-17", "2026-10-17", "Manish", "Documentation", "Completed", 4.0, 0, 0, 0, 4.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    ]
    
    for t in tasks:
        ws_sb.append(list(t))
        
    # Sheet 3: Stand up Meeting (1 genuine entry)
    ws_su = wb.create_sheet(title="Stand up Meeting")
    ws_su.append(["Sprint ", "Day", "Impediments", "Action Taken"])
    
    su_rows = [
        ("Sprint 1", "Day 1", "Workspace lacks dedicated virtual environment and Git repository is uninitialized.", "Documented setup requirements; planned Git initialization and virtual environment configuration in initial tasks."),
        ("Sprint 1", "Day 2 (Planned)", "Reviewing initial API schema and file validation constraints.", "Planned team discussion on upload limits and supported document types."),
        ("Sprint 1", "Day 3 (Planned)", "Finalizing document parser specifications.", "Reviewing PyMuPDF vs pypdf for PDF coordinate preservation."),
        ("Sprint 1", "Day 4 (Planned)", "Milestone 1 review preparation.", "Verifying presentation slides and simplified project management spreadsheets.")
    ]
    for r in su_rows:
        ws_su.append(list(r))
        
    # Sheet 4: Retrospection (Minimal / Pending)
    ws_re = wb.create_sheet(title="Retrospection")
    ws_re.append(["SL #", "Sprint #", "Sprint start date", "Sprint end date", "Team member name ", "Start Doing", "Stop Doing ", "Continue Doing ", "Action taken"])
    
    re_rows = [
        (1, 1, "2026-10-14", "2026-10-17", "Manish", "Initial Sprint Retrospective - Pending (Sprint in progress)", "", "", "To be completed upon conclusion of initial setup sprint"),
        (2, "", "", "", "", "", "", "", ""),
        (3, "", "", "", "", "", "", "")
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
                
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if "\n" in val_str:
                    val_str = max(val_str.split("\n"), key=len)
                if len(val_str) > max_len:
                    max_len = len(val_str)
            sheet.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 55)
            
    ws_sb["A1"].font = Font(name="Calibri", size=10, italic=True, bold=True, color="C00000")
    ws_sb["A1"].fill = PatternFill(fill_type=None)
    ws_sb["A4"].font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    ws_sb["A4"].fill = sub_header_fill
    
    agile_path = os.path.join(output_dir, "Agile_Template_Milestone1.xlsx")
    wb.save(agile_path)
    print(f"Saved simplified Agile Template: {agile_path}")

# ==========================================
# 2. SIMPLIFIED DEFECT TRACKER (LIGHTWEIGHT)
# ==========================================
def build_simplified_defect_tracker():
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
    
    # Exactly 1 real, verified setup defect observed during initial repository audit
    defects = [
        (1, "Manish", datetime.datetime(2026, 10, 14), "Workspace repository is not yet initialized in Git and lacks dedicated virtual environment.", "Sprint 1", "Manish", "Maintainability", "Documented in MILESTONE1_REPOSITORY_AUDIT.md; scheduled Git initialization and virtual environment creation in initial setup tasks.", datetime.datetime(2026, 10, 14), "Open", "Identified during initial project setup.")
    ]
    
    for d in defects:
        ws_def.append(list(d))
        
    # Clean, empty formatted rows ready for future QA logging
    for i in range(2, 16):
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
            sheet.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)
            
    defect_path = os.path.join(output_dir, "Defect_Tracker_Milestone1.xlsx")
    wb.save(defect_path)
    print(f"Saved simplified Defect Tracker: {defect_path}")

# ==========================================
# 3. SIMPLIFIED UNIT TEST PLAN (7 RELEVANT TESTS)
# ==========================================
def build_simplified_unit_test_plan():
    wb = openpyxl.Workbook()
    ws_ut = wb.active
    ws_ut.title = "UT"
    
    headers = [
        "Sl: No:", "Test Case Name", "Test Procedure", 
        "Condition to be tested", "Expected Result", 
        "Actual Result", "Test Status"
    ]
    ws_ut.append(headers)
    
    test_cases = [
        (1, "TC-01: Frontend Development Server Startup", 
         "Run 'npm run dev' from the frontend project directory once initialized.", 
         "Node.js installed, frontend dependencies installed via npm.", 
         "Vite development server starts successfully and listens on http://localhost:5173.", 
         "Not executed (Frontend initialization scheduled in Sprint 1)", "Not Run"),
        
        (2, "TC-02: FastAPI Backend Server Startup", 
         "Run 'uvicorn main:app --port 8000' from the backend project directory.", 
         "Python 3.13 and FastAPI installed in virtual environment.", 
         "Uvicorn boots ASGI application and listens on http://127.0.0.1:8000.", 
         "Not executed (Backend main.py entrypoint scheduled in Sprint 1)", "Not Run"),
         
        (3, "TC-03: Backend Health Endpoint Response", 
         "Send HTTP GET request to 'http://127.0.0.1:8000/health'.", 
         "FastAPI server is running.", 
         "HTTP 200 OK returned with JSON response {'status': 'ok'}.", 
         "Not executed (Endpoint implementation scheduled in Sprint 1)", "Not Run"),
         
        (4, "TC-04: Supported Document Format Identification", 
         "Pass file names with extensions .pdf, .docx, .csv, and .txt to file validator.", 
         "Uploaded document has an allowed file extension.", 
         "Validation function identifies file format correctly and permits upload.", 
         "Not executed (Validation service scheduled in Sprint 1)", "Not Run"),
         
        (5, "TC-05: Invalid Document Format Rejection", 
         "Attempt upload of disallowed file types (e.g. .exe, .zip, .png).", 
         "Uploaded file extension is outside allowed whitelist.", 
         "Validation function rejects file and returns descriptive error message (HTTP 415).", 
         "Not executed (Validation service scheduled in Sprint 1)", "Not Run"),
         
        (6, "TC-06: ChromaDB Vector Store Connection", 
         "Initialize ChromaDB persistent client in local data directory.", 
         "ChromaDB library installed in virtual environment.", 
         "Chroma client initializes without error and creates or connects to collection.", 
         "Not executed (ChromaDB setup scheduled in Sprint 2)", "Not Run"),
         
        (7, "TC-07: Automated Test Runner Discovery", 
         "Execute 'python -m pytest' in repository root to discover automated tests.", 
         "Pytest installed, tests/ directory created.", 
         "Pytest discovers test files and executes unit test assertions.", 
         "Not executed (Test suite creation scheduled in Sprint 1)", "Not Run")
    ]
    
    for tc in test_cases:
        ws_ut.append(list(tc))
        
    # Apply styling
    for cell in ws_ut[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
    for row in ws_ut.iter_rows(min_row=2):
        for cell in row:
            cell.border = cell_border
            cell.alignment = Alignment(vertical="center")
            
        status_cell = row[6]
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
        ws_ut.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 48)
        
    ut_path = os.path.join(output_dir, "Unit_Test_Plan_Milestone1.xlsx")
    wb.save(ut_path)
    print(f"Saved simplified Unit Test Plan: {ut_path}")

if __name__ == "__main__":
    build_simplified_agile()
    build_simplified_defect_tracker()
    build_simplified_unit_test_plan()
    print("All 3 simplified templates successfully built!")
