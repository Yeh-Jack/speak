"""YouTube video download service using yt-dlp."""

import asyncio
import logging
from pathlib import Path
from typing import Optional

import yt_dlp

from app.services.exceptions import DownloadError

logger = logging.getLogger(__name__)


class DownloadService:
    """Service for downloading YouTube videos using yt-dlp."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.videos_dir = output_dir / "videos"
        self.videos_dir.mkdir(parents=True, exist_ok=True)

    async def download_video(self, youtube_url: str, video_id: str) -> Path:
        """Download video from YouTube URL.

        Args:
            youtube_url: Full YouTube URL
            video_id: Unique identifier for the video

        Returns:
            Path to downloaded video file

        Raises:
            DownloadError: If download fails
        """
        output_path = self.videos_dir / f"{video_id}.webm"

        logger.info(f"Downloading video {video_id} from {youtube_url}")

        try:
            await asyncio.to_thread(self._download_sync, youtube_url, str(output_path))
        except Exception as e:
            logger.error(f"Download failed for {video_id}: {e}")
            raise DownloadError(f"Failed to download video: {e}")

        if not output_path.exists():
            raise DownloadError(f"Download completed but file not found: {output_path}")

        logger.info(f"Video downloaded successfully: {output_path}")
        return output_path

    def _download_sync(self, youtube_url: str, output_path: str) -> None:
        """Synchronous download using yt-dlp."""
        ydl_opts = {
            "format": "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best",
            "outtmpl": output_path.replace(".webm", ""),
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

    async def get_video_info(self, youtube_url: str) -> dict:
        """Get video metadata without downloading.

        Args:
            youtube_url: Full YouTube URL

        Returns:
            Dict with video metadata (title, duration, etc.)
        """
        try:
            return await asyncio.to_thread(self._get_info_sync, youtube_url)
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return {"title": "Unknown", "duration": 0.0}

    def _get_info_sync(self, youtube_url: str) -> dict:
        """Synchronous info extraction using yt-dlp."""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)

        return {
            "title": info.get("title", "Unknown"),
            "duration": info.get("duration", 0.0),
            "thumbnail": info.get("thumbnail"),
        }
