# AI Project Intelligence & Risk Advisor

An evidence-grounded AI platform that analyzes project documents, extracts scope, risks, blockers and action items, generates structured Agile documentation, calculates project health scores, and answers project-related questions using uploaded documents.

**Version:** `0.3.0 (Milestone 3)`  
**Milestone 3 Planned End Date:** 6 November 2026  
**Backend Tests:** 47 passing pytest tests (100% pass rate)

---

## 1. Features

### 1.1 Multi-Format Document Ingestion

- Upload PDF, DOCX, CSV and TXT files with batch processing and individual file validation.
- RapidOCR (ONNX Runtime) fallback for scanned image-based PDFs.
- Boundary-aware text chunking that preserves source coordinates such as Page, Row and Paragraph.
- Persistent workspace grouping to prevent information from different projects from mixing.
- HTTP 409 conflict detection for workspace isolation.

### 1.2 Multi-Agent Project Analysis

**Scope & Deliverable Extraction Agent**
- Identifies project goals and objectives.
- Extracts scope boundaries, deliverables and milestones.
- Identifies deadlines and dependencies.

**Risk Detection & Delivery Forecasting Agent**
- Detects schedule delays using deadline comparisons.
- Identifies dependency bottlenecks.
- Evaluates risks using a 5×5 likelihood and severity matrix.

**Blocker & Action Item Identification Agent**
- Extracts unresolved blockers and pending decisions.
- Identifies action items, owners and deadlines.
- Uses `UNKNOWN` when required information is not available in the documents.

### 1.3 Documentation Generation Studio

- Generates Agile user stories using the standard user story format.
- Creates measurable Given–When–Then acceptance criteria.
- Generates structured risk registers.
- Consolidates action items with owners and due dates.
- Supports Draft, Approved and Rejected review statuses.
- Exports user stories, risks and action items as CSV files.

### 1.4 Deterministic Project Health Scoring

Calculates an overall project health score on a scale of 0–100.

**Health Score Formula:**

Health Score = (Scope Clarity × 35%) + (Timeline Health × 35%) + (Blocker Health × 30%)

- Provides dimension-wise health scores.
- Calculates penalties using extracted project evidence.
- Displays warnings when important project information is missing.
- Maintains historical health score snapshots in `backend/data/health_history.json`.

### 1.5 Conversational Project Intelligence Assistant

- Answers natural language questions about project progress, risks, blockers, responsibilities and deliverables.
- Retrieves relevant information from uploaded project documents.
- Provides clickable citations with source filenames, page numbers, row numbers and supporting excerpts.
- Generates contextual follow-up suggestions.
- Separates documented evidence from AI recommendations.
- Uses a strict fallback response when supporting evidence is unavailable.
- Maintains conversation isolation between project workspaces.

---

## 2. Project Structure

The application is divided into two main parts: the React frontend and the FastAPI backend.

```text
AI-Project-Intelligence-Risk-Advisor/
│
├── frontend/
│   ├── public/
│   │
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── ...
│   │
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │
│   │   ├── services/
│   │   │
│   │   ├── models/
│   │   │
│   │   └── ...
│   │
│   ├── tests/
│   ├── uploads/
│   ├── data/
│   └── requirements.txt
│
├── Documents/
├── final_docs/
│
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

*Note: This is a logical overview. The exact source folder names should match the actual repository.*

### Frontend (`frontend/`)

The frontend provides the user interface and communicates with the backend through API requests.

- **public/** – Static assets used by the application.
- **src/components/** – Reusable interface components such as navigation, cards, tables and dialogs.
- **src/pages/** – Individual application pages for document upload, project analysis, documentation generation, health monitoring and conversational assistance.
- **src/services/** – API communication and backend request handling.
- **src/hooks/** – Reusable React hooks.
- **src/types/** – TypeScript interfaces and type definitions.

### Backend (`backend/`)

The backend handles document processing, AI analysis, data management and API operations.

- **app/api/** – FastAPI routes that receive frontend requests and return responses.
- **app/services/** – Core processing logic, document ingestion, retrieval, AI agents, health scoring and conversational assistant functionality.
- **app/models/** – Data models and schemas used for validation and structured responses.
- **tests/** – Automated backend tests.
- **uploads/** – Local storage for uploaded project documents.
- **data/** – Application-generated data such as health history.

### Project Documentation

- **Documents/** – Project development and milestone-related documents.
- **final_docs/** – Final project documentation and submission materials.

---

## 3. System Architecture and Working Flow

The application follows a frontend-backend architecture. The frontend handles user interaction, while the backend performs document processing, retrieval, analysis and response generation.

### Overall Workflow

```text
             USER
               |
               v
       REACT FRONTEND
               |
               v
       FASTAPI BACKEND
               |
               v
      DOCUMENT UPLOAD
               |
               v
       FILE VALIDATION
               |
               v
     DOCUMENT EXTRACTION
      PDF / DOCX / CSV / TXT
               |
               v
       OCR IF REQUIRED
               |
               v
      TEXT CHUNKING
   Page / Row / Paragraph
               |
               v
    EMBEDDING & INDEXING
               |
               v
       KNOWLEDGE BASE
               |
       +-------+-------+
       |       |       |
       v       v       v
     SCOPE   RISK   BLOCKER
     AGENT   AGENT   AGENT
       |       |       |
       +-------+-------+
               |
               v
       STRUCTURED RESULTS
               |
       +-------+-------+
       |       |       |
       v       v       v
   DOCUMENT  HEALTH  PROJECT
   GENERATION SCORING INSIGHTS
               |
               v
       CONVERSATIONAL
         ASSISTANT
               |
               v
      RETRIEVAL + GROUNDED
           ANSWERING
               |
               v
       CITATIONS & RESULTS
               |
               v
         REACT FRONTEND
```

### Step 1: Document Upload

Users upload project-related documents through the frontend.

The backend validates the uploaded files, checks their formats and processes each document independently.

### Step 2: Document Extraction

The ingestion module extracts text from different file formats.

- PDF files are processed using PDF text extraction.
- Scanned PDFs use RapidOCR when normal text extraction is insufficient.
- DOCX files are processed to extract paragraphs and tables.
- CSV files are processed while preserving row information.
- TXT files are read as plain text.

### Step 3: Chunking and Knowledge Base Construction

Extracted text is divided into smaller chunks.

Each chunk maintains source information such as:

- Document filename.
- Page number.
- Row number.
- Paragraph reference.

The chunks are converted into representations suitable for semantic retrieval and stored in the project's knowledge base.

This allows the system to retrieve relevant information without repeatedly processing the entire document collection.

### Step 4: Multi-Agent Analysis

The retrieved project information is processed by specialized agents.

| Agent | Responsibility | Output |
|---|---|---|
| Scope Agent | Extracts project scope and deliverables | Goals, requirements, milestones |
| Risk Agent | Identifies project and schedule risks | Risk register and delivery risks |
| Blocker Agent | Identifies blockers and tasks | Blockers, owners and action items |

The agents produce structured results supported by the uploaded documents.

### Step 5: Documentation Generation

The Documentation Generation module uses the extracted project information to generate:

- Agile user stories.
- Acceptance criteria.
- Risk registers.
- Action item registers.

Users can review the generated information and update its approval status.

### Step 6: Project Health Scoring

The health scoring engine calculates three separate dimensions:

1. Scope Clarity – evaluates how clearly the project scope and requirements are documented.
2. Timeline Health – evaluates schedule progress and deadline-related risks.
3. Blocker Health – evaluates the impact of unresolved blockers.

The three dimensions are combined using the weighted health score formula.

The resulting score and its breakdown are displayed in the frontend.

### Step 7: Conversational Project Assistant

Users can ask questions such as:

- Are we on track?
- What are our biggest risks?
- Who is responsible for this task?
- What deliverables are pending?
- What are the current blockers?

The assistant retrieves relevant project information, generates an answer based on supporting evidence and provides source citations.

If sufficient evidence is unavailable, the assistant informs the user instead of inventing an answer.

### Step 8: Results and Visualization

The frontend displays the processed information through project dashboards, tables, health indicators, documentation views and conversational responses.

This allows users to understand project progress and identify issues using information extracted from their own documents.

---

## 4. Technologies Used

| Category | Technologies |
|---|---|
| Frontend | React 18, TypeScript, Vite 5 |
| Backend | Python 3.10+, FastAPI, Uvicorn |
| Data Validation | Pydantic v2 |
| AI & Retrieval | Sentence Transformers, TF-IDF Semantic Retriever |
| OCR | RapidOCR, ONNX Runtime |
| UI | Lucide React, Custom CSS |
| Testing | Pytest, AnyIO, FastAPI TestClient |

---

## 5. Installation & Setup

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
```

Activate the environment.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend API: http://127.0.0.1:8000

Swagger API documentation: http://127.0.0.1:8000/docs

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend

npm install

npm run dev
```

Open the application:

http://localhost:5173

---

## 6. Testing & Validation

### Backend Automated Tests

```bash
cd backend

python -m pytest tests -v
```

The current recorded test result is 47 passing tests.

### Frontend Production Build

```bash
cd frontend

npm run build
```

---

## 7. Project Milestones

**Milestone 1 (10–14 October 2026)**

Foundation, document ingestion, multi-format parsing and knowledge base construction.

**Milestone 2 (24–31 October 2026)**

Multi-agent intelligence covering scope extraction, risk detection, blocker identification, scanned PDF OCR and workspace isolation.

**Milestone 3 (01–06 November 2026)**

Documentation Generation Studio, deterministic project health scoring and conversational project intelligence assistant.

---

## 8. License

This project is licensed under the MIT License. See the `LICENSE` file for details.
