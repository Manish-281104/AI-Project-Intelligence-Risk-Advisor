# Milestone 1 Repository Audit: AI Project Intelligence & Risk Advisor

**Audit Date:** October 14, 2026  
**Project Title:** AI Project Intelligence & Risk Advisor  
**Repository Location:** `C:\Users\manis\Desktop\SP`  
**Audit Type:** Physical Codebase Inspection & Verification (Milestone 1 Implementation Phase)  
**Evaluation Standard:** Physical Codebase Evidence (Strict Anti-Hallucination)

---

## 1. Executive Summary

This repository audit documents the physical codebase located at `C:\Users\manis\Desktop\SP` following the completion of Milestone 1 development (representing approximately 3–4 days of initial engineering). 

In accordance with strict academic integrity rules, this report documents only what is physically present and verified on disk, distinguishing working source code from upcoming planned architecture.

### Key Audit Findings
1. **Repository State:** The workspace contains fully configured and verified `backend/` and `frontend/` directories containing runnable source code, configuration files, test suites, and production build assets.
2. **Backend API (FastAPI):** Operational FastAPI application (`backend/app/main.py`) providing:
   - `GET /api/health`: Health monitoring and honest pipeline readiness reporting.
   - `GET /api/modules`: Dynamic registry of all 9 project modules with current status metadata.
   - `POST /api/documents/upload`: Ingestion pipeline validating MIME types, enforcing size limits (< 15 MB), rejecting malformed/unsupported files, extracting structural text (PDF, DOCX, CSV, TXT), and storing documents securely in `backend/uploads/`.
3. **Automated Backend Testing:** `backend/tests/test_api.py` contains 10 automated unit and integration tests executed via `pytest`, achieving 100% pass rate.
4. **Frontend Dashboard (React + TypeScript + Vite):** A modern, responsive dashboard (`frontend/src/`) featuring:
   - Live backend health polling and connection status pill in `Navbar.tsx`.
   - Interactive `FileUpload.tsx` supporting PDF, DOCX, CSV, and TXT with instant metadata and text preview.
   - Modular `ModuleCard.tsx` grid displaying the 9 system modules with honest status filtering.
   - 4-phase system workflow architecture visualization.
   - Transparent academic integrity notice regarding upcoming AI/RAG capabilities.
5. **Frontend Build Verification:** Verified via `tsc -b && vite build` with zero TypeScript errors and bundled production assets in `frontend/dist/`.
6. **Project Management Templates:** Project-specific workbooks (`Agile_Template_Milestone1.xlsx`, `Defect_Tracker_Milestone1.xlsx`, `Unit_Test_Plan_Milestone1.xlsx`) preserved in `milestone1_deliverables/`.

---

## 2. Actual Directory Tree

Below is the exhaustive file tree of `C:\Users\manis\Desktop\SP`:

```
C:\Users\manis\Desktop\SP\
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI app, CORS middleware, root & docs routing
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py               # /health, /modules, /documents/upload endpoints
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py               # Settings, environment loader, upload directory
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── project.py              # Pydantic models (Health, Module, Upload, DocumentMetadata)
│   │   └── services/
│   │       ├── __init__.py
│   │       └── document_service.py     # File validation, local storage, PDF/DOCX/CSV/TXT parsers
│   ├── tests/
│   │   └── test_api.py                 # 10 automated pytest unit/integration tests
│   ├── uploads/                        # Designated local document storage (gitignored)
│   ├── pytest.ini                      # Pytest discovery configuration
│   └── requirements.txt                # Pinned dependencies (fastapi, uvicorn, pymupdf, python-docx)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx              # Header with live backend connection indicator
│   │   │   ├── FileUpload.tsx          # Drag-and-drop document upload lab & text preview
│   │   │   └── ModuleCard.tsx          # Module card with status badges & milestone tags
│   │   ├── services/
│   │   │   └── api.ts                  # Reusable API client (health, modules, upload)
│   │   ├── App.tsx                     # Main dashboard layout, workflow cards, integrity notice
│   │   ├── main.tsx                    # React DOM entry point
│   │   ├── index.css                   # Modern dashboard stylesheet
│   │   └── vite-env.d.ts               # Vite TypeScript declarations
│   ├── dist/                           # Verified production build output
│   ├── index.html                      # HTML5 template
│   ├── package.json                    # Node dependencies & scripts
│   ├── tsconfig.json                   # TypeScript configuration
│   └── vite.config.ts                  # Vite bundler configuration
│
├── milestone1_deliverables/            # Project management workbooks & presentation materials
│   ├── Agile_Template_Milestone1.xlsx
│   ├── Defect_Tracker_Milestone1.xlsx
│   ├── Unit_Test_Plan_Milestone1.xlsx
│   ├── Milestone1_Presentation.pptx
│   └── Milestone1_Presentation_Script.md
│
├── .env.example                        # Example non-secret environment variables
├── .gitignore                          # Excludes uploads/, .venv/, node_modules/, dist/
└── README.md                           # Master setup, running instructions & verification guide
```

---

## 3. Important Files and Their Responsibilities

| File Path | Language / Format | Verified Responsibility |
| :--- | :--- | :--- |
| [`backend/app/main.py`](file:///C:/Users/manis/Desktop/SP/backend/app/main.py) | Python (FastAPI) | Application entry point; mounts CORS middleware, routes, and OpenAPI `/docs`. |
| [`backend/app/api/routes.py`](file:///C:/Users/manis/Desktop/SP/backend/app/api/routes.py) | Python (FastAPI) | Exposes `GET /api/health`, `GET /api/modules`, and `POST /api/documents/upload`. Contains central module registry. |
| [`backend/app/services/document_service.py`](file:///C:/Users/manis/Desktop/SP/backend/app/services/document_service.py) | Python | Validates extensions/sizes, checks magic headers, saves files securely, and extracts text using PyMuPDF, python-docx, and CSV parsers. |
| [`backend/app/schemas/project.py`](file:///C:/Users/manis/Desktop/SP/backend/app/schemas/project.py) | Python (Pydantic) | Data contracts for health checks, module items, document metadata, and upload responses. |
| [`backend/app/core/config.py`](file:///C:/Users/manis/Desktop/SP/backend/app/core/config.py) | Python | Centralizes environment variables with sensible development defaults and CORS origins. |
| [`backend/tests/test_api.py`](file:///C:/Users/manis/Desktop/SP/backend/tests/test_api.py) | Python (PyTest) | 10 unit and integration tests covering health, modules, parsers, and negative validation cases. |
| [`frontend/src/services/api.ts`](file:///C:/Users/manis/Desktop/SP/frontend/src/services/api.ts) | TypeScript | Reusable HTTP client communicating with backend using `VITE_API_BASE_URL`. |
| [`frontend/src/components/Navbar.tsx`](file:///C:/Users/manis/Desktop/SP/frontend/src/components/Navbar.tsx) | React / TypeScript | Header bar with real-time backend connection status pill and Swagger link. |
| [`frontend/src/components/FileUpload.tsx`](file:///C:/Users/manis/Desktop/SP/frontend/src/components/FileUpload.tsx) | React / TypeScript | File upload drag-and-drop zone, client validation, metadata grid, and text preview snippet. |
| [`frontend/src/components/ModuleCard.tsx`](file:///C:/Users/manis/Desktop/SP/frontend/src/components/ModuleCard.tsx) | React / TypeScript | Renders each module with category, description, milestone target, and verified status. |
| [`frontend/src/App.tsx`](file:///C:/Users/manis/Desktop/SP/frontend/src/App.tsx) | React / TypeScript | Dashboard layout, hero section, workflow pipeline, integrity notice, and module filters. |
| [`README.md`](file:///C:/Users/manis/Desktop/SP/README.md) | Markdown | Comprehensive running instructions for Windows PowerShell, architecture docs, and troubleshooting. |

---

## 4. Implemented Functionality and Audit Verification

| Functional Area | Claimed / Required Feature | Supporting File Paths | Physical Audit Finding |
| :--- | :--- | :--- | :--- |
| **Backend API** | FastAPI Service with OpenAPI Docs | `backend/app/main.py`, `backend/app/api/routes.py` | **Implemented and Verified (100%)** |
| **Service Health Check** | `GET /api/health` with honest status | `backend/app/api/routes.py` | **Implemented and Verified (100%)** |
| **Module Registry** | `GET /api/modules` listing 9 modules | `backend/app/api/routes.py` | **Implemented and Verified (100%)** |
| **Document Ingestion** | PDF, DOCX, CSV, TXT validation & text parsing | `backend/app/services/document_service.py` | **Implemented and Verified (100%)** |
| **Error Handling** | Rejection of 0-byte, oversized, and invalid formats | `backend/app/services/document_service.py` | **Implemented and Verified (100%)** |
| **Automated Tests** | PyTest test suite (10 test cases) | `backend/tests/test_api.py` | **Implemented and Verified (100% pass)** |
| **Frontend UI** | React + TypeScript + Vite Dashboard | `frontend/src/App.tsx`, `frontend/src/components/` | **Implemented and Verified (100%)** |
| **Connection Indicator** | Real-time backend status pill | `frontend/src/components/Navbar.tsx` | **Implemented and Verified (100%)** |
| **Production Build** | Static bundle generation via Vite | `frontend/dist/` | **Verified (`npm run build` succeeds)** |
| **RAG & Vector DB** | ChromaDB Indexing & Embeddings | None in Milestone 1 | **Planned (Milestone 2 Target)** |
| **Multi-Agent Reasoning** | LangGraph Scope, Risk, & Blocker Agents | None in Milestone 1 | **Planned (Milestone 2 Target)** |
| **Project Health Scoring** | Algorithmic Health Scoring Formula | None in Milestone 1 | **Planned (Milestone 3 Target)** |

---

## 5. Verification Commands Executed and Results

| # | Command Executed | Purpose | Exit Code | Observed Result |
| :- | :--- | :--- | :-: | :--- |
| 1 | `python -m pytest backend -c backend/pytest.ini` | Execute backend test suite | 0 | 10 passed in 0.94s |
| 2 | `npm run build` (in `frontend/`) | Compile TypeScript & build Vite bundle | 0 | Production build generated cleanly |
| 3 | `Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health"` | Live backend health verification | 0 | Status `ok`, storage ready, AI status planned |
| 4 | `Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/modules"` | Live modules endpoint check | 0 | Exactly 9 modules returned with honest statuses |
| 5 | `curl.exe -X POST .../api/documents/upload -F "file=@test.txt"` | Live file upload and parsing verification | 0 | Returned 201 Created, parsed text snippet and metadata |
| 6 | `curl.exe -X POST .../api/documents/upload -F "file=@app.exe"` | Verify invalid format rejection | 0 | Returned 400 Bad Request with format error detail |

---

## 6. Milestone 1 Presentation Evidence: Screenshots Guide

During the academic review, capture or demonstrate the following live artifacts:

1. **Frontend Dashboard Running in Browser (`http://localhost:5173`)**:
   - Showing the hero section, live "Backend Online" green status pill, and 4-phase system architecture workflow cards.
2. **FastAPI Swagger Documentation (`http://127.0.0.1:8000/docs`)**:
   - Showing interactive OpenAPI documentation with `/api/health`, `/api/modules`, and `/api/documents/upload`.
3. **Successful Document Upload Demo**:
   - Showing upload of a sample file in the Document Ingestion Lab with extracted metadata (UUID, word count, character count, and text snippet).
4. **Backend Health Response**:
   - Browser or curl view of `GET /api/health` showing JSON response with honest `ai_pipeline_status: "planned"`.
5. **Module Status Endpoint Response**:
   - Browser or curl view of `GET /api/modules` showing the complete 9-module registry.
6. **Project Structure in VS Code**:
   - VS Code explorer panel showing clean separation of `backend/` and `frontend/`.
7. **Passing PyTest Suite**:
   - Terminal window showing `10 passed in 0.94s` for `python -m pytest tests`.
