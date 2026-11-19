# AI Project Intelligence & Risk Advisor
## Final Project Demonstration Script & Viva Walkthrough

**Target Audience:** Final-Year Project Evaluators, External Examiners, Engineering Leads  
**Project:** AI Project Intelligence & Risk Advisor  
**Milestone:** Milestone 4 Final Release  
**Duration:** Approximately 15–20 minutes  

---

## Demonstration Overview

This practical demonstration script provides a step-by-step walkthrough of the entire **AI Project Intelligence & Risk Advisor** platform. It demonstrates how heterogeneous project documents are ingested, how autonomous agents extract delivery insights, how deterministic project health is calculated, how the executive dashboard visualizes delivery risks, how incremental documents are added without re-indexing, and how the conversational assistant answers complex inquiries while strictly suppressing hallucinations.

---

## Step 1: System Boot & Architecture Walkthrough
**Objective:** Demonstrate system startup, zero-error health check, and system architecture.

### Action
1. Open terminal 1 and start the FastAPI backend:
   ```powershell
   cd backend
   .\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. Open terminal 2 and launch the React frontend:
   ```powershell
   cd frontend
   npm run dev
   ```
3. Open browser at `http://localhost:5173`.

### Spoken Explanation
> *"Welcome to the final demonstration of our B.Tech project, the AI Project Intelligence & Risk Advisor. The system consists of a FastAPI asynchronous backend in Python and a React + TypeScript frontend built with Vite. Notice the header bar: it dynamically connects to our FastAPI health endpoint, displaying 'Backend Connected' with latency telemetry. In the hero section, we see our operational status: 4 autonomous agents, 100% deterministic mathematical health scoring, and multi-format document ingestion across PDF, DOCX, CSV, and TXT."*

---

## Step 2: Fresh Workspace Initialization & Empty State
**Objective:** Demonstrate clean workspace boundaries and safe empty states.

### Action
1. Navigate to the **Project Dashboard** tab.
2. Observe the empty dashboard prompt: *"No Project Documents Uploaded Yet"*.
3. Note that the dashboard gracefully renders zero metrics rather than mock data or an application crash.
4. Click on **Document Ingestion** in the top navigation.
5. In the Project Workspace card, click **Start New Project** and enter `Apex ERP Modernization`.

### Spoken Explanation
> *"We begin in an isolated project workspace named 'Apex ERP Modernization'. Notice our strict anti-mocking principle: when no documents are uploaded, the executive dashboard displays an honest, helpful empty state rather than fabricated statistics. Every metric in this platform must be grounded in actual document evidence."*

---

## Step 3: Initial Document Upload (Project Charter)
**Objective:** Ingest an initial unstructured project charter and observe the real-time parsing pipeline.

### Action
1. In the dropzone, drag and drop `Apex_Project_Charter.txt` (or browse and select it).
2. Click **Upload 1 File**.
3. Observe the loading spinner and the instant confirmation message:
   `"Successfully uploaded and indexed 1 document(s)."`
4. Expand the uploaded document row in the Document Catalog to view:
   - File size, word count, character count, and chunk count.
   - Click **View Chunks** to inspect sentence-level chunks with page/row coordinates.

### Spoken Explanation
> *"We upload the initial project charter. The backend validates the MIME type, extracts clean text, generates a SHA-256 content hash, and uses our sentence-boundary chunker to divide the document into semantic passages. Each chunk is tagged with source coordinates—document ID, chunk ID, page number, and source reference—and indexed into our persistent vector store."*

---

## Step 4: Multi-Agent Extraction Verification
**Objective:** Inspect autonomous intelligence outputs from Scope, Risk, and Blocker agents.

### Action
1. Click the **Agent Intelligence** tab on the dashboard navigation bar.
2. Review the three autonomous agent panels:
   - **Scope Agent:** Displays Primary Goal (*"Modernize the legacy warehouse management system into a cloud-native ERP platform"*), Core Objectives, and Deliverables (`DEL-01` through `DEL-04`).
   - **Risk Agent:** Displays detected risks, including `RISK-01: Third-party logistics API rate limits` (Severity: High) with recommended mitigation.
   - **Blocker Agent:** Displays active blockers, including `BLOCKER-01: Staging cloud IAM role permissions for AWS Aurora cluster` with impact and escalation path.

### Spoken Explanation
> *"Our multi-agent engine separates concerns across specialized autonomous agents. Rather than running a monolithic prompt, the Scope Agent extracts goals and milestones, the Risk Agent maps pitfalls against deadlines to generate a severity matrix, and the Blocker Agent identifies critical path impediments while explicitly marking unassigned owners as 'UNKNOWN' to prevent assumptions."*

---

## Step 5: Deterministic Health Scoring Analysis
**Objective:** Demonstrate transparent, mathematical project health scoring.

### Action
1. Click the **Project Health (0–100)** tab.
2. Observe the composite score gauge (e.g., `78.5 / 100 — Needs Attention`).
3. Point out the transparent mathematical formula breakdown:
   $$\text{Overall Score} = (\text{Scope} \times 0.35) + (\text{Timeline} \times 0.35) + (\text{Blocker} \times 0.30)$$
4. Show the three dimensional cards:
   - *Scope Clarity* score and contributing factors.
   - *Timeline Health* score and schedule compression alerts.
   - *Blocker Health* score and unassigned task penalties.
5. In the custom weights panel, adjust Blocker Health weight to `0.50` and observe the immediate mathematical recalculation.

### Spoken Explanation
> *"Unlike traditional project management tools where project health is subjectively guessed by managers, our system uses an objective, mathematical scoring engine. It evaluates Scope Clarity, Timeline Health, and Blocker Health using weighted dimensions. Stakeholders can inspect the exact mathematical contributions and critical issues pulling the score down."*

---

## Step 6: Autonomous Documentation Studio & CSV Export
**Objective:** Review generated user stories, risk register, and action items, and demonstrate CSV export.

### Action
1. Click the **Documentation Studio** tab.
2. Inspect the synthesized **User Stories**:
   - Formatted in Agile Given-When-Then criteria.
   - Click **Approve** on Story 1.
3. Switch sub-tab to **Risk Register**:
   - Inspect Risk ID, Category, Severity, and Mitigations.
4. Switch sub-tab to **Action Items**:
   - Inspect Action ID, Task Description, Owner, Due Date, and Priority.
5. Click **Export CSV** and open the downloaded `Action_Items.csv` to demonstrate enterprise spreadsheet compatibility.

### Spoken Explanation
> *"The Documentation Generation Studio translates raw requirements into agile delivery artifacts. User stories follow standard acceptance criteria, risks are formatted for PMO audits, and action items track delivery owners. Team leads can approve, edit, or reject items, and export them directly to CSV for integration with Jira or Excel."*

---

## Step 7: Executive Project Insights & Risk Summary Dashboard
**Objective:** Showcase the Milestone 4 Executive Dashboard.

### Action
1. Click the **Project Dashboard** tab.
2. Walk through the executive layout:
   - **5 Top Metric Cards:** Overall Health Score (`78.5`), Active Blockers (`1`), Total Risks (`2`), Pending Actions (`3`), and Deliverable Completion Rate (`25.0%`).
   - **Health Indicators Grid:** Dimensional score pills and recommendations.
   - **Key Deliverables Table:** Displays `DEL-01` (Completed), `DEL-02` (In Progress), `DEL-03` (Pending), `DEL-04` (Planned).
   - **Risks & Mitigations Cards:** Color-coded severity badges with direct evidence citations.
   - **Active Blockers List:** Owner, schedule impact, and resolution.

### Spoken Explanation
> *"Here is our core Milestone 4 deliverable: the Executive Project Insights & Risk Summary Dashboard. In one unified view, engineering leadership can immediately see overall project health, active blockers, delivery completion percentage, and high-severity risks. Every single number and card is computed live from the active project workspace without any synthetic or mock data."*

---

## Step 8: Incremental Document Upload (Meeting Notes)
**Objective:** Demonstrate non-destructive incremental document ingestion.

### Action
1. Click **Document Ingestion**.
2. Notice the badge in the workspace identity card: **`Incremental Mode Active`**.
3. Notice the upload button reads: **`Incrementally Add & Index File(s)`**.
4. Select `Apex_Sprint_Meeting_Notes.txt` and click upload.
5. Observe:
   - Green success banner: *"Successfully incrementally indexed 1 new document(s) into active workspace without disturbing existing knowledge base."*
   - Document count increments from 1 to 2.
   - Both `Apex_Project_Charter.txt` and `Apex_Sprint_Meeting_Notes.txt` appear in the catalog.
   - Previously indexed chunks are preserved; only new chunks were added.

### Spoken Explanation
> *"In Milestone 4, we implemented the Incremental Upload Pipeline. Real-world projects evolve weekly through meeting minutes and sprint reports. Notice how our system automatically recognized the active project, switched into Incremental Mode, and appended the meeting notes to our vector store without wiping or re-processing the initial project charter."*

---

## Step 9: Conversational Project Intelligence Assistant
**Objective:** Execute the 7 mandatory Milestone 4 queries and demonstrate strict anti-hallucination guardrails.

### Action
Click the **AI Assistant** tab. Enter the following queries one by one:

1. **Query 1: Main Goal**
   - *Prompt:* `"What is the main goal of this project?"`
   - *Observation:* Cites the cloud-native warehouse modernization goal with document provenance.
2. **Query 2: Biggest Risks**
   - *Prompt:* `"What are the biggest risks?"`
   - *Observation:* Answers with the logistics API rate limit and legacy unindexed foreign keys.
3. **Query 3: Are We On Track?**
   - *Prompt:* `"Are we currently on track?"`
   - *Observation:* Reports the 78.5 health score, status (Needs Attention), and delivery progress.
4. **Query 4: Pending Action Items**
   - *Prompt:* `"What are the pending action items?"`
   - *Observation:* Lists Dave Miller's and Sarah Chen's open tasks and due dates.
5. **Query 5: Completed Deliverables**
   - *Prompt:* `"Which deliverables are completed?"`
   - *Observation:* Reports that Database Migration Script is completed.
6. **Query 6: Blockers Affecting Progress**
   - *Prompt:* `"What blockers are affecting progress?"`
   - *Observation:* Reports the AWS Aurora IAM security approval blocker.
7. **Query 7: Changes After Meeting Notes**
   - *Prompt:* `"What changed after uploading the latest meeting notes?"`
   - *Observation:* Pulls directly from the newly uploaded meeting notes, noting that Aurora IAM approval was granted and query latency dropped 60%.
8. **Anti-Hallucination Guardrail Demo:**
   - *Prompt:* `"What is the project manager's favorite pizza topping and vacation island?"`
   - *Observation:* The assistant strictly refuses to speculate, responding:
     *"I couldn't find enough information in the uploaded project documents to answer this question."*

### Spoken Explanation
> *"The Conversational Assistant utilizes our RAG pipeline with strict provenance. For each question, it retrieves top-k chunks, provides direct citations down to the document and chunk ID, and supports complex queries such as 'What changed after uploading the latest meeting notes?'. Crucially, when asked about facts not in the documents, our anti-hallucination guardrail prevents fabrication and honestly admits lack of evidence."*

---

## Step 10: Multi-Project Workspace Isolation & Clean Teardown
**Objective:** Prove zero data bleed between projects.

### Action
1. Go to **Document Ingestion** and click **Start New Project**.
2. Enter `Healthcare Clinic Portal`.
3. Verify that the workspace resets cleanly: 0 documents, 0 chunks, clean dashboard.
4. In terminal, run the automated test suite to confirm all 61 tests pass:
   ```powershell
   backend\.venv\Scripts\python.exe -m pytest backend/tests -v
   ```
5. Point out the final line:
   `======================= 61 passed, 1 warning in 14.34s =======================`

### Spoken Explanation
> *"Finally, we demonstrate strict multi-project isolation. Starting a new workspace archives the previous project's embeddings and clears the active catalog, ensuring zero cross-project data bleed. To verify total system integrity, our automated pytest suite runs 61 end-to-end tests across all four milestones with a 100% pass rate. This concludes our demonstration."*
