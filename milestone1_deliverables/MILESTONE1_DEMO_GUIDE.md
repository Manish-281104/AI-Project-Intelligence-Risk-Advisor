# Milestone 1 Faculty Demonstration & Review Guide: AI Project Intelligence & Risk Advisor

**Project Title:** AI Project Intelligence & Risk Advisor  
**Review Type:** University Milestone 1 Evaluation  
**Auditor / Presenter:** Manish  
**Repository Directory:** `C:\Users\manis\Desktop\SP`  
**Deliverables Directory:** `C:\Users\manis\Desktop\SP\milestone1_deliverables\`

---

## 1. How to Start the Frontend and Backend

### Current State Notice
Because the codebase is currently at the **System Architecture, Repository Audit, and Quality Assurance Foundation** stage (Milestone 1), application servers are not yet executing. Attempting to start the backend or frontend in the root directory will yield the following verified behavior:
- Backend: `python -m uvicorn main:app` -> Exits with code 1 (`Could not import module main`).
- Frontend: `npm test` -> Exits with code 1 (`Error: no test specified / no package.json in workspace`).

### Target Milestone 2 Startup Commands (Post-Scaffolding)

#### Backend Service (FastAPI)
```powershell
# From C:\Users\manis\Desktop\SP
# 1. Activate isolated Python virtual environment
.\venv\Scripts\Activate.ps1

# 2. Run backend development server
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend Application (React + Vite)
```powershell
# In a separate terminal from C:\Users\manis\Desktop\SP\frontend
# 1. Install dependencies
npm install

# 2. Launch Vite development server
npm run dev
# Application will be accessible at http://localhost:5173
```

---

## 2. Required Environment Variables

When running the application in Milestone 2, create a `.env` file in `C:\Users\manis\Desktop\SP\backend\.env`:

```ini
# ===================================================================
# AI Project Intelligence & Risk Advisor - Configuration Schema
# ===================================================================

# Environment Mode
ENVIRONMENT=development
DEBUG=True

# API Server Configuration
API_V1_PREFIX=/api/v1
HOST=127.0.0.1
PORT=8000

# LLM & Embedding Credentials (Use secure API keys)
GEMINI_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# ChromaDB Vector Store Persistence
CHROMA_PERSIST_DIR=./data/chroma_db
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

# Document Ingestion Constraints
MAX_UPLOAD_SIZE_MB=25
ALLOWED_EXTENSIONS=["pdf", "docx", "csv", "txt"]

# Relational Database (Optional / Future Persistence)
DATABASE_URL=postgresql://user:password@localhost:5432/project_advisor_db
```

> [!CAUTION]
> Never commit real API keys, passwords, or production database strings to version control or presentation materials.

---

## 3. How to Verify What Is Running

During the Milestone 1 faculty review, demonstrate host readiness and repository integrity with these verified commands:

```powershell
# Step 1: Verify Host Runtime Tools
python --version     # Expected: Python 3.13.3
node --version       # Expected: v22.15.0
npm --version        # Expected: 10.9.2

# Step 2: Verify Python Packages Required for Spreadsheet Governance
python -c "import openpyxl, xlrd; print('OpenPyXL & xlrd: Operational')"

# Step 3: Verify Integrity of Milestone 1 Deliverables
python -c "
import openpyxl
wb1 = openpyxl.load_workbook('milestone1_deliverables/Agile_Template_Milestone1.xlsx')
wb2 = openpyxl.load_workbook('milestone1_deliverables/Defect_Tracker_Milestone1.xlsx')
wb3 = openpyxl.load_workbook('milestone1_deliverables/Unit_Test_Plan_Milestone1.xlsx')
print('Agile Backlog Sheets:', wb1.sheetnames)
print('Defect Tracker Sheets:', wb2.sheetnames)
print('Unit Test Plan Sheets:', wb3.sheetnames)
"
```

---

## 4. Which Actual Files to Open During the Presentation

Have the following physical files open in Microsoft Excel, VS Code, and PowerPoint:

1. **PowerPoint Presentation:**  
   `milestone1_deliverables/Milestone1_Presentation.pptx`  
   *Action:* Present in Slide Show mode (15 slides with embedded speaker notes).
2. **Agile Backlog Workbook:**  
   `milestone1_deliverables/Agile_Template_Milestone1.xlsx`  
   *Action:* Open in Microsoft Excel; navigate to `Product Backlog` (show US-01..US-12) and `Sprint Backlog` (show T-01..T-14 with 0.5–12 hr estimates).
3. **Unit Test Plan Workbook:**  
   `milestone1_deliverables/Unit_Test_Plan_Milestone1.xlsx`  
   *Action:* Open in Microsoft Excel; show sheet `UT` with 28 test cases, pointing out the explicit distinction between `Not Run` tests and executed audit tests.
4. **Defect Tracker Workbook:**  
   `milestone1_deliverables/Defect_Tracker_Milestone1.xlsx`  
   *Action:* Open in Microsoft Excel; show the 4 real audit defects logged with status `Open`.
5. **Repository Audit Markdown:**  
   `MILESTONE1_REPOSITORY_AUDIT.md`  
   *Action:* Open in VS Code preview to demonstrate the physical file tree and audit methodology.
6. **Application Test Report Markdown:**  
   `MILESTONE1_TEST_REPORT.md`  
   *Action:* Open in VS Code preview to show exact terminal commands and outputs.

---

## 5. Which Features Can Be Demonstrated Successfully

| Feature / Artifact | Can It Be Demonstrated? | Demonstration Method |
| :--- | :---: | :--- |
| **System Architecture & Workflow** | **Yes** | Slide 5 & 8 in PowerPoint showing the 5-tier architecture. |
| **Agile Product & Sprint Backlog** | **Yes** | Excel opening `Agile_Template_Milestone1.xlsx` with burn-down formulas. |
| **Active Defect Tracking System** | **Yes** | Excel opening `Defect_Tracker_Milestone1.xlsx` with 4 verified audit defects. |
| **28-Case Unit Test Specification** | **Yes** | Excel opening `Unit_Test_Plan_Milestone1.xlsx` with status highlights. |
| **Physical Codebase Audit** | **Yes** | Live PowerShell terminal running `Get-ChildItem -Force`. |
| **Host Toolchain Verification** | **Yes** | Live terminal checks of Python 3.13, Node 22, and npm 10. |
| **Live Document Upload & Ingestion**| **No** (Planned) | Explain technical design in Slide 6; demonstrate in Milestone 2. |
| **ChromaDB Vector Retrieval** | **No** (Planned) | Explain chunking & isolation design in Slide 6; demonstrate in Milestone 2. |
| **Live Chatbot Interaction** | **No** (Planned) | Explain grounding constraints in Slide 8; demonstrate in Milestone 2. |
| **React Dashboard Execution** | **No** (Planned) | Explain UI component specs in Slide 9; demonstrate in Milestone 2. |

---

## 6. Step-by-Step Demonstration Sequence for Faculty

### Step 1: Presentation Deck (5–7 Minutes)
1. Open `milestone1_deliverables/Milestone1_Presentation.pptx`.
2. Follow `milestone1_deliverables/Milestone1_Presentation_Script.md`.
3. Walk through Problem Statement, Architecture, Repository Audit, and the 9-Module Status Matrix.

### Step 2: Physical Repository Verification (2 Minutes)
1. Switch to PowerShell terminal in `C:\Users\manis\Desktop\SP`.
2. Run: `Get-ChildItem -Force`
3. State to faculty: *"As you can see, our workspace strictly reflects our Phase 1 baseline. We have not created fake code files or simulated fallbacks."*
4. Run: `python -m pytest` -> Show the output (`0 items collected, exit code 1`) to prove that we do not hide real test results.

### Step 3: Project Management & Quality Deliverables (4 Minutes)
1. Switch to Microsoft Excel with `Agile_Template_Milestone1.xlsx`:
   - Highlight User Stories `US-01` to `US-12`.
   - Explain the MoSCoW prioritization and dependency chaining.
   - Switch to `Sprint Backlog`: show 14 tasks with estimates strictly between 0.5 and 12 hours.
   - Show `Stand up Meeting` and `Retrospection` tabs.
2. Switch to `Defect_Tracker_Milestone1.xlsx`:
   - Explain that zero fake bugs were entered.
   - Walk through the 4 real baseline defects logged during audit (Git repo uninitialized, Uvicorn boot fail, Pytest exit 1, missing AI libraries).
   - Point out that all four are kept `Open`.
3. Switch to `Unit_Test_Plan_Milestone1.xlsx`:
   - Walk through the 28 test cases across Ingestion, RAG, Scope, Risk, Blockers, Health Scoring, and Assistant.
   - Highlight the `Test Status` column: explain why prospective tests are honestly marked `Not Run` with actual results stating `Not executed`.

### Step 4: Faculty Q&A & Roadmap Discussion (2–3 Minutes)
1. Conclude on Slide 15 (Milestone 2 Prioritized Implementation Plan).
2. Answer faculty questions using the FAQ answers below.

---

## 7. Expected Results Based on Verified Behavior

When executing commands during the live review, expect these exact outputs:
- **`Get-ChildItem -Force`:** Shows the 3 original template spreadsheets and the `milestone1_deliverables/` folder.
- **`python -m pytest`:** Returns exit code 1 with message `collected 0 items / no tests ran in 0.01s`.
- **`python -m uvicorn main:app`:** Returns exit code 1 with message `ERROR: Could not import module 'main'`.
- **`npm test`:** Returns exit code 1 with message `Error: no test specified`.

---

## 8. Known Issues and Safe Alternatives if a Feature Fails

| Potential Live Issue | Root Cause | Safe Alternative / Presenter Response |
| :--- | :--- | :--- |
| Faculty asks why `uvicorn` fails to start | No application entrypoint written yet | Explain that Milestone 1 explicitly focuses on System Architecture, Agile Planning, and QA Test Design. Open `MILESTONE1_TEST_REPORT.md` to show that this failure was already documented as Defect #2. |
| Faculty asks why the original templates had "Keshav" | Original files were inherited templates | Open `milestone1_deliverables/Template_Update_Summary.md` and explain: *"We preserved the original files for traceability, scrubbed the legacy data, and created verified, customized workbooks in `milestone1_deliverables/`."* |
| PowerPoint slide format issues | Display resolution difference | The presentation is standard 16:9 widescreen (`13.333" x 7.5"`). If PowerPoint is unavailable, use the full markdown transcript in `Milestone1_Presentation_Script.md`. |

---

## 9. Likely Faculty Questions and Accurate Answers

### Q1: "Why don't you have working code or a running demo for Milestone 1?"
> **Answer:** *"In accordance with standard engineering project management and university review guidelines, Milestone 1 is the Project Inception, System Architecture, and Quality Assurance Planning phase. Rather than rushing premature code that lacks structure, we conducted an exhaustive codebase audit, designed the end-to-end multi-agent architecture, created 12 prioritized user stories with a 14-task sprint backlog, established an active defect register, and authored 28 rigorous unit test cases. In Milestone 2, our development proceeds in strict alignment with this plan, starting with document ingestion and ChromaDB vector retrieval."*

### Q2: "How is your platform different from simply pasting a project document into ChatGPT?"
> **Answer:** *"Standard ChatGPT has three fatal flaws for enterprise project management: 1) It suffers from hallucinations, inventing deliverables and dates; 2) It has no concept of project-scoped multi-tenancy or access control; and 3) It cannot perform deterministic schedule calculations. Our platform uses LangGraph to separate deterministic rules—such as negative float calculations and reproducible mathematical health scoring—from generative synthesis. Furthermore, every extracted claim in our RAG pipeline cites exact document coordinates (file name and page number) and explicitly refuses to answer when evidence is absent."*

### Q3: "How will you prevent one project's sensitive documents from leaking into another project in ChromaDB?"
> **Answer:** *"Every text chunk ingested into ChromaDB is stored with mandatory metadata attributes: `project_id`, `document_id`, and `page_number`. When querying the vector store, our retrieval service applies a strict metadata filter: `where={'project_id': current_project_id}`. This guarantees that vector similarity calculations are mathematically restricted to chunks belonging to the authorized project, preventing cross-tenant leakage."*

### Q4: "How does your Project Health Scoring formula work?"
> **Answer:** *"We use an objective, deterministic formula scaled from 0 to 100:  
> `Health Score = 100 - (0.35 * SchedulePenalty + 0.30 * RiskPenalty + 0.20 * BlockerPenalty + 0.15 * MissingDataPenalty)`.  
> Each penalty is mathematically calculated from stored project metrics. Crucially, we penalize missing data: if a project does not upload a risk log or project charter, it receives a 15-point documentation penalty rather than assuming the project has zero risk."*

---

## 10. Strict List of Claims That Should NOT Be Made

Do **NOT** make any of the following claims during the presentation, as they are not supported by codebase evidence:
1. ❌ Do NOT claim that the React dashboard is running or built.
2. ❌ Do NOT claim that document parsing (PDF, DOCX, CSV) is already functioning in Python.
3. ❌ Do NOT claim that ChromaDB is already indexing documents or performing semantic searches.
4. ❌ Do NOT claim that the LangGraph agents are currently executing or integrated with LLM APIs.
5. ❌ Do NOT claim that unit tests 1 through 24 have passed.
6. ❌ Do NOT claim that the four logged defects are closed or resolved.
7. ❌ Do NOT claim that the system has been tested on real client projects.

**Always frame these items as:**
- *"Designed in our system architecture..."*
- *"Specified in our unit test catalog with execution status 'Not Run'..."*
- *"Scheduled for implementation in Sprint 1 and Sprint 2 of Milestone 2..."*
