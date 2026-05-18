"""Tests for video_service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.video_service import VideoService
from app.services.exceptions import VideoProcessingError


class MockVideo:
    """Mock Video model."""

    def __init__(
        self, id=None, status="pending", youtube_url="https://youtube.com/watch?v=test", **kwargs
    ):
        self.id = id or uuid4()
        self.status = status
        self.youtube_url = youtube_url
        self.file_path = kwargs.get("file_path", None)
        self.title = kwargs.get("title", "Test Video")
        self.duration = kwargs.get("duration", 300.0)
        self.chunk_duration = kwargs.get("chunk_duration", 300.0)
        self.error_message = kwargs.get("error_message", None)


class MockVideoServiceDependencies:
    """Mock service dependencies for VideoService."""

    def __init__(self):
        self.video_repo = MagicMock()
        self.chunk_repo = MagicMock()
        self.transcript_repo = MagicMock()
        self.study_plan_repo = MagicMock()
        self.download_service = MagicMock()
        self.chunking_service = MagicMock()
        self.transcription_service = MagicMock()


@pytest.fixture
def mock_deps():
    """Create mock dependencies for VideoService."""
    return MockVideoServiceDependencies()


@pytest.fixture
def video_service(mock_deps, tmp_path):
    """Create VideoService with mock dependencies."""
    return VideoService(
        video_repo=mock_deps.video_repo,
        chunk_repo=mock_deps.chunk_repo,
        transcript_repo=mock_deps.transcript_repo,
        study_plan_repo=mock_deps.study_plan_repo,
        download_service=mock_deps.download_service,
        chunking_service=mock_deps.chunking_service,
        transcription_service=mock_deps.transcription_service,
        storage_dir=tmp_path,
    )


class TestVideoServiceInitialization:
    """Tests for VideoService initialization."""

    def test_initialization_with_custom_services(self, mock_deps, tmp_path):
        """VideoService should initialize with custom service instances."""
        service = VideoService(
            video_repo=mock_deps.video_repo,
            chunk_repo=mock_deps.chunk_repo,
            transcript_repo=mock_deps.transcript_repo,
            study_plan_repo=mock_deps.study_plan_repo,
            download_service=mock_deps.download_service,
            chunking_service=mock_deps.chunking_service,
            transcription_service=mock_deps.transcription_service,
            storage_dir=tmp_path,
        )

        assert service.video_repo is mock_deps.video_repo
        assert service.chunk_repo is mock_deps.chunk_repo
        assert service.transcript_repo is mock_deps.transcript_repo
        assert service.study_plan_repo is mock_deps.study_plan_repo
        assert service.download_service is mock_deps.download_service
        assert service.chunking_service is mock_deps.chunking_service
        assert service.transcription_service is mock_deps.transcription_service

    def test_initialization_with_defaults(self, mock_deps):
        """VideoService should create default services when not provided."""
        service = VideoService(
            video_repo=mock_deps.video_repo,
            chunk_repo=mock_deps.chunk_repo,
            transcript_repo=mock_deps.transcript_repo,
            study_plan_repo=mock_deps.study_plan_repo,
        )

        assert service.download_service is not None
        assert service.chunking_service is not None
        assert service.transcription_service is not None


class TestProcessVideo:
    """Tests for process_video state progression."""

    @pytest.mark.asyncio
    async def test_process_video_not_found(self, mock_deps, video_service):
        """process_video should raise error if video not found."""
        mock_deps.video_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(VideoProcessingError) as exc_info:
            await video_service.process_video(uuid4())

        assert "not found" in str(exc_info.value.message)
        assert exc_info.value.failed_step == "lookup"

    @pytest.mark.asyncio
    async def test_process_video_pending_to_ready(self, mock_deps, video_service):
        """process_video should transition from pending to ready."""
        video = MockVideo(status="pending")
        mock_deps.video_repo.get_by_id = AsyncMock(return_value=video)
        mock_deps.video_repo.save = AsyncMock(return_value=video)
        mock_deps.download_service.download_video = AsyncMock(return_value=MagicMock())
        mock_deps.download_service.get_video_info = AsyncMock(
            return_value={"title": "Test", "duration": 600.0}
        )
        mock_deps.chunking_service.get_video_duration = AsyncMock(return_value=600.0)
        mock_deps.chunking_service.create_chunks = AsyncMock(
            return_value=[
                MagicMock(index=0, start_time=0.0, end_time=300.0, duration=300.0),
                MagicMock(index=1, start_time=300.0, end_time=600.0, duration=300.0),
            ]
        )
        mock_deps.transcript_repo.get_by_video_id = AsyncMock(return_value=MagicMock(segments=[]))
        mock_deps.transcript_repo.create = AsyncMock(return_value=MagicMock())
        mock_deps.transcription_service.transcribe = AsyncMock(
            return_value=[{"text": "Hello", "start": 0.0}]
        )
        mock_deps.study_plan_repo.create = AsyncMock(return_value=MagicMock())
        mock_deps.chunk_repo.create = AsyncMock(return_value=MagicMock())

        result = await video_service.process_video(video.id)

        assert result.status == "ready"
        assert mock_deps.download_service.download_video.called
        assert mock_deps.chunk_repo.create.called

    @pytest.mark.asyncio
    async def test_process_video_already_ready_skips(self, mock_deps, video_service):
        """process_video should skip if video already ready."""
        video = MockVideo(status="ready")
        mock_deps.video_repo.get_by_id = AsyncMock(return_value=video)
        mock_deps.video_repo.save = AsyncMock(return_value=video)

        result = await video_service.process_video(video.id)

        assert result.status == "ready"
        assert not mock_deps.download_service.download_video.called

    @pytest.mark.asyncio
    async def test_process_video_failure_sets_error(self, mock_deps, video_service):
        """process_video should set error_message on failure."""
        video = MockVideo(status="pending")
        mock_deps.video_repo.get_by_id = AsyncMock(return_value=video)
        mock_deps.video_repo.save = AsyncMock(return_value=video)
        mock_deps.download_service.download_video = AsyncMock(
            side_effect=Exception("Download failed")
        )

        with pytest.raises(Exception):
            await video_service.process_video(video.id)

        assert video.status == "failed"
        assert "Download failed" in video.error_message


class TestRetryVideo:
    """Tests for retry_video."""

    @pytest.mark.asyncio
    async def test_retry_already_complete(self, mock_deps, tmp_path):
        """retry_video should return immediately if video is ready."""
        video = MockVideo(status="ready")
        mock_deps.video_repo.get_by_id = AsyncMock(return_value=video)

        video_service = VideoService(
            video_repo=mock_deps.video_repo,
            chunk_repo=mock_deps.chunk_repo,
            transcript_repo=mock_deps.transcript_repo,
            study_plan_repo=mock_deps.study_plan_repo,
            download_service=mock_deps.download_service,
            chunking_service=mock_deps.chunking_service,
            transcription_service=mock_deps.transcription_service,
            storage_dir=tmp_path,
        )

        result = await video_service.retry_video(video.id)

        assert result.status == "ready"
        assert not mock_deps.download_service.download_video.called

    @pytest.mark.asyncio
    async def test_retry_from_downloading_complete(self, mock_deps, tmp_path):
        """retry_video should reprocess from downloading_complete state."""
        video = MockVideo(
            status="downloading_complete",
            error_message="Previous error",
            file_path="/path/to/video.webm",
        )
        mock_deps.video_repo.get_by_id = AsyncMock(return_value=video)
        mock_deps.video_repo.save = AsyncMock(return_value=video)
        mock_deps.download_service.download_video = AsyncMock(return_value=MagicMock())
        mock_deps.download_service.get_video_info = AsyncMock(
            return_value={"title": "Test", "duration": 600.0}
        )
        mock_deps.chunking_service.get_video_duration = AsyncMock(return_value=600.0)
        mock_deps.chunking_service.create_chunks = AsyncMock(
            return_value=[
                MagicMock(index=0, start_time=0.0, end_time=300.0, duration=300.0),
            ]
        )
        mock_deps.transcript_repo.get_by_video_id = AsyncMock(return_value=MagicMock(segments=[]))
        mock_deps.transcript_repo.create = AsyncMock(return_value=MagicMock())
        mock_deps.transcription_service.transcribe = AsyncMock(
            return_value=[{"text": "Hello", "start": 0.0}]
        )
        mock_deps.study_plan_repo.create = AsyncMock(return_value=MagicMock())
        mock_deps.chunk_repo.create = AsyncMock(return_value=MagicMock())

        video_service = VideoService(
            video_repo=mock_deps.video_repo,
            chunk_repo=mock_deps.chunk_repo,
            transcript_repo=mock_deps.transcript_repo,
            study_plan_repo=mock_deps.study_plan_repo,
            download_service=mock_deps.download_service,
            chunking_service=mock_deps.chunking_service,
            transcription_service=mock_deps.transcription_service,
            storage_dir=tmp_path,
        )

        result = await video_service.retry_video(video.id)

        assert not mock_deps.download_service.download_video.called
        assert mock_deps.chunking_service.create_chunks.called
        assert result.status == "ready"

    @pytest.mark.asyncio
    async def test_retry_nonexistent_video(self, mock_deps, tmp_path):
        """retry_video should raise error if video not found."""
        mock_deps.video_repo.get_by_id = AsyncMock(return_value=None)

        video_service = VideoService(
            video_repo=mock_deps.video_repo,
            chunk_repo=mock_deps.chunk_repo,
            transcript_repo=mock_deps.transcript_repo,
            study_plan_repo=mock_deps.study_plan_repo,
            download_service=mock_deps.download_service,
            chunking_service=mock_deps.chunking_service,
            transcription_service=mock_deps.transcription_service,
            storage_dir=tmp_path,
        )

        with pytest.raises(VideoProcessingError) as exc_info:
            await video_service.retry_video(uuid4())

        assert "not found" in str(exc_info.value.message)
