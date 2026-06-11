"""Video service orchestrator with checkpoint-resume state machine."""

import asyncio
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
from app.services.llm_service import LLMService
from app.core.config import DATA_DIR

logger = get_logger(__name__)


@dataclass
class ProcessingTimings:
    """Elapsed time metrics for each processing stage."""

    download_seconds: float = 0.0
    transcription_seconds: float = 0.0
    chunking_seconds: float = 0.0
    audio_extraction_seconds: float = 0.0
    study_plan_seconds: float = 0.0
    llm_init_seconds: float = 0.0
    llm_inference_seconds: float = 0.0
    total_seconds: float = 0.0
    stages_completed: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "download_seconds": round(self.download_seconds, 2),
            "transcription_seconds": round(self.transcription_seconds, 2),
            "chunking_seconds": round(self.chunking_seconds, 2),
            "audio_extraction_seconds": round(self.audio_extraction_seconds, 2),
            "study_plan_seconds": round(self.study_plan_seconds, 2),
            "llm_init_seconds": round(self.llm_init_seconds, 2),
            "llm_inference_seconds": round(self.llm_inference_seconds, 2),
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

    Transcript Priority (highest to lowest):
        1. user - Student-uploaded subtitles
        2. youtube_author - YouTube author-uploaded subtitles
        3. whisper - Whisper transcription (always available)
        4. youtube_auto - YouTube auto-generated captions
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
        llm_service: LLMService | None = None,
        storage_dir: Path = DATA_DIR,
    ):
        self.video_repo = video_repo
        self.chunk_repo = chunk_repo
        self.transcript_repo = transcript_repo
        self.study_plan_repo = study_plan_repo
        self.download_service = download_service or DownloadService(storage_dir)
        self.chunking_service = chunking_service or ChunkingService()
        self.transcription_service = transcription_service or TranscriptionService(storage_dir)
        self.llm_service = llm_service or LLMService()

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
                video.thumbnail = info.get("thumbnail")
                video.uploader = info.get("uploader")
                video.upload_date = info.get("upload_date")
                video.view_count = info.get("view_count")
                video.like_count = info.get("like_count")
                video.metadata_json = {
                    "categories": info.get("categories"),
                    "tags": info.get("tags"),
                    "language": info.get("language"),
                    "subtitles": info.get("subtitles"),
                    "automatic_captions": info.get("automatic_captions"),
                    "available_formats": info.get("available_formats"),
                }
                await self._update_status(video, "downloading_complete")

            if video.status == "downloading_complete":
                current_stage = "transcription"
                start = time.perf_counter()
                await self._update_status(video, "transcribing")
                subtitle_paths = info.get("subtitle_paths", {})
                (
                    youtube_author_transcript,
                    youtube_auto_transcript,
                    whisper_transcript,
                ) = await self._transcribe_video(video, subtitle_paths)

                existing_transcripts = await self.transcript_repo.get_all_by_video_id(video.id)
                if existing_transcripts:
                    for et in existing_transcripts:
                        await self.transcript_repo.delete(et.id)
                    logger.info(f"Deleted {len(existing_transcripts)} existing transcripts before recreating")

                if youtube_author_transcript:
                    await self.transcript_repo.create(
                        video.id,
                        {
                            "source": "youtube_author",
                            "segments": youtube_author_transcript,
                            "language": "en",
                        },
                    )
                if youtube_auto_transcript:
                    await self.transcript_repo.create(
                        video.id,
                        {
                            "source": "youtube_auto",
                            "segments": youtube_auto_transcript,
                            "language": "en",
                        },
                    )
                await self.transcript_repo.create(
                    video.id,
                    {
                        "source": "whisper",
                        "segments": whisper_transcript,
                        "language": "en",
                    },
                )

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

                existing_chunks = await self.chunk_repo.get_by_video_id(video.id)
                if existing_chunks:
                    await self.chunk_repo.delete_by_video_id(video.id)
                    logger.info(f"Deleted {len(existing_chunks)} existing chunks before recreating")

                chunks = await self._create_chunks_with_snap(video)
                await self.chunk_repo.create_many(chunks)
                timings.chunking_seconds = time.perf_counter() - start
                timings.stages_completed.append("chunking")
                logger.info(f"[TIMING] Chunking stage completed in {timings.chunking_seconds:.2f}s")
                await self._update_status(video, "chunking_complete")

            if video.status == "chunking_complete":
                current_stage = "audio_extraction"
                start = time.perf_counter()
                await self._update_status(video, "extracting_audio")
                await self._extract_audio_chunks(video)
                timings.audio_extraction_seconds = time.perf_counter() - start
                timings.stages_completed.append("audio_extraction")
                logger.info(
                    f"[TIMING] Audio extraction stage completed in {timings.audio_extraction_seconds:.2f}s"
                )
                await self._update_status(video, "audio_extracted")

            if video.status == "audio_extracted":
                current_stage = "study_plan"
                start = time.perf_counter()
                await self._update_status(video, "studying")
                transcript = await self.get_transcript_by_priority(video.id)
                transcript_data = {"segments": transcript.segments} if transcript else {}
                study_plan, llm_timings = await self._generate_study_plan(video, transcript_data)
                await self.study_plan_repo.create(video.id, study_plan)
                timings.study_plan_seconds = time.perf_counter() - start
                timings.llm_init_seconds = llm_timings.get("llm_init_seconds", 0.0)
                timings.llm_inference_seconds = llm_timings.get("llm_inference_seconds", 0.0)
                timings.stages_completed.append("study_plan")
                logger.info(
                    f"[TIMING] Study plan stage completed in {timings.study_plan_seconds:.2f}s "
                    f"(llm_init={timings.llm_init_seconds:.2f}s, "
                    f"llm_inference={timings.llm_inference_seconds:.2f}s)"
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
            stage_to_status = {
                "download": "downloading_complete",
                "transcription": "transcribing_complete",
                "chunking": "chunking_complete",
                "audio_extraction": "audio_extracted",
                "study_plan": "ready",
            }
            last_completed = timings.stages_completed[-1] if timings.stages_completed else None
            resume_status = stage_to_status.get(last_completed, "pending")
            await self._update_status(video, resume_status, error_message=str(e))
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

        logger.info(f"Retrying video {video_id} from status {video.status}")
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

        transcript = await self.get_transcript_by_priority(video.id)
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

    async def _transcribe_video(
        self, video: Video, subtitle_paths: dict | None = None
    ) -> tuple[Optional[list[dict]], Optional[list[dict]], list[dict]]:
        """Transcribe video using triple transcript system.

        Always runs Whisper. Tries to get YouTube author and auto subtitles if available.

        Args:
            video: Video model with file_path
            subtitle_paths: Dict with 'author' and 'auto' subtitle paths

        Returns:
            Tuple of (youtube_author_transcript, youtube_auto_transcript, whisper_transcript)
        """
        video_path = Path(video.file_path)
        subtitle_paths = subtitle_paths or {}
        (
            youtube_author_transcript,
            youtube_auto_transcript,
            whisper_transcript,
        ) = await self.transcription_service.get_dual_transcripts(
            video_path, subtitle_paths=subtitle_paths
        )
        return youtube_author_transcript, youtube_auto_transcript, whisper_transcript

    async def _extract_audio_chunks(self, video: Video) -> None:
        """Extract audio for each chunk in mp3 format.

        Args:
            video: Video model with file_path and chunks
        """
        video_path = Path(video.file_path)
        video_audios_dir = self.transcription_service.storage_dir / "audios" / str(video.id)
        video_audios_dir.mkdir(parents=True, exist_ok=True)

        chunks = await self.chunk_repo.get_by_video_id(video.id)
        if not chunks:
            logger.warning(f"No chunks found for video {video.id}")
            return

        for chunk in chunks:
            audio_path = video_audios_dir / f"chunk_{chunk.chunk_index}.mp3"
            if audio_path.exists():
                logger.info(f"Audio already exists for chunk {chunk.chunk_index}")
                continue

            await self._extract_audio_chunk(
                video_path, chunk.start_time, chunk.end_time, audio_path
            )
            logger.info(f"Extracted audio for chunk {chunk.chunk_index}: {audio_path}")

    async def _extract_audio_chunk(
        self, video_path: Path, start_time: float, end_time: float, output_path: Path
    ) -> Path:
        """Extract a specific audio chunk from video.

        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            end_time: End time in seconds
            output_path: Output path for mp3 file

        Returns:
            Path to extracted audio file
        """
        cmd = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-ss",
            str(start_time),
            "-to",
            str(end_time),
            "-vn",
            "-acodec",
            "libmp3lame",
            "-ab",
            "128k",
            "-y",
            str(output_path),
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            logger.error(f"FFmpeg audio extraction failed: {stderr.decode()}")
            raise TranscriptionError(f"FFmpeg audio extraction failed: {stderr.decode()}")

        return output_path

    async def _generate_study_plan(self, video: Video, transcript: dict) -> dict:
        """Generate study plan using LLM."""
        logger.info(f"Generating study plan for video {video.id}")
        return await self.llm_service.generate_study_plan(
            transcript=transcript,
            video_title=video.title or "Untitled Video",
            video_duration=video.duration or 0.0,
        )

    async def get_transcript_by_priority(self, video_id: UUID) -> dict | None:
        """Get transcript using priority: user > youtube_author > whisper > youtube_auto.

        Returns the highest priority available transcript.

        Priority:
            1. user - Student-uploaded subtitles (highest)
            2. youtube_author - YouTube author-uploaded subtitles
            3. whisper - Whisper transcription (always available)
            4. youtube_auto - YouTube auto-generated captions (lowest)

        Args:
            video_id: Video UUID

        Returns:
            Transcript with highest priority, or None if none available
        """
        for source in ["user", "youtube_author", "whisper", "youtube_auto"]:
            transcript = await self.transcript_repo.get_by_video_and_source(video_id, source)
            if transcript and hasattr(transcript, "segments") and transcript.segments:
                logger.info(f"Selected {source} transcript for video {video_id}")
                return transcript
        return None
