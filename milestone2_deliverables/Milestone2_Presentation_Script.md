# Milestone 2 Presentation Script: AI Project Intelligence & Risk Advisor

**Project Title:** AI Project Intelligence & Risk Advisor  
**Review Stage:** Milestone 2 (Autonomous Multi-Agent Intelligence, Multi-Format Ingestion & RAG)  
**Presenter:** Manish (Department of Computer Science & Engineering)  
**Milestone 2 Completion Date:** 31 October 2026  
**Target Duration:** 12 – 15 Minutes  
**Accompanying Slide Deck:** `milestone2_deliverables/Milestone2_Presentation.pptx` (15 Slides)

---

## Slide 1: Title Slide
- **Slide Title:** AI Project Intelligence & Risk Advisor — Milestone 2 Review
- **Visuals on Slide:** Dark slate theme, project title, subtitle (Autonomous Multi-Agent Intelligence, Multi-Format Ingestion & RAG), academic details, date (31 October 2026).
- **Presenter Spoken Script:**
  > "Respected faculty evaluators, internal committee members, and fellow students: Good morning. My name is Manish, and I am presenting the Milestone 2 review for my final-year B.Tech major project: **AI Project Intelligence & Risk Advisor**, concluded on **31 October 2026**.
  >
  > In our Milestone 1 review on October 14, we established our architectural foundation, Agile backlog, and quality assurance framework. Over the past two weeks during Sprint 2, our team transitioned from blueprints into fully operational, verified software.
  >
  > Today, I am proud to demonstrate our completed Milestone 2 deliverables: an end-to-end multi-format ingestion pipeline with local RapidOCR fallback, dynamic project identity resolution with zero cross-bleed, three autonomous reasoning agents (Scope, Risk, and Blocker), an interactive React 18 dashboard, and a 100% passing automated test suite of 35 unit and integration tests."

---

## Slide 2: Milestone 2 Executive Summary & Verification Highlights
- **Slide Title:** Milestone 2 Executive Summary & Verification Highlights
- **Visuals on Slide:** 4 structured summary cards: Autonomous Multi-Agent Core, Multi-Format Ingestion & OCR, Dynamic Identity & Zero Bleed, 100% Verified Quality Assurance.
- **Presenter Spoken Script:**
  > "To provide an executive overview of what has been built and verified in Milestone 2:
  >
  > First, we developed our autonomous multi-agent reasoning core. Three specialized agents—the Scope Agent, Risk Detection Agent, and Blocker Identification Agent—operate concurrently and expose dedicated REST endpoints alongside a unified orchestrator at `/api/agents/analyze-all`.
  >
  > Second, we implemented multi-format document parsing across PDF, DOCX, CSV with automatic delimiter sniffing, and UTF-8 TXT files, backed by an on-device RapidOCR fallback engine for scanned, non-selectable PDF prints.
  >
  > Third, we solved dynamic project identity resolution. The application detects the true project name and objectives directly from document metadata without hardcoded domain bias, enforcing strict workspace isolation with HTTP 409 cross-project conflict handling.
  >
  > Fourth, every capability is verified: 35 out of 35 automated pytest tests pass in 5.71 seconds, 11 documented defects have been resolved and closed, and the frontend Vite bundle builds cleanly in 2.25 seconds."

---

## Slide 3: Evolution: Milestone 1 (Oct 14) vs Milestone 2 (Oct 31)
- **Slide Title:** Evolution: Milestone 1 (Oct 14) vs Milestone 2 (Oct 31)
- **Visuals on Slide:** Side-by-side comparison table contrasting Milestone 1 planning baseline with Milestone 2 working reality.
- **Presenter Spoken Script:**
  > "This slide illustrates our verified engineering progress between our initial Milestone 1 audit on October 14 and our Milestone 2 completion today, October 31.
  >
  > In Milestone 1, our workspace contained initial planning documents and single-file extraction prototypes. Pytest discovered 0 tests, no multi-agent workflows existed, and scanned image-only PDFs failed extraction.
  >
  > Over Sprint 2, we resolved 11 verified engineering defects. Today, we have multi-file batch upload with a staging queue, local OCR fallback, a persistent vector store, three autonomous agents with strict anti-hallucination guardrails, and 35 passing automated tests. We have strictly adhered to scientific verification—every claim in our documentation corresponds to working code and reproducible test executions."

---

## Slide 4: Milestone 2 Verified System Architecture
- **Slide Title:** Milestone 2 Verified System Architecture
- **Visuals on Slide:** 5 architectural layers: Presentation (React + Vite), API & Routing (FastAPI), Extraction & OCR Engine (PyMuPDF, RapidOCR, docx, csv), Multi-Agent Core, and Isolated Persistence Storage.
- **Presenter Spoken Script:**
  > "Here we see the architectural data flow of our platform:
  >
  > At the Presentation layer, users interact with a responsive React 18 SPA built with TypeScript and Vite. It provides an intuitive drag-and-drop dropzone, multi-file staging queue, chunk coordinate viewer, and tabbed AI advisory views.
  >
  > The frontend communicates with our FastAPI backend microservice via structured REST endpoints. Incoming documents enter our Ingestion Engine, where format-specific parsers extract structured text. If a PDF contains image-only scans, our RapidOCR ONNX pipeline activates seamlessly.
  >
  > Extracted text is split into boundary-aware chunks and indexed into a persistent vector store tagged with the active workspace `project_id`. Downstream, our Scope, Risk, and Blocker agents query this grounded knowledge base to synthesize project intelligence with exact sentence citations."

---

## Slide 5: Multi-Format Ingestion & Scanned PDF OCR Fallback Pipeline
- **Slide Title:** Multi-Format Ingestion & Scanned PDF OCR Fallback Pipeline
- **Visuals on Slide:** 4 capability cards: Native PDF extraction, Scanned PDF OCR fallback, DOCX & CSV parsing, Batch ingestion & validation.
- **Presenter Spoken Script:**
  > "A core engineering achievement of Milestone 2 is our resilient document extraction pipeline:
  >
  > For native digital PDFs, PyMuPDF extracts text streams with per-page tracking. However, in real-world project governance, teams frequently encounter scanned contracts or non-selectable prints. In Milestone 1, these produced 'Document contains no extractable text' errors.
  >
  > In Milestone 2, we integrated RapidOCR using local ONNX Runtime CPU execution. If extracted text falls below 60 characters, the system renders the page to a 200 DPI bitmap and invokes local OCR. Pages that are genuinely blank are detected and filtered, while text-containing scanned pages are extracted with page coordinates.
  >
  > For tabular data, our CSV parser automatically sniffs delimiters—whether comma, semicolon, tab, or pipe—and preserves row coordinates without flattening records."

---

## Slide 6: Dynamic Project Identity & Zero Cross-Bleed Isolation
- **Slide Title:** Dynamic Project Identity & Zero Cross-Bleed Isolation
- **Visuals on Slide:** Two comparative panels detailing Dynamic Project Identity Resolution and Cross-Project Conflict Isolation (HTTP 409).
- **Presenter Spoken Script:**
  > "A fatal flaw in naive generative AI applications is context bleed—where findings from a previous project bleed into another project's analysis.
  >
  > In our platform, project identity is completely dynamic. The system extracts the true project name and primary goals from Section 1 Overview metadata. It supports any project domain—we have rigorously tested it across Campus Event Management, Hospital ICU Management, Community Library Management, and E-Commerce systems.
  >
  > Furthermore, if a user uploads a document explicitly belonging to a different project into an established workspace, the backend raises an HTTP 409 Conflict error. The user is presented with a 1-click option to archive the current workspace and initialize a clean, isolated project workspace. Our regression test `test_dynamic_project_switching_and_zero_bleed` confirms 0% token contamination across domains."

---

## Slide 7: Agent 1: Scope & Deliverable Extraction Agent
- **Slide Title:** Agent 1: Scope & Deliverable Extraction Agent
- **Visuals on Slide:** Panels covering Core Extraction Capabilities and Anti-Hallucination & Provenance Rigor.
- **Presenter Spoken Script:**
  > "Now let us examine our three autonomous agents, beginning with the Scope and Deliverable Extraction Agent:
  >
  > The Scope Agent extracts one overarching Primary Project Goal and up to five structured supporting Sub-Goals. It demarcates In-Scope requirements from Out-of-Scope boundaries, extracting discrete deliverables, milestone schedules, and task dependencies.
  >
  > Most importantly, the agent enforces a strict anti-hallucination standard: whenever a source document omits an owner or target deadline, the agent maps the attribute strictly to 'UNKNOWN' and logs the omission in `missing_information`. It never invents placeholder names or fictitious dates. Every deliverable includes exact document and coordinate citations."

---

## Slide 8: Agent 2: Risk Detection & Delivery Forecasting Agent
- **Slide Title:** Agent 2: Risk Detection & Delivery Forecasting Agent
- **Visuals on Slide:** 4 cards: Deterministic Schedule Engine, 5x5 Qualitative Severity Matrix, Evidence vs Recommendation Separation, Honest Delivery Forecasting.
- **Presenter Spoken Script:**
  > "Our second agent is the Risk Detection and Delivery Forecasting Agent:
  >
  > It operates via a dual-engine architecture:
  > First, a deterministic schedule difference calculator compares milestone deadlines against the project reference date, flagging overdue milestones with exact calendar day deltas.
  > Second, an entity extraction engine maps qualitative delivery risks (such as resource bottlenecks and external dependencies) onto a standardized 5x5 severity matrix.
  >
  > A crucial governance rule is our strict boundary between document evidence and AI recommendations: the `supporting_evidence` field contains only verbatim quotes from uploaded documents, while recommended mitigations are explicitly prefixed with `[AI Recommendation]`. The agent discloses full methodology and refuses to fabricate synthetic burndown charts when historical velocity data is absent."

---

## Slide 9: Agent 3: Blocker & Action Item Identification Agent
- **Slide Title:** Agent 3: Blocker & Action Item Identification Agent
- **Visuals on Slide:** Operational Impediment Extraction paired with Anti-Hallucination & Cross-Document Deduplication.
- **Presenter Spoken Script:**
  > "Our third agent is the Blocker and Action Item Identification Agent:
  >
  > It continuously scans meeting minutes, status reports, and sprint tasks to extract active blockers, unresolved impediments, action items, and pending decisions requiring stakeholder approval.
  >
  > When action items lack explicit assignees, the agent assigns the owner strictly to 'UNKNOWN' and increments `unassigned_count`. When identical impediments are mentioned across both meeting minutes and a project charter, the agent performs cross-document deduplication, consolidating the findings into a single record with combined citations."

---

## Slide 10: RAG Pipeline & Traceable Evidence Grounding
- **Slide Title:** RAG Pipeline & Traceable Evidence Grounding
- **Visuals on Slide:** 4 RAG workflow cards: Boundary-Aware Chunking, Vector Space & TF-IDF Cosine Ranking, Project Workspace Isolation, Sentence-Level Citations.
- **Presenter Spoken Script:**
  > "Our Retrieval-Augmented Generation pipeline is engineered specifically for software governance:
  >
  > Documents are split into 500-character target chunks with 100-character overlap along natural sentence boundaries. Chunks retain structural coordinates—such as 'Page 2' or 'Row 1-5'—so that tabular relationships are never lost.
  >
  > Chunks are indexed into a persistent JSON catalog and queried using TF-IDF cosine vector similarity. This provides fast, deterministic retrieval without requiring native C++ compilers on Windows Python 3.13. All retrieval queries strictly filter by `project_id`, preventing any data leakage across projects."

---

## Slide 11: Production Frontend Interface (React + TypeScript + Vite)
- **Slide Title:** Production Frontend Interface (React + TypeScript + Vite)
- **Visuals on Slide:** 4 feature cards: Multi-File Staging Dropzone, Per-File Status, Extracted Chunk Viewer, Tabbed AI Advisory View.
- **Presenter Spoken Script:**
  > "The frontend dashboard provides a streamlined, production-grade user experience:
  >
  > Users can drag and drop multiple files into the ingestion lab. The staging list displays format badges, formatted file sizes, and individual remove buttons before initiating upload.
  >
  > Upload progress is tracked per file. In mixed valid and invalid batches, valid documents process successfully with HTTP 201 while invalid files display clear error badges.
  >
  > An Extracted Chunk Viewer allows users to inspect raw chunks, copy snippets, and check coordinate provenance. Finally, the tabbed `AgentAnalysisView` presents Scope, Risks, and Blockers with summary metric pills, severity badges, verbatim quote cards, and type filters."

---

## Slide 12: Quality Assurance & Verified Defect Management (11/11 Closed)
- **Slide Title:** Quality Assurance & Verified Defect Management (11/11 Closed)
- **Visuals on Slide:** Comprehensive defect summary table detailing Defects 1 through 11, defect types, resolutions, and Closed statuses.
- **Presenter Spoken Script:**
  > "In accordance with disciplined software engineering practices, we tracked all defects in our `Defect_Tracker_Milestone2.xlsx` workbook.
  >
  > Across Sprints 1 and 2, we logged 11 genuine defects:
  > - Defects 1 and 2 addressed frontend styling and chunk visibility.
  > - Defects 3 and 4 introduced multi-file batch upload and catalog persistence.
  > - Defect 5 enforced strict anti-hallucination UNKNOWN mappings.
  > - Defect 6 resolved blank PDF handling.
  > - Defects 7 and 8 implemented persistent workspace grouping and HTTP 409 conflict detection.
  > - Defect 9 resolved section goal priority on benchmark documents.
  > - Defect 10 integrated RapidOCR for scanned PDFs.
  > - Defect 11 resolved cross-project context bleed.
  >
  > All 11 defects have been retested, verified, and officially Closed."

---

## Slide 13: Automated Test Execution & Verification Evidence
- **Slide Title:** Automated Test Execution & Verification Evidence
- **Visuals on Slide:** 4 test module breakdown cards summarizing 35 passed tests with execution times.
- **Presenter Spoken Script:**
  > "To verify application stability, we developed a comprehensive automated test suite in pytest:
  >
  > - `test_api.py`: 10 tests verifying server health, module registry, multi-format upload endpoints, and input rejection.
  > - `test_chunking.py`: 8 tests verifying boundary-aware chunking, overlap, table preservation, and blank page rejection.
  > - `test_milestone2_agents.py`: 10 tests verifying batch upload, partial batch success, document deletion, Scope Agent, Risk Agent, and Blocker Agent.
  > - `test_project_grouping_and_consistency.py`: 2 tests verifying persistent workspace IDs and generic file inheritance.
  > - `test_sample_document_validation.py`: 1 test verifying all 10 ground-truth criteria.
  > - `test_milestone2_comprehensive_validation.py`: 3 tests verifying OCR fallback, dynamic switching, and CSV delimiters.
  > - `test_library_management_validation.py`: 1 test validating full domain shift.
  >
  > Total: 35 tests, 100% pass rate in 5.71 seconds. Frontend build compiles cleanly in 2.25 seconds."

---

## Slide 14: Milestone 2 Ground Truth Benchmark Demonstration
- **Slide Title:** Milestone 2 Ground Truth Benchmark Demonstration
- **Visuals on Slide:** Complete checklist of the 10/10 acceptance criteria validated against `AI_Project_Agent_Test_Sample_Document.docx`.
- **Presenter Spoken Script:**
  > "To demonstrate extraction accuracy, we validated our multi-agent pipeline against our standardized benchmark test document `AI_Project_Agent_Test_Sample_Document.docx`.
  >
  > All 10 ground-truth criteria were achieved with 100% fidelity:
  > 1. Primary Goal extracted from Section 1 Overview, excluding dependency codes.
  > 2. Five structured supporting Sub-Goals extracted with clear scope boundaries.
  > 3. Exactly 6 deliverables extracted with source citations.
  > 4. Exactly 6 milestones identified with completion dates.
  > 5. Exactly 3 documented project risks captured with Likelihood and Impact ratings.
  > 6. Active server provisioning blocker detected with resolution action steps.
  > 7. Exactly 5 action items extracted with owners and deadlines.
  > 8. Approved decisions and 1 pending decision identified.
  > 9. Unassigned count evaluated strictly against action items equals zero.
  > 10. Overdue count relative to reporting date equals zero.
  > Zero hallucination, exact evidence quotes, and 100% reproducible results."

---

## Slide 15: Milestone 2 Conclusion & Milestone 3 Roadmap
- **Slide Title:** Milestone 2 Conclusion & Milestone 3 Roadmap
- **Visuals on Slide:** Two panels: Completed Milestone 2 Deliverables (concluded 31 Oct 2026) paired with the upcoming Milestone 3 Planned Scope.
- **Presenter Spoken Script:**
  > "In conclusion, Milestone 2 successfully achieves all planned core engineering goals on our authoritative completion date of **31 October 2026**.
  >
  > We have delivered a working, tested, multi-agent AI project intelligence advisor with multi-format ingestion, OCR fallback, workspace isolation, and an interactive dashboard.
  >
  > Looking ahead to Milestone 3, our remaining roadmap encompasses:
  > 1. Module 6: Documentation Generation Agent to synthesize Gherkin user stories, risk registers, and executive briefs.
  > 2. Module 7: Composite Project Health Scoring Engine using a transparent 0-to-100 mathematical formula.
  > 3. Module 8: Grounded Conversational Assistant providing interactive natural language Q&A with clickable citation badges.
  >
  > All deliverables, workbooks, defect logs, test plans, and code are committed and organized. Thank you for your time, and I look forward to your questions and evaluation."
