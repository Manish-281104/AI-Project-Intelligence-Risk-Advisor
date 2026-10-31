import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings:
    """Application configuration loaded from environment variables."""

    BASE_DIR: Path = BASE_DIR
    APP_NAME: str = os.getenv("APP_NAME", "AI Project Intelligence & Risk Advisor API")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.2.0 (Milestone 2)")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    # CORS origins for local development
    CORS_ORIGINS_RAW: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
    )

    @property
    def CORS_ORIGINS(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]

    # File upload settings
    UPLOAD_DIR_NAME: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "15"))
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024

    # Whitelist of allowed extensions
    ALLOWED_EXTENSIONS: tuple[str, ...] = (".pdf", ".docx", ".csv", ".txt")

    # Document text chunking settings (character-based)
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))

    @property
    def UPLOAD_DIR(self) -> Path:
        upload_path = BASE_DIR / self.UPLOAD_DIR_NAME
        upload_path.mkdir(parents=True, exist_ok=True)
        return upload_path


settings = Settings()
