from typing import Optional, List
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check endpoint response model."""

    status: str = Field(..., description="Overall service status (e.g., 'ok')")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Current application release version")
    environment: str = Field(..., description="Runtime environment")
    timestamp: str = Field(..., description="ISO 8601 server timestamp")
    storage_ready: bool = Field(..., description="Local document upload directory availability")
    ai_pipeline_status: str = Field(..., description="Honest status of AI inference / RAG pipeline")
    message: str = Field(..., description="Informational message about the service")


class ModuleItem(BaseModel):
    """Schema for individual functional module metadata."""

    id: int = Field(..., description="Module numeric identifier (1-9)")
    key: str = Field(..., description="Unique machine-readable module key")
    name: str = Field(..., description="Display title of the module")
    category: str = Field(..., description="Functional area / domain")
    description: str = Field(..., description="Brief description of the module scope")
    status: str = Field(..., description="Current implementation status ('Implemented and Verified', 'Partially Implemented', 'Planned')")
    milestone: str = Field(..., description="Target or active milestone")
    notes: str = Field(..., description="Honest technical commentary on what is physically built vs planned")


class ModulesResponse(BaseModel):
    """Response containing list of all 9 project modules."""

    total_modules: int = Field(9, description="Total planned system modules")
    implemented_count: int = Field(0, description="Count of fully completed modules")
    partially_implemented_count: int = Field(2, description="Count of partially implemented modules")
    planned_count: int = Field(7, description="Count of upcoming planned modules")
    modules: List[ModuleItem] = Field(..., description="Registry of all nine project modules")


class ProjectWorkspace(BaseModel):
    """Unified single-project workspace metadata."""

    project_id: str = Field(..., description="Persistent project workspace identifier")
    project_name: Optional[str] = Field(None, description="Established project title/name")
    client: Optional[str] = Field(None, description="Established client / sponsor organization")
    description: Optional[str] = Field(None, description="Project overview or summary")
    created_at: str = Field(..., description="ISO 8601 workspace creation timestamp")
    updated_at: str = Field(..., description="ISO 8601 last update timestamp")
    document_ids: List[str] = Field(default_factory=list, description="IDs of all documents associated with this project")
    document_count: int = Field(0, description="Total documents in project workspace")


class ProjectConflictDetail(BaseModel):
    """Details returned when an uploaded document explicitly conflicts with the workspace project identity."""

    error: str = Field("Project identity conflict", description="Error category")
    message: str = Field(..., description="User-friendly conflict explanation")
    existing_project_id: str = Field(..., description="Current workspace project ID")
    existing_project_name: Optional[str] = Field(None, description="Established workspace project name")
    existing_client: Optional[str] = Field(None, description="Established workspace client")
    conflicting_project_name: Optional[str] = Field(None, description="Conflicting project name found in document")
    conflicting_project_id: Optional[str] = Field(None, description="Conflicting project ID found in document")
    conflicting_client: Optional[str] = Field(None, description="Conflicting client/sponsor found in document")
    filename: str = Field(..., description="Filename that triggered conflict")


class DocumentChunk(BaseModel):
    """A discrete text chunk produced during document processing."""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Source document identifier")
    project_id: str = Field(default="proj_workspace_default", description="Associated project workspace ID")
    source: str = Field(..., description="Source filename")
    text: str = Field(..., description="Extracted chunk text content")
    page_number: Optional[int] = Field(None, description="Source page number (for PDF)")
    row_number: Optional[int] = Field(None, description="Source row number (for CSV/tables)")
    source_ref: Optional[str] = Field(None, description="Source reference label (e.g. 'Page 1', 'Rows 1-5')")
    char_count: int = Field(..., description="Number of characters in chunk")
    word_count: int = Field(..., description="Number of words in chunk")
    token_count: Optional[int] = Field(None, description="Estimated token count in chunk")
    is_evaluator_guidance: bool = Field(False, description="Whether chunk contains test evaluator guidance or suggested questions")


class DocumentMetadata(BaseModel):
    """Extracted metadata and text statistics from an ingested document."""

    document_id: str = Field(..., description="Unique UUID assigned to the document")
    project_id: str = Field(default="proj_workspace_default", description="Persistent workspace project identifier")
    project_name: Optional[str] = Field(None, description="Project name extracted or inherited from workspace")
    client: Optional[str] = Field(None, description="Client or sponsor organization")
    is_project_inherited: bool = Field(True, description="Whether project identity was inherited from workspace")
    upload_batch_id: Optional[str] = Field(None, description="Internal upload batch operation identifier")
    filename: str = Field(..., description="Original client filename")
    file_type: str = Field(..., description="Detected file format extension (.pdf, .docx, .csv, .txt)")
    file_size_bytes: int = Field(..., description="Raw file size in bytes")
    file_size_kb: float = Field(..., description="File size formatted in kilobytes")
    uploaded_at: str = Field(..., description="ISO 8601 upload timestamp")
    page_count: Optional[int] = Field(None, description="Number of pages (for PDF)")
    paragraph_count: Optional[int] = Field(None, description="Number of paragraphs (for DOCX)")
    row_count: Optional[int] = Field(None, description="Number of data rows (for CSV)")
    column_count: Optional[int] = Field(None, description="Number of columns (for CSV)")
    columns: Optional[List[str]] = Field(None, description="List of column headers (for CSV)")
    char_count: int = Field(..., description="Total characters extracted from text")
    word_count: int = Field(..., description="Total words extracted from text")
    preview_snippet: str = Field(..., description="First 400 characters of extracted text for UI preview")
    chunk_count: int = Field(0, description="Total number of chunks produced")
    chunks: List[DocumentChunk] = Field(default_factory=list, description="List of generated text chunks")
    full_text: Optional[str] = Field(None, description="Clean full document text without chunk overlap")
    status: str = Field("processed", description="Document ingestion status")
    notes: str = Field(..., description="Processing and next milestone indexing notes")


class FileUploadResultItem(BaseModel):
    """Result of an individual file upload and processing within a batch."""

    filename: str = Field(..., description="Original client filename")
    success: bool = Field(..., description="Whether file parsing succeeded")
    status: str = Field("processed", description="Status: 'processed' or 'failed'")
    project_id: Optional[str] = Field(None, description="Persistent workspace project identifier")
    document_id: Optional[str] = Field(None, description="Unique document ID if successful")
    upload_batch_id: Optional[str] = Field(None, description="Internal upload batch operation identifier")
    extracted_characters: int = Field(0, description="Characters extracted from text")
    chunk_count: int = Field(0, description="Number of chunks generated")
    chunks: List[DocumentChunk] = Field(default_factory=list, description="List of generated text chunks")
    document: Optional[DocumentMetadata] = Field(None, description="Document metadata if successful")
    error: Optional[str] = Field(None, description="Error message if processing failed")


class UploadResponse(BaseModel):
    """Response payload for document upload and chunking (single or multiple files)."""

    success: bool = Field(True, description="Indicates at least one document succeeded")
    message: str = Field(..., description="User-friendly status message")
    project_id: str = Field(default="proj_workspace_default", description="Unified workspace project ID")
    upload_batch_id: Optional[str] = Field(None, description="Internal upload batch operation identifier")
    total_files: int = Field(1, description="Total number of files submitted in batch")
    successful_count: int = Field(1, description="Number of successfully processed files")
    failed_count: int = Field(0, description="Number of failed files")
    # Backwards-compatible single-file fields (populated with first successful document)
    document_id: Optional[str] = Field(None, description="Primary document ID")
    filename: Optional[str] = Field(None, description="Primary document filename")
    status: str = Field("processed", description="Overall ingestion status")
    extracted_characters: int = Field(0, description="Total characters extracted")
    chunk_count: int = Field(0, description="Total chunks produced")
    chunks: List[DocumentChunk] = Field(default_factory=list, description="All chunks produced")
    document: Optional[DocumentMetadata] = Field(None, description="Primary document metadata")
    # Per-file results for multiple file tracking
    results: List[FileUploadResultItem] = Field(default_factory=list, description="Per-file detailed results")



