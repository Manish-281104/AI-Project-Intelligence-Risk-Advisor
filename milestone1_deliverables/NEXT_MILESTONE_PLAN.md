# Milestone 2 Implementation Roadmap: AI Project Intelligence & Risk Advisor

**Document Version:** 1.0  
**Date:** October 14, 2026  
**Target Milestone:** Milestone 2 (Core Engineering, Multi-Agent RAG & Working Prototype)  
**Author / Lead:** Manish  
**Workspace:** `C:\Users\manis\Desktop\SP`

---

## 1. Prioritized Implementation Sequence

Based on codebase dependencies and the findings of `MILESTONE1_REPOSITORY_AUDIT.md`, development is structured into the following prioritized order:

```
[Phase 0: Scaffolding & Git Init] ──> [Task 1: Document Ingestion] ──> [Task 2: RAG Pipeline & ChromaDB]
                                                                                │
                                                                                ▼
[Task 5: Blocker Extraction] <── [Task 4: Risk & Schedule Engine] <── [Task 3: Scope Extraction Agent]
            │                                   │
            ▼                                   ▼
[Task 6: Doc Generation] ──────────> [Task 7: Health Scoring Formula]
                                                │
                                                ▼
[Task 9: React Dashboard] <────────── [Task 8: Conversational Assistant]
            │
            ▼
[Task 10: End-to-End Testing & Deployment Preparation]
```

---

## 2. Detailed Task Breakdown

### Task 0: Foundation Scaffolding & Version Control Setup (Sprint 1, Day 1)
- **Required Changes:** Initialize Git version control; configure `.gitignore` for Python (`.venv`, `__pycache__`) and Node (`node_modules`, `dist`); set up an isolated Python virtual environment (`.venv`) and install baseline dependencies.
- **Relevant Existing Files:** None in workspace.
- **New Files Needed:**
  - `.gitignore`
  - `requirements.txt`
  - `backend/main.py`
  - `backend/core/config.py`
- **Dependencies:** None.
- **Acceptance Criteria:**
  - `git status` shows clean tracking branch on `main`.
  - Pinned `requirements.txt` installs successfully in `.venv`.
  - `uvicorn backend.main:app` boots cleanly on port 8000 and responds to `GET /health`.
- **Verification Steps:**
  - Run: `git status` -> Verify repository initialized.
  - Run: `curl http://127.0.0.1:8000/health` -> Verify HTTP 200 `{"status": "ok"}`.

---

### Task 1: Complete Document Ingestion Pipeline (Sprint 1, Days 2–4)
- **Required Changes:** Build multi-format document parsers handling PDF, DOCX, CSV, and TXT files. Preserve structural coordinate metadata (page numbers, table row indexes, document timestamps). Implement file validation middleware enforcing MIME types and 25MB size limits.
- **Relevant Existing Files:** `Unit_Test_Plan_Milestone1.xlsx` (Test cases `UT-ING-01` to `UT-ING-06`).
- **New Files Needed:**
  - `backend/services/ingestion/__init__.py`
  - `backend/services/ingestion/validator.py`
  - `backend/services/ingestion/pdf_parser.py` (PyMuPDF)
  - `backend/services/ingestion/docx_parser.py` (python-docx)
  - `backend/services/ingestion/csv_parser.py` (pandas)
  - `backend/services/ingestion/txt_parser.py`
  - `backend/api/v1/routes/documents.py`
  - `test_data/sample_charter.pdf`, `test_data/meeting_minutes.docx`, `test_data/sprint_backlog.csv`
- **Dependencies:** Task 0.
- **Acceptance Criteria:**
  - PDF parser extracts text with per-page tracking (pages 1 to N).
  - DOCX parser extracts paragraphs and 4-column tables preserving row structures.
  - CSV parser loads sprint task items into structured dicts.
  - Unsupported files (`.exe`, `.zip`) return HTTP 415.
- **Verification Steps:**
  - Run: `pytest tests/test_ingestion.py` covering tests `UT-ING-01` through `UT-ING-06`.

---

### Task 2: Validate RAG Retrieval and Evidence Citations (Sprint 1, Days 5–7)
- **Required Changes:** Implement recursive character chunking (800 chars, 150 overlap). Integrate ChromaDB persistent vector database. Embed chunks using `all-MiniLM-L6-v2`. Store rich metadata (`project_id`, `document_id`, `page_number`, `chunk_id`). Enforce multi-tenant query filtering.
- **Relevant Existing Files:** `Unit_Test_Plan_Milestone1.xlsx` (Test cases `UT-RAG-01` to `UT-RAG-04`).
- **New Files Needed:**
  - `backend/services/rag/__init__.py`
  - `backend/services/rag/chunker.py`
  - `backend/services/rag/embeddings.py`
  - `backend/services/rag/chroma_client.py`
  - `backend/services/rag/retriever.py`
  - `backend/api/v1/routes/rag.py`
- **Dependencies:** Task 1.
- **Acceptance Criteria:**
  - Text chunked into 800-character segments with 150-character overlap.
  - Vectors indexed in local ChromaDB directory (`backend/data/chroma/`).
  - Semantic similarity queries return top-k chunks with cosine similarity > 0.70.
  - Queries with `project_id='Project_A'` return zero chunks belonging to `'Project_B'`.
- **Verification Steps:**
  - Run: `pytest tests/test_rag.py` covering tests `UT-RAG-01` through `UT-RAG-04`.

---

### Task 3: Implement Scope and Deliverable Extraction Agent (Sprint 2, Days 1–3)
- **Required Changes:** Build a LangGraph stateful graph with a specialized extraction node. Define Pydantic models for project goals, deliverables, milestones, and acceptance criteria. Enforce sentence-level source citations mapping to chunk IDs.
- **Relevant Existing Files:** `Unit_Test_Plan_Milestone1.xlsx` (Test cases `UT-SCP-01` to `UT-SCP-02`).
- **New Files Needed:**
  - `backend/schemas/scope.py`
  - `backend/agents/state.py`
  - `backend/agents/scope_agent.py`
  - `backend/api/v1/routes/agents.py`
- **Dependencies:** Task 2.
- **Acceptance Criteria:**
  - Agent produces valid JSON conforming to `ScopeExtractionResult` schema.
  - Every extracted deliverable includes `deliverable_name`, `milestone`, `target_date`, and `source_citation` (document name and page number).
- **Verification Steps:**
  - Run: `pytest tests/test_scope_agent.py` against `test_data/sample_charter.pdf`.

---

### Task 4: Implement Risk Detection & Delivery Forecasting Agent (Sprint 2, Days 4–6)
- **Required Changes:** Implement dual-engine risk analysis:
  1. *Deterministic Engine:* Date difference calculator comparing milestone target dates against current date; calculates float and flags overdue items.
  2. *LLM Extraction Engine:* Extracts qualitative risks (technical dependencies, resource bottlenecks) and assigns Likelihood ($1-5$) and Impact ($1-5$) on a $5 \times 5$ matrix.
- **Relevant Existing Files:** `Unit_Test_Plan_Milestone1.xlsx` (Test cases `UT-RSK-01` to `UT-RSK-02`).
- **New Files Needed:**
  - `backend/schemas/risk.py`
  - `backend/services/risk/deterministic_rules.py`
  - `backend/agents/risk_agent.py`
- **Dependencies:** Task 3.
- **Acceptance Criteria:**
  - Tasks with target date in the past are deterministically flagged as `OVERDUE` with exact negative float days.
  - Qualitative risks mapped to standard severity bands: Low (1-4), Medium (5-9), High (10-16), Critical (17-25).
- **Verification Steps:**
  - Run: `pytest tests/test_risk_agent.py` covering tests `UT-RSK-01` and `UT-RSK-02`.

---

### Task 5: Implement Blocker and Action Item Extraction Agent (Sprint 2, Days 7–9)
- **Required Changes:** Build meeting notes parser to extract decisions, blockers, and assigned action items. Enforce strict anti-hallucination prompting: when an owner or deadline is omitted in the source text, the agent must output `"UNKNOWN"` rather than fabricating values.
- **Relevant Existing Files:** `Unit_Test_Plan_Milestone1.xlsx` (Test case `UT-BLK-01`).
- **New Files Needed:**
  - `backend/schemas/action_items.py`
  - `backend/agents/blocker_agent.py`
- **Dependencies:** Task 2.
- **Acceptance Criteria:**
  - Unresolved blockers extracted with severity and days active.
  - Missing assignees mapped to `"UNKNOWN"`; missing deadlines mapped to `"UNKNOWN"`.
  - Zero hallucinated names or dates generated.
- **Verification Steps:**
  - Run: `pytest tests/test_blocker_agent.py` against `test_data/meeting_minutes.docx`.

---

### Task 6: Implement Documentation Generation Agent (Sprint 3, Days 1–3)
- **Required Changes:** Build document synthesis agent to generate standardized project artifacts: User Stories with Gherkin acceptance criteria, Tabular Risk Registers, and Executive Status Briefings. Prepend mandatory draft disclaimers and chunk-level footnotes.
- **Relevant Existing Files:** `Unit_Test_Plan_Milestone1.xlsx` (Test cases `UT-DOC-01` to `UT-DOC-02`).
- **New Files Needed:**
  - `backend/agents/doc_generator_agent.py`
  - `backend/templates/user_stories.md.jinja`
  - `backend/templates/risk_register.md.jinja`
  - `backend/templates/status_report.md.jinja`
- **Dependencies:** Tasks 3, 4, 5.
- **Acceptance Criteria:**
  - Synthesized markdown artifacts include header: `"DRAFT - Generated by AI Project Intelligence"`.
  - Every extracted requirement links back to ingested document chunk citations.
- **Verification Steps:**
  - Run: `pytest tests/test_doc_generator.py`.

---

### Task 7: Implement Transparent Project Health Scoring Engine (Sprint 3, Days 4–6)
- **Required Changes:** Implement mathematical scoring algorithm ($0-100$) combining schedule adherence ($W_s=0.35$), risk severity ($W_r=0.30$), blocker volume ($W_b=0.20$), and documentation completeness ($W_d=0.15$). Apply conservative missing-data penalty (15 points) when critical logs are missing.
- **Relevant Existing Files:** `Unit_Test_Plan_Milestone1.xlsx` (Test cases `UT-HLT-01` to `UT-HLT-02`).
- **New Files Needed:**
  - `backend/services/health/scoring_engine.py`
  - `backend/schemas/health.py`
  - `backend/api/v1/routes/health.py`
- **Dependencies:** Tasks 4, 5.
- **Acceptance Criteria:**
  - Output score is 100% reproducible given identical stored inputs.
  - Score breakdown includes detailed penalty itemization.
  - Projects missing risk registers receive missing data penalty rather than 100% health.
- **Verification Steps:**
  - Run: `pytest tests/test_health_scoring.py` covering tests `UT-HLT-01` and `UT-HLT-02`.

---

### Task 8: Integrate Conversational Project Assistant (Sprint 3, Days 7–9)
- **Required Changes:** Build `/api/v1/chat` conversational endpoint integrating ChromaDB retriever with grounded system prompt. Implement interactive citation badge generator and explicit refusal guardrail for ungrounded queries.
- **Relevant Existing Files:** `Unit_Test_Plan_Milestone1.xlsx` (Test cases `UT-CHT-01` to `UT-CHT-02`).
- **New Files Needed:**
  - `backend/agents/conversational_assistant.py`
  - `backend/api/v1/routes/chat.py`
  - `backend/core/prompts.py`
- **Dependencies:** Tasks 2, 7.
- **Acceptance Criteria:**
  - Responses cite exact source documents (`[Page X, File.pdf]`).
  - Questions with retrieval similarity below threshold trigger refusal: `"I cannot find evidence regarding this in the uploaded project documents."`
- **Verification Steps:**
  - Run: `pytest tests/test_chat_agent.py` covering tests `UT-CHT-01` and `UT-CHT-02`.

---

### Task 9: Complete Dashboard Integration (Sprint 4, Days 1–6)
- **Required Changes:** Scaffold React + TypeScript frontend using Vite. Implement Overview Dashboard (Health Score Dial, 5x5 Risk Heatmap, Overdue Milestones list), Document Hub (drag-and-drop uploader with progress bar), and Conversational Assistant drawer.
- **Relevant Existing Files:** `Unit_Test_Plan_Milestone1.xlsx` (Test cases `UT-DSH-01` to `UT-DSH-02`).
- **New Files Needed:**
  - `frontend/package.json`
  - `frontend/src/App.tsx`
  - `frontend/src/components/HealthScoreDial.tsx`
  - `frontend/src/components/RiskMatrixHeatmap.tsx`
  - `frontend/src/components/DocumentUploader.tsx`
  - `frontend/src/components/ChatDrawer.tsx`
  - `frontend/src/services/api.ts`
- **Dependencies:** Tasks 1 through 8.
- **Acceptance Criteria:**
  - Health dial renders dynamically in green (80-100), amber (60-79), or red (<60).
  - Risk heatmap plots items on $5 \times 5$ matrix with clickable item drawers.
  - Chat drawer streams answers with interactive citation badges.
  - Upload errors display clean alert banners with retry buttons.
- **Verification Steps:**
  - Run: `npm run build` in `frontend/` -> Production build succeeds with 0 errors.
  - Run: `npm test` in `frontend/` -> Component tests pass.

---

### Task 10: End-to-End Testing & Deployment Preparation (Sprint 4, Days 7–10)
- **Required Changes:** Author end-to-end integration test suite exercising the complete pipeline from document upload to health score calculation and chat Q&A. Create containerization configuration (`docker-compose.yml`) for reproducible evaluation.
- **Relevant Existing Files:** All previous deliverables; `Defect_Tracker_Milestone1.xlsx`.
- **New Files Needed:**
  - `tests/e2e/test_full_pipeline.py`
  - `docker-compose.yml`
  - `Dockerfile.backend`
  - `Dockerfile.frontend`
- **Dependencies:** Tasks 1 through 9.
- **Acceptance Criteria:**
  - Complete workflow executes without manual intervention in under 45 seconds for a 20-page document corpus.
  - All 28 test cases in `Unit_Test_Plan_Milestone1.xlsx` transition from `Not Run` to `Passed`.
  - Zero open Critical or High severity defects in `Defect_Tracker_Milestone1.xlsx`.
- **Verification Steps:**
  - Run: `pytest tests/e2e/` -> 100% passing tests.
  - Run: `docker-compose up --build` -> Both backend and frontend services boot cleanly.
