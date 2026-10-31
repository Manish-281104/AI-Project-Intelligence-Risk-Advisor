# AI Project Intelligence & Risk Advisor

An AI-powered application that helps teams understand project documents, track risks, identify blockers, and monitor project progress.

## Features

- Upload PDF, DOCX, CSV, and TXT files.
- Extract information from scanned PDFs using OCR.
- Identify project goals, scope, and deliverables.
- Detect project risks and dependencies.
- Identify blockers, pending decisions, and action items.
- Maintain separate workspaces for different projects.
- View analysis results through an interactive dashboard.
- Get evidence-based results from uploaded documents.

## Technologies Used

**Frontend:** React, TypeScript, Vite

**Backend:** Python, FastAPI

**AI & Data Processing:** RAG, Sentence Transformers, ChromaDB, RapidOCR

## Requirements

- Python 3.10 or later
- Node.js 18 or later
- npm

## Installation

Clone the repository:

```bash
git clone https://github.com/Manish-281104/AI-Project-Intelligence-Risk-Advisor.git
cd AI-Project-Intelligence-Risk-Advisor
```

### Backend Setup

```bash
cd backend

python -m venv .venv
```

Activate the environment on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the application at:

http://localhost:5173

## API Documentation

Once the backend is running, access:

http://127.0.0.1:8000/docs

## Supported File Formats

- PDF
- DOCX
- CSV
- TXT

## Testing

Run backend tests:

```bash
cd backend
python -m pytest tests -v
```

Build the frontend:

```bash
cd frontend
npm run build
```

## Future Improvements

- Project health score.
- Automated project report generation.
- Conversational AI assistant.