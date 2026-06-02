"""Services module for business logic."""

from app.services.download_service import DownloadService
from app.services.chunking_service import (
    ChunkingService,
    ChunkingConfig,
    VideoChunk as ChunkingVideoChunk,
)
from app.services.transcription_service import (
    TranscriptionService,
    SubtitleService,
    WhisperTranscriptionService,
)
from app.services.video_service import VideoService
from app.services.llm_service import LLMService
from app.services.exceptions import (
    VideoProcessingError,
    DownloadError,
    ChunkingError,
    TranscriptionError,
    StudyPlanError,
)

__all__ = [
    # Download
    "DownloadService",
    # Chunking
    "ChunkingService",
    "ChunkingConfig",
    "ChunkingVideoChunk",
    # Transcription
    "TranscriptionService",
    "SubtitleService",
    "WhisperTranscriptionService",
    # Video orchestrator
    "VideoService",
    # LLM
    "LLMService",
    # Exceptions
    "VideoProcessingError",
    "DownloadError",
    "ChunkingError",
    "TranscriptionError",
    "StudyPlanError",
]
