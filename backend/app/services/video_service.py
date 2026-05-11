"""Video service orchestrator with checkpoint-resume state machine."""

import logging
from pathlib import Path
from typing import List, Optional
from uuid import UUID

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

logger = logging.getLogger(__name__)


class VideoService:
    """Orchestrator for video processing pipeline.

    State Machine:
        pending -> downloading -> downloading_complete ->
        chunking -> chunking_complete ->
        transcribing -> transcribing_complete ->
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
        self.transcription_service = transcription_service or TranscriptionService(
            storage_dir
        )

    async def process_video(self, video_id: UUID) -> Video:
        """Process video through full pipeline with checkpoint-resume.

        Pipeline steps:
            1. Download (if pending)
            2. Chunk (if downloading_complete)
            3. Transcribe (if chunking_complete)
            4. Study Plan (if transcribing_complete)

        Args:
            video_id: UUID of video to process

        Returns:
            Processed Video model

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

        logger.info(
            f"Starting video processing for {video_id}, current status: {video.status}"
        )

        try:
            if video.status == "pending":
                await self._update_status(video, "downloading")
                info = await self.download_service.download_video(
                    video.youtube_url, str(video_id)
                )
                video.file_path = str(info.output_path)
                video.title = info.get("title", video.title)
                video.duration = info.get("duration", 0.0)
                await self._update_status(video, "downloading_complete")

            if video.status == "downloading_complete":
                await self._update_status(video, "chunking")
                chunks = await self._create_chunks_with_snap(video)
                await self.chunk_repo.create_many(chunks)
                await self._update_status(video, "chunking_complete")

            if video.status == "chunking_complete":
                await self._update_status(video, "transcribing")
                transcript = await self._transcribe_video(video)
                await self.transcript_repo.create(video.id, transcript)
                await self._update_status(video, "transcribing_complete")

            if video.status == "transcribing_complete":
                await self._update_status(video, "studying")
                study_plan = {"objectives": [], "vocabulary": [], "grammar": []}
                await self.study_plan_repo.create(video.id, study_plan)
                await self._update_status(video, "ready")

            logger.info(f"Video {video_id} processing completed successfully")
            return await self.video_repo.get_by_id(video_id)

        except Exception as e:
            logger.error(f"Video {video_id} processing failed at {video.status}: {e}")
            await self._update_status(video, "failed", error_message=str(e))
            raise

    async def retry_video(self, video_id: UUID) -> Video:
        """Retry processing from last checkpoint.

        Args:
            video_id: UUID of video to retry

        Returns:
            Video model (may still be in-progress if not yet ready)
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
            return video

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
            transcript_data = (
                transcript.segments if hasattr(transcript, "segments") else []
            )

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
        """Transcribe video and return transcript data."""
        video_path = Path(video.file_path)
        transcript_entries = await self.transcription_service.transcribe(video_path)
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
