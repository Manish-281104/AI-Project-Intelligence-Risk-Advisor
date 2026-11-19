# AI Project Intelligence & Risk Advisor

An evidence-grounded AI platform that ingests unstructured project documents (PDF, DOCX, CSV, TXT), extracts verifiable scope, risks, and blockers, synthesizes structured Agile documentation, calculates deterministic project health scores, and answers natural language project queries with coordinate citations.

**Version:** `0.3.0 (Milestone 3)`  
**Milestone 3 Planned End Date:** 6 November 2026  
**Test Suite:** 47 passing pytest tests (100% pass rate)

---

## Features

### 1. Multi-Format Ingestion & Boundary-Aware Chunking (Milestones 1 & 2)
- Upload `.pdf`, `.docx`, `.csv`, and `.txt` files with independent batch processing and per-file validation.
- RapidOCR (ONNX Runtime) fallback pipeline for scanned image-only PDFs with blank page filtering.
- Boundary-aware chunking preserving exact structural coordinates (`Page`, `Row`, `Paragraph`).
- Persistent workspace grouping preventing cross-project context bleed (HTTP 409 conflict detection).

### 2. Autonomous Multi-Agent Advisory (Milestone 2)
- **Scope & Deliverable Extraction Agent:** Identifies project goals, scope boundaries, deliverables, milestones, deadlines, and dependencies.
- **Risk Detection & Delivery Forecasting Agent:** Detects schedule slips via deterministic deadline deltas, identifies dependency bottlenecks, and evaluates qualitative risk via a 5x5 matrix.
- **Blocker & Action Item Identification Agent:** Extracts unresolved blockers, action items, and pending decisions with strict `UNKNOWN` fallbacks for missing owners or dates.

### 3. Documentation Generation Studio (Milestone 3)
- **Agile User Stories:** Synthesizes standard Agile stories (`As a [user], I want [feature], so that [benefit]`) with measurable **Given–When–Then** acceptance criteria.
- **Structured Risk Register:** Categorizes risks into Likelihood and Severity matrices, separating documented mitigations from `[AI Recommendation]` strategies.
- **Action Items Register:** Consolidates actionable tasks with assignees and due dates.
- **Review & Approval Workflow:** Interactive `Draft`, `Approved`, and `Rejected` review status toggles.
- **RFC 4180 CSV Exports:** Dedicated downloads for user stories, risk register, and action items.

### 4. Deterministic Project Health Scoring Engine (Milestone 3)
- **Explainable Mathematical Formula (0–100 Scale):**
  $$\text{Health Score} = (\text{Scope Clarity} \times 35\%) + (\text{Timeline Health} \times 35\%) + (\text{Blocker Health} \times 30\%)$$
- **Zero Hallucination:** Computes penalties strictly from extracted evidence without synthetic or guessed numbers.
- **Missing Information Warnings:** Displays actionable alerts when documents lack required schedule or risk data.
- **Snapshot History:** Automatically persists immutable historical snapshots to `backend/data/health_history.json`.

### 5. Conversational Project Intelligence Assistant (Milestone 3)
- **Grounded Q&A:** Answers natural language project queries about status, risks, blockers, assignees, and health.
- **Coordinate Citation Provenance:** Every response provides clickable citation pills indicating source document filename, page number, row number, and verbatim excerpt.
- **Contextual Suggestions:** Generates dynamic follow-up chips tailored to the active discussion.
- **Strict Anti-Hallucination Fallback:** If a question lacks document evidence, the assistant strictly responds:
  *"I couldn't find enough information in the uploaded project documents to answer this question."*
- **Project Isolation:** Conversation threads are isolated per workspace and can be reset cleanly via `POST/DELETE /api/assistant/clear`.

---

## Technologies Used

* **Frontend:** React 18, TypeScript, Vite 5, Lucide React icons, Custom CSS design system.
* **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic v2.
* **AI & Retrieval:** Sentence Transformers / TF-IDF Semantic Retriever, RapidOCR (ONNX Runtime).
* **Testing:** Pytest, AnyIO, FastAPI TestClient.

---

## Installation & Setup

### Prerequisites
- Python 3.10 or later
- Node.js 18 or later
- npm

### 1. Clone the Repository
```bash
git clone https://github.com/Manish-281104/AI-Project-Intelligence-Risk-Advisor.git
cd AI-Project-Intelligence-Risk-Advisor
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The interactive Swagger API documentation is available at: `http://127.0.0.1:8000/docs`

### 3. Frontend Setup
In a new terminal window:
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```

Open your browser at: `http://localhost:5173`

---

## Testing & Validation

### Automated Backend Tests (47 Passing Tests)
```bash
cd backend
python -m pytest tests -v
```

### Standalone End-to-End CLI Verification
```bash
# Milestone 2 Validation:
python validate_milestone2.py

# Milestone 3 Validation (DocGen, Health Scoring & Conversational Assistant):
python validate_milestone3.py
```

### Frontend Production Build
```bash
cd frontend
npm run build
```

---

## Authoritative Project Milestones

* **Milestone 1 (10–14 October 2026):** Foundation, Ingestion Scaffolding & Multi-Format Parsing.
* **Milestone 2 (24–31 October 2026):** Multi-Agent Intelligence (Scope, Risk, Blocker), Scanned PDF OCR & Dynamic Workspace Isolation.
* **Milestone 3 (01–06 November 2026):** Documentation Generation Studio, Deterministic Health Scoring Engine & Conversational Project Intelligence Assistant.

---

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.