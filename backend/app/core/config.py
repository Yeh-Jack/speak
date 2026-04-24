"""Application configuration using Pydantic settings."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings

# Get project root (parent of backend directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent


def get_database_url() -> str:
    """Get database URL with auto-created data directory."""
    data_dir = PROJECT_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "learning.db"
    return f"sqlite+aiosqlite:///{db_path}"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database - computed absolute path from project root
    DATABASE_URL: str = get_database_url()

    # Storage - relative to project root, resolved to absolute
    STORAGE_BASE_PATH: Path = PROJECT_ROOT / "data"

    # LLM Configuration
    LLM_MODEL_PATH: Path = PROJECT_ROOT / "data" / "shared" / "models"
    DEFAULT_MODEL: str = "qwen2.5-7b-q4_k_m.gguf"
    LLM_GPU_LAYERS: str = "-1"  # -1=auto, 0=CPU, N=specific layers
    LLM_CONTEXT_SIZE: int = 4096
    LLM_THREADS: int = 4

    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # YouTube Download
    YOUTUBE_DOWNLOAD_QUALITY: int = 720
    YOUTUBE_AUDIO_QUALITY: str = "128k"

    # App Settings
    ENVIRONMENT: Literal["development", "production", "test"] = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
