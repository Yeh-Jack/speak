"""Tests for DownloadService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from app.services.download_service import DownloadService
from app.services.exceptions import DownloadError


@pytest.fixture
def download_service(tmp_path):
    """Create DownloadService with temp directory."""
    return DownloadService(output_dir=tmp_path)


class TestDownloadServiceInitialization:
    """Tests for DownloadService initialization."""

    @pytest.mark.asyncio
    async def test_initialization_creates_directories(self, tmp_path):
        """DownloadService should create videos and subtitles directories."""
        service = DownloadService(output_dir=tmp_path)
        assert service.output_dir == tmp_path
        assert service.videos_dir == tmp_path / "videos"
        assert service.subtitles_dir == tmp_path / "subtitles"
        assert service.videos_dir.exists()
        assert service.subtitles_dir.exists()


class TestDownloadVideo:
    """Tests for download_video method."""

    @pytest.mark.asyncio
    async def test_download_video_success(self, download_service, tmp_path):
        """download_video should return video info dict on success."""
        mock_info = {
            "title": "Test Video",
            "duration": 600.0,
            "thumbnail": "http://example.com/thumb.jpg",
            "video_path": str(tmp_path / "videos" / "test_id.webm"),
            "subtitle_paths": {"author": [], "auto": []},
            "uploader": "Test Channel",
            "upload_date": "20240101",
            "view_count": 1000,
            "like_count": 50,
        }

        (tmp_path / "videos" / "test_id.webm").touch()

        with patch.object(
            download_service, "_download_sync", return_value=mock_info
        ) as mock_sync:
            result = await download_service.download_video(
                "https://www.youtube.com/watch?v=test", "test_id"
            )

            assert result["title"] == "Test Video"
            assert result["duration"] == 600.0
            assert result["video_path"] == str(tmp_path / "videos" / "test_id.webm")
            mock_sync.assert_called_once_with(
                "https://www.youtube.com/watch?v=test", "test_id"
            )

    @pytest.mark.asyncio
    async def test_download_video_file_not_found_raises_error(self, download_service):
        """download_video should raise DownloadError if file doesn't exist after download."""
        mock_info = {
            "title": "Test Video",
            "duration": 600.0,
            "video_path": str(Path("/nonexistent/test_id.webm")),
            "subtitle_paths": {"author": [], "auto": []},
        }

        with patch.object(download_service, "_download_sync", return_value=mock_info):
            with pytest.raises(DownloadError) as exc_info:
                await download_service.download_video(
                    "https://www.youtube.com/watch?v=test", "test_id"
                )
            assert "file not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_download_video_download_error_raises_download_error(self, download_service):
        """download_video should raise DownloadError when sync download fails."""
        with patch.object(
            download_service,
            "_download_sync",
            side_effect=DownloadError("Video unavailable"),
        ):
            with pytest.raises(DownloadError) as exc_info:
                await download_service.download_video(
                    "https://www.youtube.com/watch?v=invalid", "invalid_id"
                )
            assert "Failed to download video" in str(exc_info.value)


class TestGetVideoInfo:
    """Tests for get_video_info method."""

    @pytest.mark.asyncio
    async def test_get_video_info_success(self, download_service):
        """get_video_info should return video metadata without downloading."""
        mock_info = {
            "title": "Test Video",
            "duration": 600.0,
            "thumbnail": "http://example.com/thumb.jpg",
            "description": "A test video",
            "uploader": "Test Channel",
            "upload_date": "20240101",
            "view_count": 1000,
            "like_count": 50,
            "categories": ["Education"],
            "tags": ["test", "video"],
            "language": "en",
            "subtitles": ["en"],
            "automatic_captions": ["en"],
            "available_formats": [],
        }

        with patch.object(
            download_service, "_get_info_sync", return_value=mock_info
        ) as mock_sync:
            result = await download_service.get_video_info(
                "https://www.youtube.com/watch?v=test"
            )

            assert result["title"] == "Test Video"
            assert result["duration"] == 600.0
            assert result["thumbnail"] == "http://example.com/thumb.jpg"
            assert result["uploader"] == "Test Channel"
            mock_sync.assert_called_once_with("https://www.youtube.com/watch?v=test")

    @pytest.mark.asyncio
    async def test_get_video_info_error_returns_defaults(self, download_service):
        """get_video_info should return defaults if extraction fails."""
        with patch.object(
            download_service, "_get_info_sync", side_effect=Exception("Network error")
        ):
            result = await download_service.get_video_info(
                "https://www.youtube.com/watch?v=test"
            )

            assert result["title"] == "Unknown"
            assert result["duration"] == 0.0