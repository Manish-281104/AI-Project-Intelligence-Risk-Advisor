import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Request, HTTPException, Query, status

from app.core.config import settings
from app.schemas.project import (
    HealthResponse,
    ModuleItem,
    ModulesResponse,
    UploadResponse,
    DocumentMetadata,
    FileUploadResultItem,
    ProjectWorkspace,
    ProjectConflictDetail,
)
from app.schemas.agent_models import (
    ScopeExtractionResponse,
    RiskDetectionResponse,
    BlockerExtractionResponse,
    ComprehensiveAnalysisResponse,
)
from app.services.document_service import document_service
from app.services.scope_agent import scope_agent
from app.services.risk_agent import risk_agent
from app.services.blocker_agent import blocker_agent
from starlette.datastructures import UploadFile

router = APIRouter()

# Central registry of the nine project modules.
MODULES_REGISTRY: List[ModuleItem] = [
    ModuleItem(
        id=1,
        key="doc_ingestion",
        name="Document Ingestion and Knowledge Base Construction",
        category="Ingestion & Data Pipeline",
        description="Ingests heterogeneous project documents (PDF, DOCX, CSV, TXT), validates formats, and extracts text.",
        status="Partially Implemented",
        milestone="Milestone 1 Active",
        notes="File upload, size validation, MIME checks, single-file upload enforcement, and text parsers for PDF, DOCX, CSV, TXT are implemented and verified. Vector embedding & catalog persistence operational in Milestone 2.",
    ),
    ModuleItem(
        id=2,
        key="rag_pipeline",
        name="RAG Pipeline",
        category="Retrieval-Augmented Generation",
        description="Semantic chunking, vector embeddings, and persistent similarity retrieval with project isolation.",
        status="Planned",
        milestone="Milestone 2",
        notes="Semantic and lexical retrieval engine with TF-IDF vector embeddings, boundary-aware coordinate tracking (page/row/chunk), and persistent catalog.",
    ),
    ModuleItem(
        id=3,
        key="scope_extraction",
        name="Scope and Deliverable Extraction Agent",
        category="Autonomous Multi-Agent",
        description="Extracts objectives, in-scope vs out-of-scope boundaries, milestones, and deliverables with citations.",
        status="Planned",
        milestone="Milestone 2",
        notes="Multi-agent scope and deliverable extractor with Pydantic structured output validation and source citations.",
    ),
    ModuleItem(
        id=4,
        key="risk_forecasting",
        name="Risk Detection and Delivery Forecasting Agent",
        category="Autonomous Multi-Agent",
        description="Quantifies risk likelihood & impact, detects schedule slips via deterministic deadline deltas, and forecasts delays.",
        status="Planned",
        milestone="Milestone 2",
        notes="Dual-engine architecture: deterministic schedule slip calculations combined with qualitative risk severity matrix.",
    ),
    ModuleItem(
        id=5,
        key="blocker_identification",
        name="Blocker and Action Item Identification Agent",
        category="Autonomous Multi-Agent",
        description="Identifies blockers, dependencies, actionable tasks, designated assignees, and deadlines from minutes/retros.",
        status="Planned",
        milestone="Milestone 2",
        notes="Agent extraction with fallback handling for unassigned tasks, missing deadlines, and cross-document deduplication.",
    ),
    ModuleItem(
        id=6,
        key="doc_generation",
        name="Documentation Generation Agent",
        category="Autonomous Multi-Agent",
        description="Automated synthesis of draft user stories, risk registers, and executive status summaries.",
        status="Planned",
        milestone="Milestone 3",
        notes="Jinja2 and Markdown/DOCX templating engine with traceability links to ingested document chunks.",
    ),
    ModuleItem(
        id=7,
        key="health_scoring",
        name="Project Health Scoring",
        category="Analytics & Metrics",
        description="Deterministic mathematical composite health score (0-100) reflecting schedule adherence and risk density.",
        status="Planned",
        milestone="Milestone 3",
        notes="Formula-driven, reproducible scoring model without synthetic or fabricated values.",
    ),
    ModuleItem(
        id=8,
        key="conversational_assistant",
        name="Conversational Project Intelligence Assistant",
        category="Conversational AI",
        description="Project Q&A chat assistant with strict groundedness constraints and explicit document page/row citations.",
        status="Planned",
        milestone="Milestone 3",
        notes="Chat API with memory management and fallback to 'cannot find evidence in uploaded documents'.",
    ),
    ModuleItem(
        id=9,
        key="insights_dashboard",
        name="Project Insights and Risk Summary Dashboard",
        category="User Experience",
        description="React + TypeScript dashboard displaying live health, module status, document ingestion lab, and multi-agent findings.",
        status="Partially Implemented",
        milestone="Milestone 1 Active",
        notes="React + TypeScript dashboard with multi-agent results viewer for Scope, Risks, and Blockers.",
    ),
]


@router.get("/health", response_model=HealthResponse, tags=["System Health"])
async def get_health():
    """
    Health check endpoint.
    Returns backend service status and active multi-agent pipeline readiness.
    """
    storage_ok = settings.UPLOAD_DIR.exists() and settings.UPLOAD_DIR.is_dir()
    now_iso = datetime.now(timezone.utc).isoformat()

    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment="development",
        timestamp=now_iso,
        storage_ready=storage_ok,
        ai_pipeline_status="active in Milestone 2 (previously planned in Milestone 1)",
        message="Backend API is running. Multi-agent AI advisory pipeline and document ingestion services are active.",
    )


@router.get("/modules", response_model=ModulesResponse, tags=["Project Modules"])
async def get_modules():
    """
    Returns the nine planned project modules with their actual implementation statuses.
    """
    implemented = sum(1 for m in MODULES_REGISTRY if m.status == "Implemented and Verified")
    partially = sum(1 for m in MODULES_REGISTRY if m.status == "Partially Implemented")
    planned = sum(1 for m in MODULES_REGISTRY if m.status == "Planned")

    return ModulesResponse(
        total_modules=len(MODULES_REGISTRY),
        implemented_count=implemented,
        partially_implemented_count=partially,
        planned_count=planned,
        modules=MODULES_REGISTRY,
    )


@router.post(
    "/documents/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Document Ingestion"],
)
async def upload_document(request: Request):
    """
    Upload, parse, and chunk project documents (PDF, DOCX, CSV, TXT).
    Supports selecting and uploading multiple files together in a single operation.
    Validates and processes each file independently with per-file results.
    """
    form = await request.form()

    # Collect all uploaded file items from all form fields
    file_items: List[UploadFile] = []
    for _, value in form.multi_items():
        if isinstance(value, UploadFile) and value.filename:
            file_items.append(value)

    if len(file_items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded. Please select one or more documents to upload.",
        )

    batch_id = f"batch_{uuid.uuid4().hex[:8]}"
    results: List[FileUploadResultItem] = []
    successful_results: List[FileUploadResultItem] = []
    failed_results: List[FileUploadResultItem] = []

    for file_obj in file_items:
        try:
            metadata = await document_service.process_uploaded_file(file_obj, upload_batch_id=batch_id)
            item = FileUploadResultItem(
                filename=metadata.filename,
                success=True,
                status="processed",
                project_id=metadata.project_id,
                document_id=metadata.document_id,
                upload_batch_id=batch_id,
                extracted_characters=metadata.char_count,
                chunk_count=metadata.chunk_count,
                chunks=metadata.chunks,
                document=metadata,
                error=None,
            )
            results.append(item)
            successful_results.append(item)
        except HTTPException as exc:
            # For single file upload, raise directly to maintain exact status code and message
            if len(file_items) == 1:
                raise exc
            item = FileUploadResultItem(
                filename=file_obj.filename or "unknown",
                success=False,
                status="failed",
                project_id=document_service.get_workspace().project_id,
                upload_batch_id=batch_id,
                error=exc.detail,
            )
            results.append(item)
            failed_results.append(item)
        except Exception as exc:
            if len(file_items) == 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to process '{file_obj.filename}': {str(exc)}",
                )
            item = FileUploadResultItem(
                filename=file_obj.filename or "unknown",
                success=False,
                status="failed",
                project_id=document_service.get_workspace().project_id,
                upload_batch_id=batch_id,
                error=str(exc),
            )
            results.append(item)
            failed_results.append(item)

    # If all files in a multi-file batch failed
    if len(successful_results) == 0:
        error_summary = "; ".join(f"{r.filename}: {r.error}" for r in failed_results)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"All files failed validation: {error_summary}",
        )

    # At least one file succeeded
    first_success = successful_results[0]
    total_chars = sum(r.extracted_characters for r in successful_results)
    total_chunks = sum(r.chunk_count for r in successful_results)
    all_chunks = [c for r in successful_results for c in r.chunks]
    ws = document_service.get_workspace()

    if len(file_items) == 1:
        message = f"Document '{first_success.filename}' uploaded, parsed, and chunked successfully into project workspace '{ws.project_name or ws.project_id}'."
    else:
        message = (
            f"Batch upload complete: {len(successful_results)}/{len(file_items)} files processed successfully "
            f"into project workspace '{ws.project_name or ws.project_id}' ({total_chunks} chunks, {total_chars:,} characters)."
        )
        if failed_results:
            message += f" {len(failed_results)} file(s) failed."

    return UploadResponse(
        success=True,
        message=message,
        project_id=ws.project_id,
        upload_batch_id=batch_id,
        total_files=len(file_items),
        successful_count=len(successful_results),
        failed_count=len(failed_results),
        document_id=first_success.document_id,
        filename=first_success.filename,
        status="processed",
        extracted_characters=total_chars,
        chunk_count=total_chunks,
        chunks=all_chunks,
        document=first_success.document,
        results=results,
    )


@router.get(
    "/project",
    response_model=ProjectWorkspace,
    tags=["Project Workspace"],
)
async def get_project_workspace():
    """Retrieve current unified project workspace metadata, document count, and status."""
    return document_service.get_workspace()


@router.delete(
    "/project/reset",
    response_model=ProjectWorkspace,
    tags=["Project Workspace"],
)
async def reset_project_workspace():
    """Reset the current workspace, removing all uploaded documents and embeddings."""
    return document_service.reset_workspace()


@router.post(
    "/project/new",
    response_model=ProjectWorkspace,
    tags=["Project Workspace"],
)
async def start_new_project_workspace(
    project_name: Optional[str] = Query(None, description="Optional new project name"),
    project_id: Optional[str] = Query(None, description="Optional custom project ID"),
):
    """
    Start a fresh, isolated project workspace.
    Generates a new persistent project ID, archives previous project data,
    clears active analysis, and prepares a fresh knowledge base.
    """
    return document_service.start_new_workspace(project_id=project_id, project_name=project_name)



@router.get(
    "/documents",
    response_model=List[DocumentMetadata],
    tags=["Document Ingestion"],
)
async def list_documents():
    """Retrieve list of all ingested documents in the project knowledge base."""
    return document_service.list_documents()


@router.get(
    "/documents/{document_id}",
    response_model=DocumentMetadata,
    tags=["Document Ingestion"],
)
async def get_document(document_id: str):
    """Retrieve metadata and chunks for a specific ingested document."""
    doc = document_service.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found.",
        )
    return doc


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    tags=["Document Ingestion"],
)
async def delete_document(document_id: str):
    """Remove an ingested document and its chunks from the project repository."""
    success = document_service.delete_document(document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found.",
        )
    return {"success": True, "message": f"Document '{document_id}' deleted successfully."}


# =====================================================================
# Milestone 2 Autonomous Agent Endpoints
# =====================================================================

@router.post(
    "/agents/scope",
    response_model=ScopeExtractionResponse,
    tags=["Multi-Agent Advisory"],
)
async def extract_scope(document_id: Optional[str] = Query(None, description="Optional document ID filter")):
    """
    Run Scope and Deliverable Extraction Agent.
    Identifies project goals, scope boundaries, deliverables, milestones, deadlines,
    responsibilities, and dependencies strictly grounded in document evidence.
    """
    return await scope_agent.analyze(document_id=document_id)


@router.post(
    "/agents/risks",
    response_model=RiskDetectionResponse,
    tags=["Multi-Agent Advisory"],
)
async def detect_risks(document_id: Optional[str] = Query(None, description="Optional document ID filter")):
    """
    Run Risk Detection and Delivery Forecasting Agent.
    Identifies schedule slips, dependency bottlenecks, resource gaps, and delivery challenges
    using deterministic schedule checks and qualitative risk matrices.
    """
    return await risk_agent.analyze(document_id=document_id)


@router.post(
    "/agents/blockers",
    response_model=BlockerExtractionResponse,
    tags=["Multi-Agent Advisory"],
)
async def extract_blockers(document_id: Optional[str] = Query(None, description="Optional document ID filter")):
    """
    Run Blocker and Action Item Identification Agent.
    Extracts pending decisions, unresolved problems, blockers, and action items with assignees and statuses.
    """
    return await blocker_agent.analyze(document_id=document_id)


@router.post(
    "/agents/analyze-all",
    response_model=ComprehensiveAnalysisResponse,
    tags=["Multi-Agent Advisory"],
)
async def run_comprehensive_analysis(document_id: Optional[str] = Query(None, description="Optional document ID filter")):
    """
    Execute all three autonomous agents concurrently across ingested documents.
    Returns consolidated scope, risk, and blocker intelligence findings.
    """
    docs = document_service.list_documents()
    if document_id:
        target_docs = [d for d in docs if d.document_id == document_id]
    else:
        target_docs = docs

    doc_ids = [d.document_id for d in target_docs]
    doc_names = [d.filename for d in target_docs]

    scope_res = await scope_agent.analyze(document_id=document_id)
    risk_res = await risk_agent.analyze(document_id=document_id)
    blocker_res = await blocker_agent.analyze(document_id=document_id)

    return ComprehensiveAnalysisResponse(
        document_ids=doc_ids,
        analyzed_documents=doc_names,
        timestamp=datetime.now(timezone.utc).isoformat(),
        scope=scope_res,
        risks=risk_res,
        blockers=blocker_res,
    )
