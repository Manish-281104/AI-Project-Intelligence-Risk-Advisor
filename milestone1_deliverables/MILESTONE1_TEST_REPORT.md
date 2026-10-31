# Milestone 1 Application Verification & Test Report

**Project Title:** AI Project Intelligence & Risk Advisor  
**Test Date:** October 14, 2026  
**Auditor:** Automated Engineering Verification  
**Repository Tested:** `C:\Users\manis\Desktop\SP`  
**Test Protocol:** Strict Physical Verification (No Fabricated Tests or Mock Fallbacks)

---

## 1. Environment Requirements & Host Baseline

To evaluate whether the application could be executed, the local host runtime environment was surveyed.

| Component | Minimum Required by Architecture | Host Detected Version | Status / Gap Analysis |
| :--- | :--- | :--- | :--- |
| **Operating System** | Windows 10/11 / Linux / macOS | Windows 11 Home Single Language (Build 26100) | Compatible |
| **Python** | 3.11+ | Python 3.13.3 & 3.14.2 | Compatible |
| **Node.js** | 18.0+ / 20.0+ | Node.js v22.15.0 | Compatible |
| **Package Manager** | npm 9+ / pnpm / yarn | npm 10.9.2 | Compatible |
| **FastAPI** | 0.100+ | 0.140.0 | Present globally |
| **Uvicorn** | 0.22+ | 0.51.0 | Present globally |
| **ChromaDB** | 0.4+ | Not installed | **Blocking Dependency** |
| **LangGraph / LangChain** | 0.2+ | Not installed | **Blocking Dependency** |
| **python-docx** | 1.1+ | Not installed | **Blocking Dependency** |
| **python-pptx** | 1.0+ | Not installed | **Blocking Dependency** |
| **openpyxl** | 3.1+ | 3.1.5 | Present globally |
| **xlrd** | 2.0+ | 2.0.2 | Installed during audit |
| **Project Virtual Environment** | Isolated `.venv` in workspace | None present in `C:\Users\manis\Desktop\SP` | **Configuration Gap** |

---

## 2. Automated Test Execution Commands & Results

All tests were performed using actual PowerShell executions against the current repository state.

### Test 1: Python Automated Test Discovery (`pytest`)
- **Command:** `python -m pytest`
- **Working Directory:** `C:\Users\manis\Desktop\SP`
- **Exit Code:** `1`
- **Standard Output:**
  ```text
  ============================= test session starts =============================
  platform win32 -- Python 3.13.3, pytest-9.1.1, pluggy-1.6.0
  rootdir: C:\Users\manis\Desktop\SP
  plugins: anyio-4.12.1
  collected 0 items

  ============================ no tests ran in 0.01s ============================
  ```
- **Finding:** Test runner executed successfully, but found 0 test files (`tests/` directory is absent). Pytest returns exit code 1 when zero tests are discovered.

---

### Test 2: Frontend Build / Test Script (`npm test`)
- **Command:** `npm test`
- **Working Directory:** `C:\Users\manis\Desktop\SP`
- **Exit Code:** `1`
- **Standard Output:**
  ```text
  > echo "Error: no test specified" && exit 1
  "Error: no test specified"
  ```
- **Finding:** No `package.json` exists in `C:\Users\manis\Desktop\SP`. The npm CLI traversed upward to the user home directory (`C:\Users\manis\package.json`) which has no test script defined. Frontend build and test are blocked until workspace scaffolding is completed.

---

### Test 3: Backend API Server Initialization (`uvicorn`)
- **Command:** `python -m uvicorn main:app --port 8000`
- **Working Directory:** `C:\Users\manis\Desktop\SP`
- **Exit Code:** `1`
- **Standard Output:**
  ```text
  ERROR:    Error loading ASGI app. Could not import module "main".
  ```
- **Finding:** FastAPI entry point (`main.py`) does not exist on disk. No API endpoints or web servers can run in the current repository state.

---

### Test 4: Document Ingestion Pipeline Verification
- **Verification Attempt:** Checked for sample project artifacts (`.pdf`, `.docx`, `.csv`, `.txt`) and parsing modules.
- **Result:** No document parsing script or sample test documents exist in `C:\Users\manis\Desktop\SP`.
- **Finding:** Document ingestion cannot be executed or tested at Milestone 1.

---

### Test 5: Vector Database & RAG Retrieval Verification
- **Verification Attempt:** Tested import of `chromadb` and searched for vector store persistence files.
- **Result:**
  ```text
  chromadb: NOT found
  langchain: NOT found
  langgraph: NOT found
  ```
- **Finding:** RAG pipeline and ChromaDB indexing cannot be executed.

---

### Test 6: Project Management Spreadsheet Integrity Check
- **Command:** `python -c "import openpyxl, xlrd; ..."`
- **Result:** 
  - `Agile_Template_v0.1.xls`: Verified readable via `xlrd`. Contains 4 sheets (`Product Backlog`, `Sprint Backlog`, `Stand up Meeting`, `Retrospection`).
  - `Defect_Tracker Template_v0.1.xlsx`: Verified readable via `openpyxl`. Contains 2 sheets (`Defects`, `Sheet2`).
  - `Unit_Test_Plan_v0.1.xlsx`: Verified readable via `openpyxl`. Contains 1 sheet (`UT`).
- **Exit Code:** `0`
- **Finding:** The three uploaded workbooks are structurally valid Excel files, but currently contain legacy data from another project that must be replaced.

---

## 3. Summary of Passed and Failed Verification Items

| Verification Item | Command / Probe | Result | Assessment |
| :--- | :--- | :---: | :--- |
| **Directory Integrity** | `Get-ChildItem -Recurse` | Pass | Exactly 3 template files detected; no hidden corruptions. |
| **Excel Workbook Readability** | `openpyxl` & `xlrd` parsing | Pass | Workbooks can be loaded, modified, and saved programmatically. |
| **Unit Test Discovery** | `python -m pytest` | Fail (0 collected) | No unit tests written yet. |
| **Frontend Script Execution**| `npm test` | Fail (Exit 1) | No `package.json` in workspace. |
| **Backend API Boot** | `uvicorn main:app` | Fail (Exit 1) | No `main.py` entrypoint. |
| **Document Ingestion** | Ingestion pipeline check | Fail (No code) | Ingestion service not yet built. |
| **RAG Vector Search** | ChromaDB retrieval check | Fail (No library) | ChromaDB and LangGraph not installed. |

---

## 4. Required Screenshots for Faculty Milestone Review

Because the full-stack software application is not yet executing, **genuine screenshots must focus on verifiable engineering artifacts**, rather than mock interfaces:

1. **Screenshot 1: Actual Workspace Directory Tree in File Explorer / Terminal**
   - *Target:* PowerShell displaying `Get-ChildItem -Force` in `C:\Users\manis\Desktop\SP`.
   - *Rationale:* Proves total transparency regarding the starting codebase.
2. **Screenshot 2: Host Environment Verification**
   - *Target:* PowerShell showing `python --version`, `node --version`, and `npm --version`.
   - *Rationale:* Demonstrates host environment readiness for Milestone 2 development.
3. **Screenshot 3: Agile Backlog Workbook (`Agile_Template_Milestone1.xlsx`)**
   - *Target:* Microsoft Excel opening the populated `Product Backlog` sheet showing User Stories `US-01` to `US-09` with MoSCoW priorities and Sprint allocations.
   - *Rationale:* Tangible evidence of Milestone 1 project management planning.
4. **Screenshot 4: Unit Test Plan Workbook (`Unit_Test_Plan_Milestone1.xlsx`)**
   - *Target:* Microsoft Excel displaying the populated `UT` sheet with 20+ test cases across Ingestion, RAG, Agents, Scoring, and UI, with execution status honestly set to `Not Run`.
   - *Rationale:* Demonstrates rigorous test engineering design prior to coding.
5. **Screenshot 5: Defect Tracker Workbook (`Defect_Tracker_Milestone1.xlsx`)**
   - *Target:* Microsoft Excel displaying the clean `Defects` register ready for QA logging with standardized defect categories.
   - *Rationale:* Demonstrates QA governance structure.

---

## 5. Known Gaps, Bugs, and Recommended Fixes

| # | Discovered Gap / Bug | Severity | Root Cause | Recommended Remediation |
| :- | :--- | :---: | :--- | :--- |
| **G-01** | **No Git Version Control** | High | Git repository was never initialized in `C:\Users\manis\Desktop\SP`. | Run `git init`, add standard `.gitignore` (ignoring `.venv`, `node_modules`, `__pycache__`), and create initial commit. |
| **G-02** | **Legacy Content in Templates** | High | Uploaded templates contain references to "Keshav" and "Monaco Editor". | Clean and populate templates with "AI Project Intelligence & Risk Advisor" content. Save as `milestone1_deliverables/*.xlsx`. |
| **G-03** | **Missing Python Dependencies** | Medium | `chromadb`, `langgraph`, `python-docx`, `python-pptx` not in environment. | Create `requirements.txt` and install target packages in a dedicated `.venv`. |
| **G-04** | **No Project Document Samples** | Medium | No project management artifacts (SOW, Risk Register, Minutes) available. | Create a standardized `test_data/` folder containing realistic project documents (PDF, DOCX, CSV, TXT) for Milestone 2 testing. |
