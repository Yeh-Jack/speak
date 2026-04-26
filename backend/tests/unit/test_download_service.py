import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from app.services.download_service import DownloadService
from app.services.exceptions import DownloadError


@pytest.fixture
def download_service(tmp_path):
    return DownloadService(output_dir=tmp_path)


@pytest.mark.asyncio
async def test_download_service_initialization(download_service, tmp_path):
    """DownloadService should initialize with output_dir."""
    assert download_service.output_dir == tmp_path
    assert (tmp_path / "videos").exists()


@pytest.mark.asyncio
async def test_download_youtube_success(download_service, tmp_path):
    """Download should return Path to downloaded file on success."""
    with patch("app.services.download_service.asyncio.get_event_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock()

        async def fake_run_in_executor(*args):
            output_file = tmp_path / "videos" / "test_video_id.webm"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.touch()
            return output_file

        mock_loop.return_value.run_in_executor.side_effect = fake_run_in_executor

        with patch("app.services.download_service.yt_dlp.YoutubeDL") as mock_ytdl:
            mock_instance = MagicMock()
            mock_instance.download.return_value = None
            mock_ytdl.return_value.__enter__.return_value = mock_instance

            result = await download_service.download_video(
                "https://www.youtube.com/watch?v=test", "test_video_id"
            )

            assert result.name == "test_video_id.webm"


@pytest.mark.asyncio
async def test_download_youtube_failure_raises_download_error(download_service):
    """Download failure should raise DownloadError."""
    with patch("app.services.download_service.asyncio.get_event_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock()

        async def fake_run_in_executor(*args):
            raise Exception("ERROR: video unavailable")

        mock_loop.return_value.run_in_executor.side_effect = fake_run_in_executor

        with pytest.raises(DownloadError) as exc_info:
            await download_service.download_video(
                "https://www.youtube.com/watch?v=invalid", "invalid_id"
            )
        assert "video unavailable" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_video_info(download_service):
    """get_video_info should return video metadata without downloading."""
    mock_info = {
        "title": "Test Video",
        "duration": 600.0,
        "thumbnail": "http://example.com/thumb.jpg",
    }

    with patch("app.services.download_service.asyncio.get_event_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock()

        async def fake_run_in_executor(*args):
            return mock_info

        mock_loop.return_value.run_in_executor.side_effect = fake_run_in_executor

        result = await download_service.get_video_info("https://www.youtube.com/watch?v=test")

        assert result["title"] == "Test Video"
        assert result["duration"] == 600.0
