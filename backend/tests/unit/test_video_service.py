"""Tests for VideoService."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.video_service import VideoService, ProcessingTimings
from app.services.exceptions import VideoProcessingError


class MockVideo:
    """Mock Video model for testing."""

    def __init__(
        self,
        id=None,
        status="pending",
        youtube_url="https://youtube.com/watch?v=test",
        **kwargs,
    ):
        self.id = id or uuid4()
        self._status = status
        self.youtube_url = youtube_url
        self.file_path = kwargs.get("file_path", None)
        self.title = kwargs.get("title", "Test Video")
        self.duration = kwargs.get("duration", 300.0)
        self.chunk_duration = kwargs.get("chunk_duration", 300.0)
        self.error_message = kwargs.get("error_message", None)
        self.thumbnail = kwargs.get("thumbnail", None)
        self.uploader = kwargs.get("uploader", None)
        self.upload_date = kwargs.get("upload_date", None)
        self.view_count = kwargs.get("view_count", None)
        self.like_count = kwargs.get("like_count", None)
        self.metadata_json = kwargs.get("metadata_json", None)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value


class TestVideoServiceInitialization:
    """Tests for VideoService initialization."""

    def test_initialization_with_custom_services(self, tmp_path):
        """VideoService should initialize with custom service instances."""
        video_repo = MagicMock()
        chunk_repo = MagicMock()
        transcript_repo = MagicMock()
        study_plan_repo = MagicMock()
        download_service = MagicMock()
        chunking_service = MagicMock()
        transcription_service = MagicMock()

        service = VideoService(
            video_repo=video_repo,
            chunk_repo=chunk_repo,
            transcript_repo=transcript_repo,
            study_plan_repo=study_plan_repo,
            download_service=download_service,
            chunking_service=chunking_service,
            transcription_service=transcription_service,
            storage_dir=tmp_path,
        )

        assert service.video_repo is video_repo
        assert service.chunk_repo is chunk_repo
        assert service.transcript_repo is transcript_repo
        assert service.study_plan_repo is study_plan_repo
        assert service.download_service is download_service
        assert service.chunking_service is chunking_service
        assert service.transcription_service is transcription_service

    def test_initialization_with_defaults(self):
        """VideoService should create default services when not provided."""
        video_repo = MagicMock()
        chunk_repo = MagicMock()
        transcript_repo = MagicMock()
        study_plan_repo = MagicMock()

        service = VideoService(
            video_repo=video_repo,
            chunk_repo=chunk_repo,
            transcript_repo=transcript_repo,
            study_plan_repo=study_plan_repo,
        )

        assert service.download_service is not None
        assert service.chunking_service is not None
        assert service.transcription_service is not None


class TestProcessVideo:
    """Tests for process_video state progression."""

    @pytest.mark.asyncio
    async def test_process_video_not_found(self, tmp_path):
        """process_video should raise VideoProcessingError if video not found."""
        video_repo = MagicMock()
        video_repo.get_by_id = AsyncMock(return_value=None)

        service = VideoService(
            video_repo=video_repo,
            chunk_repo=MagicMock(),
            transcript_repo=MagicMock(),
            study_plan_repo=MagicMock(),
            storage_dir=tmp_path,
        )

        with pytest.raises(VideoProcessingError) as exc_info:
            await service.process_video(uuid4())

        assert "not found" in str(exc_info.value.message)
        assert exc_info.value.failed_step == "lookup"

    @pytest.mark.asyncio
    async def test_process_video_failure_sets_error(self, tmp_path):
        """process_video should set error_message on failure."""
        video_repo = MagicMock()
        download_service = MagicMock()
        video = MockVideo(status="pending")
        video.file_path = str(tmp_path / "videos" / f"{video.id}.webm")
        (tmp_path / "videos").mkdir(parents=True, exist_ok=True)
        (tmp_path / "videos" / f"{video.id}.webm").touch()

        video_repo.get_by_id = AsyncMock(return_value=video)
        video_repo.save = AsyncMock(return_value=None)
        download_service.download_video = AsyncMock(
            side_effect=Exception("Download failed")
        )

        service = VideoService(
            video_repo=video_repo,
            chunk_repo=MagicMock(),
            transcript_repo=MagicMock(),
            study_plan_repo=MagicMock(),
            download_service=download_service,
            storage_dir=tmp_path,
        )

        with pytest.raises(Exception):
            await service.process_video(video.id)

        assert video.error_message == "Download failed"

    @pytest.mark.asyncio
    async def test_process_video_already_ready_returns_ready(self, tmp_path):
        """process_video should return (video, timings) if video already ready."""
        video_repo = MagicMock()
        video = MockVideo(status="ready")
        video_repo.get_by_id = AsyncMock(return_value=video)
        video_repo.save = AsyncMock(return_value=None)

        service = VideoService(
            video_repo=video_repo,
            chunk_repo=MagicMock(),
            transcript_repo=MagicMock(),
            study_plan_repo=MagicMock(),
            download_service=MagicMock(),
            storage_dir=tmp_path,
        )

        result, timings = await service.process_video(video.id)

        assert result.status == "ready"
        assert isinstance(timings, ProcessingTimings)


class TestRetryVideo:
    """Tests for retry_video."""

    @pytest.mark.asyncio
    async def test_retry_already_complete_returns_video(self, tmp_path):
        """retry_video should return immediately if video is ready."""
        video_repo = MagicMock()
        video = MockVideo(status="ready")
        video_repo.get_by_id = AsyncMock(return_value=video)

        service = VideoService(
            video_repo=video_repo,
            chunk_repo=MagicMock(),
            transcript_repo=MagicMock(),
            study_plan_repo=MagicMock(),
            download_service=MagicMock(),
            storage_dir=tmp_path,
        )

        result, timings = await service.retry_video(video.id)

        assert result.status == "ready"
        assert isinstance(timings, ProcessingTimings)
        assert timings.total_seconds == 0.0

    @pytest.mark.asyncio
    async def test_retry_nonexistent_video_raises_error(self, tmp_path):
        """retry_video should raise error if video not found."""
        video_repo = MagicMock()
        video_repo.get_by_id = AsyncMock(return_value=None)

        service = VideoService(
            video_repo=video_repo,
            chunk_repo=MagicMock(),
            transcript_repo=MagicMock(),
            study_plan_repo=MagicMock(),
            storage_dir=tmp_path,
        )

        with pytest.raises(VideoProcessingError) as exc_info:
            await service.retry_video(uuid4())

        assert "not found" in str(exc_info.value.message)


class TestProcessingTimings:
    """Tests for ProcessingTimings dataclass."""

    def test_timings_to_dict(self):
        """ProcessingTimings.to_dict should return properly formatted dict."""
        timings = ProcessingTimings(
            download_seconds=1.5,
            transcription_seconds=2.3,
            chunking_seconds=0.5,
            audio_extraction_seconds=1.0,
            study_plan_seconds=5.0,
            llm_init_seconds=1.0,
            llm_inference_seconds=3.5,
            total_seconds=10.3,
            stages_completed=["download", "transcription", "chunking"],
        )

        result = timings.to_dict()

        assert result["download_seconds"] == 1.5
        assert result["transcription_seconds"] == 2.3
        assert result["chunking_seconds"] == 0.5
        assert result["audio_extraction_seconds"] == 1.0
        assert result["study_plan_seconds"] == 5.0
        assert result["llm_init_seconds"] == 1.0
        assert result["llm_inference_seconds"] == 3.5
        assert result["total_seconds"] == 10.3
        assert result["stages_completed"] == ["download", "transcription", "chunking"]

    def test_timings_defaults(self):
        """ProcessingTimings should have sensible defaults."""
        timings = ProcessingTimings()

        result = timings.to_dict()

        assert result["download_seconds"] == 0.0
        assert result["transcription_seconds"] == 0.0
        assert result["chunking_seconds"] == 0.0
        assert result["audio_extraction_seconds"] == 0.0
        assert result["study_plan_seconds"] == 0.0
        assert result["llm_init_seconds"] == 0.0
        assert result["llm_inference_seconds"] == 0.0
        assert result["total_seconds"] == 0.0
        assert result["stages_completed"] == []

    def test_timings_rounding(self):
        """ProcessingTimings should round values to 2 decimal places."""
        timings = ProcessingTimings(total_seconds=1.23456789)
        result = timings.to_dict()
        assert result["total_seconds"] == 1.23