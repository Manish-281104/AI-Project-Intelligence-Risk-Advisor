# Milestone 1 Presentation Script: AI Project Intelligence & Risk Advisor

**Project Title:** AI Project Intelligence & Risk Advisor  
**Presenter:** Manish (Department of Computer Science & Engineering)  
**Target Duration:** 10 – 12 Minutes  
**Review Scope:** Days 1–4 Initial Project Planning, Architecture Design & Setup Review  
**Accompanying Slide Deck:** `milestone1_deliverables/Milestone1_Presentation.pptx` (15 Slides)

---

## Slide 1: Title Slide
- **Slide Title:** AI Project Intelligence & Risk Advisor — Milestone 1 Review
- **Visuals on Slide:** Dark navy theme, project title, subtitle (Initial Project Planning, System Architecture & Setup Review), student details, date.
- **Presenter Spoken Script:**
  > "Respected faculty members, internal evaluators, and my fellow students: Good morning. My name is Manish, and I am presenting Milestone 1 for my final-year B.Tech major project titled **AI Project Intelligence & Risk Advisor**.
  >
  > This first milestone review represents our team's **first 3 to 4 days of initial project planning, system architecture design, and setup**.
  >
  > Rather than making speculative claims about completed features, today I will walk you through our **forensic codebase audit of our workspace**, our **verified end-to-end system architecture**, our **initial 6-story Agile backlog**, our **lightweight defect tracking setup**, and our **7-case foundational unit test plan**. This establishes a disciplined, realistic foundation for our upcoming development."

---

## Slide 2: Problem Statement & Industry Motivation
- **Slide Title:** Problem Statement & Industry Motivation
- **Visuals on Slide:** 3 structured cards highlighting *Fragmented Project Knowledge*, *Latent Risks & Schedule Slips*, and *LLM Hallucination Hazards*.
- **Presenter Spoken Script:**
  > "To understand the motivation behind our platform, software engineering projects routinely struggle with three fundamental failure modes:
  >
  > First, project knowledge is fragmented across formats—PDF contracts, Word meeting minutes, CSV sprint backlogs, and plain text notes. Project managers spend up to a third of their time manually cross-referencing these files.
  >
  > Second, delivery risks and schedule slips are typically discovered too late, after milestones are already missed, because manual reviews are subjective and infrequent.
  >
  > Third, while teams are experimenting with off-the-shelf generative AI, generic chatbots hallucinate deliverable dates, invent stakeholders, and provide ungrounded advice. In software engineering governance, every single insight must cite an authenticated document with exact page coordinates. Our platform directly solves these problems."

---

## Slide 3: Project Objectives & Proposed Solution Architecture
- **Slide Title:** Project Objectives & Proposed Solution Architecture
- **Visuals on Slide:** High-level project objectives paired with the target technology stack (FastAPI, LangGraph, ChromaDB, React, PyMuPDF).
- **Presenter Spoken Script:**
  > "Our platform fulfills five core objectives:
  >
  > 1. **Multi-Format Ingestion:** Ingest PDF, DOCX, CSV, and TXT files, preserving coordinate metadata like page numbers and table rows.
  > 2. **Grounded RAG Knowledge Base:** Index chunks into a persistent vector store using ChromaDB with strict project isolation.
  > 3. **Multi-Agent Intelligence:** Deploy LangGraph stateful graphs with four specialized agents to extract scope, calculate deterministic schedule slips, capture blockers, and generate project drafts.
  > 4. **Transparent Project Health Scoring:** Calculate a deterministic 0-to-100 health score using a mathematical formula with weighted penalties, ensuring scores are fully reproducible.
  > 5. **Grounded Conversational Assistant:** Provide an interactive chat interface that answers questions with clickable citations and strictly refuses to answer when evidence is absent.
  >
  > Our technology stack pairs Python and FastAPI for the backend microservice with React, TypeScript, and Tailwind CSS for the frontend dashboard."

---

## Slide 4: Actual Repository Audit & Baseline Verification
- **Slide Title:** Actual Repository Audit & Baseline Verification
- **Visuals on Slide:** Exact directory tree of `C:\Users\manis\Desktop\SP`, physical file list (the 3 template files), and remediation protocol.
- **Presenter Spoken Script:**
  > "In accordance with strict academic integrity, we began by conducting a physical audit of our workspace `C:\Users\manis\Desktop\SP`.
  >
  > A recursive PowerShell inspection confirmed that exactly three spreadsheet files existed: `Agile_Template_v0.1.xls`, `Defect_Tracker Template_v0.1.xlsx`, and `Unit_Test_Plan_v0.1.xlsx`. No frontend or backend source code existed, and Git was not yet initialized.
  >
  > We observed that the original templates contained leftover sample entries from an earlier project. We preserved the original files and created verified, project-specific deliverables in our `milestone1_deliverables/` folder, tailored specifically to our initial 3-to-4 day planning scope."

---

## Slide 5: System Architecture & Component Implementation State
- **Slide Title:** System Architecture & Component Implementation State
- **Visuals on Slide:** 5 architectural layers (Ingestion -> Vector Store -> LangGraph Agents -> API & Health Scorer -> React UI & Governance) with color-coded status badges.
- **Presenter Spoken Script:**
  > "Slide 5 shows our complete system architecture and visually distinguishes what has been completed in Milestone 1 from what is scheduled for implementation.
  >
  > The architecture spans five clean tiers: Data Ingestion, Vector Storage & RAG, LangGraph Multi-Agent Orchestration, FastAPI Backend & Health Scoring, and the React Dashboard.
  >
  > As clearly indicated by our status badges, our project management frameworks, architecture blueprints, and quality plans are completed, while code implementation for each tier is scheduled across upcoming sprints."

---

## Slide 6: Document Ingestion & Grounded RAG Pipeline Architecture
- **Slide Title:** Document Ingestion & Grounded RAG Pipeline Architecture
- **Visuals on Slide:** Deep dive into Module 1 (Ingestion) and Module 2 (ChromaDB RAG).
- **Presenter Spoken Script:**
  > "In Module 1, our document ingestion service uses PyMuPDF for PDFs to capture page numbers for citations. For Word documents, python-docx serializes tables so structured risk registers don't lose formatting. For CSVs, pandas loads rows into structured entities. Uploads are guarded by MIME type validation and file size limits.
  >
  > In Module 2, our RAG pipeline uses a recursive character splitter with an 800-character chunk size and 150-character overlap to preserve context across boundaries. Chunks are embedded and stored in ChromaDB with metadata attributes: project ID, document ID, file name, and page number, enforcing project-isolated retrieval."

---

## Slide 7: LangGraph Multi-Agent Orchestration Engine
- **Slide Title:** LangGraph Multi-Agent Orchestration Engine
- **Visuals on Slide:** 4 agent cards: Scope Extraction, Risk & Schedule Slip, Blocker & Action Items, and Documentation Generation.
- **Presenter Spoken Script:**
  > "Slide 7 outlines our four specialized AI agents to be built in upcoming sprints using LangGraph:
  >
  > - **Scope Extraction Agent:** Extracts deliverables and milestones into Pydantic JSON schemas with source citations.
  > - **Risk & Schedule Slip Agent:** Combines deterministic date arithmetic to calculate negative float for overdue tasks with an LLM that maps qualitative risks onto a 5x5 severity matrix.
  > - **Blocker Agent:** Detects active blockers from meeting minutes, using strict prompts that output 'UNKNOWN' when assignees or dates are missing, preventing hallucination.
  > - **Documentation Agent:** Synthesizes user stories and risk registers with mandatory draft disclaimers."

---

## Slide 8: Objective Health Scoring & Grounded Chatbot Assistant
- **Slide Title:** Objective Health Scoring & Grounded Chatbot Assistant
- **Visuals on Slide:** Mathematical health score formula and weights; Conversational Assistant grounding constraints and refusal guardrail.
- **Presenter Spoken Script:**
  > "Slide 8 details Modules 7 and 8.
  >
  > For Project Health Scoring, we use an objective mathematical formula scaled from 0 to 100:
  > `Health Score = 100 - [0.35 * SchedulePenalty + 0.30 * RiskPenalty + 0.20 * BlockerPenalty + 0.15 * MissingDataPenalty]`.
  > Missing documentation is penalized: if a team uploads no risk register, the system applies a missing-documentation penalty rather than assuming zero risk.
  >
  > For Module 8, our Conversational Assistant injects retrieved ChromaDB chunks into a grounded prompt. Every answer includes citations. If information is absent from the files, the assistant explicitly states that no evidence exists."

---

## Slide 9: Nine-Module Implementation Status Matrix
- **Slide Title:** Nine-Module Implementation Status Matrix
- **Visuals on Slide:** Structured 10-row table mapping all 9 modules, status (Planned), verification performed, and target sprints.
- **Presenter Spoken Script:**
  > "Slide 9 displays our Nine-Module Implementation Status Matrix.
  >
  > At this initial 3-to-4 day milestone, all nine functional modules are transparently designated as **'Planned'**. During our audit, we ran verification commands confirming that no parser scripts, ChromaDB vector stores, agent nodes, or React components existed yet.
  >
  > We have mapped each module to an explicit sprint target, providing an actionable, phased engineering schedule."

---

## Slide 10: Agile Planning: Initial Setup & Planning (Days 1 to 4)
- **Slide Title:** Agile Planning: Initial Setup & Planning (Days 1 to 4)
- **Visuals on Slide:** Overview of `Agile_Template_Milestone1.xlsx`, Product Backlog (6 stories), and Sprint 1 Backlog (7 tasks, 22.0 hours).
- **Presenter Spoken Script:**
  > "Turning to our project management deliverables, Slide 10 highlights our revised Agile workbook, saved in `milestone1_deliverables/Agile_Template_Milestone1.xlsx`.
  >
  > In the Product Backlog, we defined **6 foundational user stories** covering repository setup, architecture design, document formats, upload workflows, RAG planning, and dashboard wireframing.
  >
  > In the Sprint Backlog, we defined **7 initial tasks** representing our first 3 to 4 days of effort, totaling **22.0 hours** across the team (~5.5 hours per day). Tasks T-01, T-02, T-03, T-06, and T-07 are completed, while API and ingestion design tasks are in progress. All task estimates strictly adhere to the 0.5 to 12 hour constraint.
  >
  > Our standup meeting tab records our Day 1 kick-off meeting, and our retrospective tab is labeled 'Pending', ready for sprint completion."

---

## Slide 11: Defect Tracking & Initial Quality Setup
- **Slide Title:** Defect Tracking & Initial Quality Setup
- **Visuals on Slide:** Display of `Defect_Tracker_Milestone1.xlsx` and the 1 real setup observation logged as Open.
- **Presenter Spoken Script:**
  > "Slide 11 demonstrates our lightweight Defect Tracker workbook, saved as `Defect_Tracker_Milestone1.xlsx`.
  >
  > Rather than inventing hypothetical bugs, we kept the tracker clean and logged exactly **one genuine setup observation** discovered during our repository audit: that the workspace was not yet initialized in Git and lacked a dedicated virtual environment.
  >
  > This defect is assigned to me with status **'Open'**. The remaining rows are formatted and clean, ready for quality assurance logging once development begins in Sprint 1."

---

## Slide 12: Unit Test Plan: Initial Setup & Verification (7 Cases)
- **Slide Title:** Unit Test Plan: Initial Setup & Verification (7 Cases)
- **Visuals on Slide:** Overview of `Unit_Test_Plan_Milestone1.xlsx`, 7 foundational test cases covering setup and verification.
- **Presenter Spoken Script:**
  > "Slide 12 presents our Unit Test Plan workbook, saved as `Unit_Test_Plan_Milestone1.xlsx`.
  >
  > We defined **7 foundational test cases** directly relevant to our setup stage:
  > - TC-01: Frontend development server startup (`npm run dev`).
  > - TC-02: FastAPI backend server startup (`uvicorn main:app`).
  > - TC-03: Backend health endpoint response (`GET /health`).
  > - TC-04: Supported document format identification (PDF, DOCX, CSV, TXT).
  > - TC-05: Invalid document format rejection (.exe, .zip).
  > - TC-06: ChromaDB vector store persistent connection.
  > - TC-07: Automated pytest test runner discovery.
  >
  > All 7 test cases have their actual results recorded as **'Not executed'** and their status honestly marked as **'Not Run'**. We make zero false claims of completed AI testing prior to code development."

---

## Slide 13: Milestone 1 Physical Verification & Command Outputs
- **Slide Title:** Milestone 1 Physical Verification & Command Outputs
- **Visuals on Slide:** Terminal outputs from `pytest`, `uvicorn`, `npm test`, and python dependency checks; list of 5 markdown evidence artifacts.
- **Presenter Spoken Script:**
  > "Slide 13 provides the raw terminal logs from our verification tests, documented in `MILESTONE1_TEST_REPORT.md`.
  >
  > Running `python -m pytest` returned exit code 1 because no test directory was present. Running `uvicorn main:app` returned exit code 1 because `main.py` was absent. Running `npm test` failed because no `package.json` was found in the workspace.
  >
  > We documented every command, exit code, and stdout log. All reports and the three customized spreadsheets are stored directly in our project workspace for faculty inspection."

---

## Slide 14: Current Limitations & Technical Risk Management
- **Slide Title:** Current Limitations & Technical Risk Management
- **Visuals on Slide:** 4 observed technical limitations paired with concrete mitigation actions scheduled in Sprint 1.
- **Presenter Spoken Script:**
  > "We have identified four primary constraints:
  > 1. Version control was uninitialized. Mitigation: Task T-01 runs `git init`, establishes a `.gitignore`, and creates our initial commit.
  > 2. The host Python environment lacks target AI packages. Mitigation: Task T-02 creates an isolated virtual environment with pinned packages in `requirements.txt`.
  > 3. The workspace currently lacks sample project documents. Mitigation: We will curate a `test_data/` folder containing realistic project documents across PDF, DOCX, CSV, and TXT formats.
  > 4. The backend and frontend are not yet running. Mitigation: Tasks T-04 and T-05 scaffold the FastAPI application and ChromaDB vector store."

---

## Slide 15: Conclusion & Next Milestone Plan
- **Slide Title:** Conclusion & Next Milestone Plan
- **Visuals on Slide:** Summary of completed Milestone 1 deliverables and prioritized 5-step build roadmap for Milestone 2.
- **Presenter Spoken Script:**
  > "In conclusion, Milestone 1 has successfully established the initial planning, architecture design, and quality assurance framework for the **AI Project Intelligence & Risk Advisor** after our first 3 to 4 days of setup.
  >
  > We have verified our starting repository state, eliminated legacy template data, created a realistic 22-hour initial sprint backlog, established a clean defect tracker, and defined 7 foundational test cases.
  >
  > For Milestone 2, our priority is to build the multi-format document ingestion pipeline and ChromaDB vector store, followed by the LangGraph agents.
  >
  > Thank you for your time and attention. I am now ready to take your questions."
