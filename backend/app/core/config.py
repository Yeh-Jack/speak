"""Application configuration using Pydantic settings."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/education"

    # Storage
    STORAGE_BASE_PATH: Path = Path("/data")

    # LLM Configuration
    LLM_MODEL_PATH: Path = Path("/data/shared/models")
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
