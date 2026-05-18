"""Video service orchestrator with checkpoint-resume state machine."""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from app.core.logging import get_logger
from app.models.chunk import VideoChunk
from app.models.video import Video
from app.repositories.chunk import ChunkRepository
from app.repositories.study_plan import StudyPlanRepository
from app.repositories.transcript import TranscriptRepository
from app.repositories.video import VideoRepository
from app.services.chunking_service import ChunkingService
from app.services.download_service import DownloadService
from app.services.exceptions import (
    ChunkingError,
    DownloadError,
    StudyPlanError,
    TranscriptionError,
    VideoProcessingError,
)
from app.services.transcription_service import TranscriptionService
from app.core.config import DATA_DIR

logger = get_logger(__name__)


@dataclass
class ProcessingTimings:
    """Elapsed time metrics for each processing stage."""

    download_seconds: float = 0.0
    transcription_seconds: float = 0.0
    chunking_seconds: float = 0.0
    study_plan_seconds: float = 0.0
    total_seconds: float = 0.0
    stages_completed: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "download_seconds": round(self.download_seconds, 2),
            "transcription_seconds": round(self.transcription_seconds, 2),
            "chunking_seconds": round(self.chunking_seconds, 2),
            "study_plan_seconds": round(self.study_plan_seconds, 2),
            "total_seconds": round(self.total_seconds, 2),
            "stages_completed": self.stages_completed,
        }


class VideoService:
    """Orchestrator for video processing pipeline.

    State Machine:
        pending -> downloading -> downloading_complete ->
        transcribing -> transcribing_complete ->
        chunking -> chunking_complete ->
        studying -> ready | failed

    On failure, video stays in last successful state with error_message set.
    Use retry_video() to resume from checkpoint.
    """

    def __init__(
        self,
        video_repo: VideoRepository,
        chunk_repo: ChunkRepository,
        transcript_repo: TranscriptRepository,
        study_plan_repo: StudyPlanRepository,
        download_service: DownloadService | None = None,
        chunking_service: ChunkingService | None = None,
        transcription_service: TranscriptionService | None = None,
        storage_dir: Path = DATA_DIR,
    ):
        self.video_repo = video_repo
        self.chunk_repo = chunk_repo
        self.transcript_repo = transcript_repo
        self.study_plan_repo = study_plan_repo
        self.download_service = download_service or DownloadService(storage_dir)
        self.chunking_service = chunking_service or ChunkingService()
        self.transcription_service = transcription_service or TranscriptionService(storage_dir)

    async def process_video(self, video_id: UUID) -> tuple[Video, ProcessingTimings]:
        """Process video through full pipeline with checkpoint-resume.

        Pipeline steps:
            1. Download (if pending) - downloads video + subtitles simultaneously
            2. Transcribe (if downloading_complete) - uses downloaded subtitles
            3. Chunk (if transcribing_complete) - uses transcript for sentence snap
            4. Study Plan (if chunking_complete)

        Args:
            video_id: UUID of video to process

        Returns:
            Tuple of (Processed Video model, ProcessingTimings)

        Raises:
            VideoProcessingError: On unrecoverable failure
        """
        video = await self.video_repo.get_by_id(video_id)
        if not video:
            raise VideoProcessingError(
                f"Video {video_id} not found",
                checkpoint_state="unknown",
                failed_step="lookup",
            )

        logger.info(f"Starting video processing for {video_id}, current status: {video.status}")

        timings = ProcessingTimings()
        total_start = time.perf_counter()
        current_stage = "none"

        try:
            if video.status == "pending":
                current_stage = "download"
                start = time.perf_counter()
                await self._update_status(video, "downloading")
                info = await self.download_service.download_video(video.youtube_url, str(video_id))
                timings.download_seconds = time.perf_counter() - start
                timings.stages_completed.append("download")
                logger.info(f"[TIMING] Download stage completed in {timings.download_seconds:.2f}s")
                video.file_path = info.get("video_path")
                video.title = info.get("title", video.title)
                video.duration = info.get("duration", 0.0)
                video.subtitle_paths = info.get("subtitle_paths", [])
                await self._update_status(video, "downloading_complete")

            if video.status == "downloading_complete":
                current_stage = "transcription"
                start = time.perf_counter()
                await self._update_status(video, "transcribing")
                transcript = await self._transcribe_video(video)
                await self.transcript_repo.create(video.id, transcript)
                timings.transcription_seconds = time.perf_counter() - start
                timings.stages_completed.append("transcription")
                logger.info(
                    f"[TIMING] Transcription stage completed in {timings.transcription_seconds:.2f}s"
                )
                await self._update_status(video, "transcribing_complete")

            if video.status == "transcribing_complete":
                current_stage = "chunking"
                start = time.perf_counter()
                await self._update_status(video, "chunking")
                chunks = await self._create_chunks_with_snap(video)
                await self.chunk_repo.create_many(chunks)
                timings.chunking_seconds = time.perf_counter() - start
                timings.stages_completed.append("chunking")
                logger.info(f"[TIMING] Chunking stage completed in {timings.chunking_seconds:.2f}s")
                await self._update_status(video, "chunking_complete")

            if video.status == "chunking_complete":
                current_stage = "study_plan"
                start = time.perf_counter()
                await self._update_status(video, "studying")
                study_plan = {"objectives": [], "vocabulary": [], "grammar": []}
                await self.study_plan_repo.create(video.id, study_plan)
                timings.study_plan_seconds = time.perf_counter() - start
                timings.stages_completed.append("study_plan")
                logger.info(
                    f"[TIMING] Study plan stage completed in {timings.study_plan_seconds:.2f}s"
                )
                await self._update_status(video, "ready")

            timings.total_seconds = time.perf_counter() - total_start
            logger.info(
                f"[TIMING] Video {video_id} processing completed in {timings.total_seconds:.2f}s"
            )
            logger.info(f"[TIMING] Stage timings: {timings.to_dict()}")
            return await self.video_repo.get_by_id(video_id), timings

        except Exception as e:
            timings.total_seconds = time.perf_counter() - total_start
            logger.error(
                f"Video {video_id} processing failed at {current_stage} after {timings.total_seconds:.2f}s: {e}"
            )
            logger.error(f"[TIMING] Failed stage timings: {timings.to_dict()}")
            await self._update_status(video, "failed", error_message=str(e))
            raise

    async def retry_video(self, video_id: UUID) -> tuple[Video, ProcessingTimings]:
        """Retry processing from last checkpoint.

        Args:
            video_id: UUID of video to retry

        Returns:
            Tuple of (Video model, ProcessingTimings) (may still be in-progress if not yet ready)
        """
        video = await self.video_repo.get_by_id(video_id)
        if not video:
            raise VideoProcessingError(
                f"Video {video_id} not found",
                checkpoint_state="unknown",
                failed_step="lookup",
            )

        if video.status == "ready":
            logger.info(f"Video {video_id} already complete")
            return video, ProcessingTimings()

        if video.status == "failed":
            logger.info(f"Retrying video {video_id} from checkpoint")
            return await self.process_video(video_id)

        return await self.process_video(video_id)

    async def _update_status(
        self,
        video: Video,
        status: str,
        error_message: str | None = None,
    ) -> None:
        """Update video status and optionally set error_message."""
        video.status = status
        if error_message is not None:
            video.error_message = error_message
        await self.video_repo.save(video)
        logger.info(f"Video {video.id} status updated to: {status}")

    async def _create_chunks_with_snap(self, video: Video) -> List[VideoChunk]:
        """Create chunks with Hybrid Dynamic sentence-snap."""
        duration = video.duration

        transcript = await self.transcript_repo.get_by_video_id(video.id)
        transcript_data = []
        if transcript:
            transcript_data = transcript.segments if hasattr(transcript, "segments") else []

        chunk_models = await self.chunking_service.create_chunks(
            video_duration=duration,
            transcript=transcript_data,
            chunk_duration=int(video.chunk_duration),
        )

        return [
            VideoChunk(
                video_id=video.id,
                chunk_index=c.index,
                start_time=c.start_time,
                end_time=c.end_time,
                duration=c.duration,
                status="pending",
            )
            for c in chunk_models
        ]

    async def _transcribe_video(self, video: Video) -> dict:
        """Transcribe video using downloaded subtitles as basis.

        Args:
            video: Video model with file_path and subtitle_paths

        Returns:
            dict with transcript segments
        """
        video_path = Path(video.file_path)
        subtitle_paths = getattr(video, "subtitle_paths", []) or []
        transcript_entries = await self.transcription_service.transcribe(
            video_path, subtitle_paths=subtitle_paths
        )
        return {
            "segments": transcript_entries,
            "language": "en",
        }

    async def _generate_study_plan(self, video: Video, transcript: dict) -> dict:
        """Generate study plan using LLM (stub for Phase 3)."""
        return {
            "objectives": ["Understand the main topic"],
            "vocabulary": [],
            "grammar": [],
            "estimated_time": "30 minutes",
        }
