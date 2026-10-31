from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import router as api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI Project Intelligence & Risk Advisor API - Milestone 1.\n\n"
        "Provides backend service health monitoring, project module registry tracking, "
        "and initial document ingestion & parsing service (PDF, DOCX, CSV, TXT)."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure Cross-Origin Resource Sharing (CORS) for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API endpoints under /api
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    """Root landing endpoint providing API information and link to Swagger docs."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "documentation": "/docs",
        "endpoints": {
            "health": "/api/health",
            "modules": "/api/modules",
            "document_upload": "/api/documents/upload",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
