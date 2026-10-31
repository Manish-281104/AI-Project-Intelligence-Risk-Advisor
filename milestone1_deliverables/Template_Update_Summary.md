# Project Management Template Update Summary: First Presentation Scope (Days 1–4)

**Project Title:** AI Project Intelligence & Risk Advisor  
**Review Stage:** Milestone 1 (Initial Project Planning & Setup Scope)  
**Effort Represented:** Approximately 3–4 Days of Initial Setup & Architecture  
**Author / Engineer:** Manish  
**Deliverables Directory:** `milestone1_deliverables/`

---

## 1. Revision Overview & Scope Calibration

In response to faculty review guidance, the three Excel workbooks were revised to represent an **early milestone scope** reflecting **approximately 3–4 days of initial project planning and setup**, rather than an advanced stage of development:
- **Original Templates Preserved:** The original files (`Agile_Template_v0.1.xls`, `Defect_Tracker Template_v0.1.xlsx`, and `Unit_Test_Plan_v0.1.xlsx`) remain untouched in the root directory.
- **Scope Calibration:** Unnecessary complexity, excessive rows, and advanced agent metrics were removed.
- **Target Deliverables in `milestone1_deliverables/`:**
  1. [`Agile_Template_Milestone1.xlsx`](file:///c:/Users/manis/Desktop/SP/milestone1_deliverables/Agile_Template_Milestone1.xlsx)
  2. [`Defect_Tracker_Milestone1.xlsx`](file:///c:/Users/manis/Desktop/SP/milestone1_deliverables/Defect_Tracker_Milestone1.xlsx)
  3. [`Unit_Test_Plan_Milestone1.xlsx`](file:///c:/Users/manis/Desktop/SP/milestone1_deliverables/Unit_Test_Plan_Milestone1.xlsx)

---

## 2. Workbook 1: Agile Planning (`Agile_Template_Milestone1.xlsx`)

### Format & Structure
- **Format:** Converted from legacy `.xls` to modern OpenXML `.xlsx` with preserved structure, formulas, and headers.
- **Sheets Included:** `Product Backlog`, `Sprint Backlog`, `Stand up Meeting`, `Retrospection`.

### Worksheet Modifications
1. **Product Backlog (6 Simple User Stories):**
   - `US-01`: Set up project repository, folder structure, and local dev environments (`MUST HAVE`, Sprint 1, In Progress).
   - `US-02`: Design system architecture, core module boundaries, and high-level data flow (`MUST HAVE`, Sprint 1, Completed).
   - `US-03`: Define supported document formats (PDF, DOCX, CSV, TXT) and validation rules (`MUST HAVE`, Sprint 1, In Progress).
   - `US-04`: Prepare document upload workflow and basic file ingestion pipeline (`MUST HAVE`, Sprint 1, Planned).
   - `US-05`: Plan RAG knowledge base, chunking strategy, and ChromaDB vector store (`SHOULD HAVE`, Sprint 2, Planned).
   - `US-06`: Design initial dashboard layout wireframes and user interaction flow (`COULD HAVE`, Sprint 2, Planned).
2. **Sprint Backlog (7 Initial Tasks, 22.0 Hours Total):**
   - Total effort is **22.0 hours** spread across Days 1–4 (~5.5 hours/day across the team), realistically modeling initial part-time planning effort:
     - `T-01`: Repository and folder structure setup (2.0 hrs, Day 1, Completed).
     - `T-02`: Dependency survey and configuration setup (2.5 hrs, Day 1, Completed).
     - `T-03`: System architecture and data flow design (4.0 hrs, Day 2, Completed).
     - `T-04`: Initial API route design and request schemas (3.5 hrs, Days 2–3, In Progress).
     - `T-05`: Document ingestion workflow and validation design (3.0 hrs, Day 3, In Progress).
     - `T-06`: Basic unit test plan authoring and test setup (3.0 hrs, Days 3–4, Completed).
     - `T-07`: Milestone 1 review documentation and slide preparation (4.0 hrs, Day 4, Completed).
   - Task sizing strictly obeys the template's constraint of **0.5 to 12 hours**.
   - Formula row (`=SUM(I5:I11)`) dynamically aggregates planned effort.
3. **Stand up Meeting:**
   - 1 genuine kick-off meeting entry for Day 1: "Identified that workspace lacks dedicated virtual environment and Git repository is uninitialized." Action Taken: "Documented setup requirements; planned Git initialization and virtual environment configuration in initial tasks."
   - Days 2, 3, and 4 are clearly labeled as planned meeting entries.
4. **Retrospection:**
   - Labeled `Initial Sprint Retrospective - Pending (Sprint in progress)` for Sprint 1. Actual retrospective findings remain blank, ready for sprint closure.

---

## 3. Workbook 2: Defect Tracker (`Defect_Tracker_Milestone1.xlsx`)

### Structure & Governance
- **Sheets Included:** `Defects` and `Sheet2` (Defect categories: *Logical, User Interface, Maintainability, Standards, Others*).
- **Lightweight Design:** No hypothetical or fabricated defects.
- **Single Verified Observation:**
  - `Sl No`: 1
  - `Submitted By`: Manish
  - `Submitted Date`: 2026-10-14
  - `Description`: "Workspace repository is not yet initialized in Git and lacks dedicated virtual environment."
  - `Detected Sprint`: Sprint 1
  - `Assigned To`: Manish
  - `Type Of Defect`: Maintainability
  - `Action Taken`: "Documented in MILESTONE1_REPOSITORY_AUDIT.md; scheduled Git initialization and virtual environment creation in initial setup tasks."
  - `Status`: Open
  - `Remarks`: "Identified during initial project setup."
- Rows 2 to 15 are left clean, formatted, and ready for future QA logging during development.

---

## 4. Workbook 3: Unit Test Plan (`Unit_Test_Plan_Milestone1.xlsx`)

### Structure & Contents
- **Worksheet:** `UT` (Preserved original 6 columns + `Test Status` column).
- **Scope:** **7 basic test cases** directly relevant to early setup, server boot, and validation:
  1. `TC-01`: Frontend Development Server Startup (`npm run dev` on localhost:5173). Status: `Not Run`.
  2. `TC-02`: FastAPI Backend Server Startup (`uvicorn main:app` on localhost:8000). Status: `Not Run`.
  3. `TC-03`: Backend Health Endpoint Response (`GET /health` returns `{"status": "ok"}`). Status: `Not Run`.
  4. `TC-04`: Supported Document Format Identification (Whitelisted extensions .pdf, .docx, .csv, .txt permitted). Status: `Not Run`.
  5. `TC-05`: Invalid Document Format Rejection (Disallowed extensions rejected with HTTP 415). Status: `Not Run`.
  6. `TC-06`: ChromaDB Vector Store Connection (Persistent client initializes collection). Status: `Not Run`.
  7. `TC-07`: Automated Test Runner Discovery (`python -m pytest` discovers test files). Status: `Not Run`.
- **Truth in Reporting:** All 7 test cases have `Actual Result` explicitly stated as `"Not executed (Scheduled in Sprint 1/2)"` and `Test Status` marked as `Not Run` (highlighted in amber).

---

## 5. Verification Checklist

- [x] All 3 workbooks reloaded and validated using `openpyxl`.
- [x] Formulas verified (`=SUM(...)` in Sprint Backlog).
- [x] Total effort across tasks equals 22.0 hours (3–4 days initial effort).
- [x] Zero fabricated bugs; single genuine setup observation kept Open.
- [x] Test plan contains 7 relevant setup cases with status `Not Run`.
- [x] All materials saved in `milestone1_deliverables/`.
