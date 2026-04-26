"""Application configuration using Pydantic settings."""

import os
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings

# Project root is the directory where the application is installed
# In Docker: PROJECT_ROOT=/app (set via environment variable)
# In local dev: path/to/education (calculated from file location)
_env_root = os.getenv("PROJECT_ROOT")
if _env_root:
    PROJECT_ROOT = Path(_env_root)
else:
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Fixed system constants - relative to PROJECT_ROOT
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_URL: str = f"sqlite+aiosqlite:///{DATA_DIR}/db/learning.db"
STORAGE_BASE_PATH: Path = DATA_DIR
LLM_MODEL_PATH: Path = DATA_DIR / "models"
SENTENCE_SNAP: bool = True


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Paths and database are fixed system constants (not configurable)
    # DATABASE_URL, STORAGE_BASE_PATH, LLM_MODEL_PATH, SENTENCE_SNAP
    # are defined at module level above

    DEFAULT_MODEL: str = "Qwen3.5-2B-Q4_K_M.gguf"
    LLM_GPU_LAYERS: str = "-1"
    LLM_CONTEXT_SIZE: int = 4096
    LLM_THREADS: int = 4

    YOUTUBE_DOWNLOAD_QUALITY: int = 720
    YOUTUBE_AUDIO_QUALITY: str = "128k"
    CHUNK_DURATION: int = 300

    ENVIRONMENT: Literal["development", "production", "test"] = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
