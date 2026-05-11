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

    async def download_video(self, youtube_url: str, video_id: str) -> dict:
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
            info = await asyncio.to_thread(
                self._download_sync, youtube_url, str(output_path)
            )
        except Exception as e:
            logger.error(f"Download failed for {video_id}: {e}")
            raise DownloadError(f"Failed to download video: {e}")

        if not output_path.exists():
            raise DownloadError(f"Download completed but file not found: {output_path}")

        logger.info(f"Video downloaded successfully: {output_path}")
        return info

    def _download_sync(self, youtube_url: str, output_path: str) -> dict:
        """Synchronous download using yt-dlp.
                Subtitle formats :
                    Potential choices:
                        1. json3 : For NLP/AI transcript processing.
                        2. lrc : with timestamped lines.
        | Format          | Type                      | Best Use                | Notes                                 |
        | --------------- | ------------------------- | ----------------------- | ------------------------------------- |
        | `vtt`           | WebVTT text               | General subtitle usage  | Most common and clean                 |
        | `srt`           | SubRip text               | Media players/editors   | Widely supported                      |
        | `ass`           | Advanced SubStation Alpha | Styled subtitles        | Supports colors/positioning           |
        | `lrc`           | Lyric format              | Karaoke/audio sync      | Timestamped lines                     |
        | `ttml` / `dfxp` | XML subtitles             | Broadcast/pro workflows | Structured XML                        |
        | `srv1`          | YouTube XML               | Basic auto captions     | Older/simple XML                      |
        | `srv2`          | YouTube XML               | Better timing           | More structured                       |
        | `srv3`          | YouTube XML               | Rich formatting         | Newer YouTube XML                     |
        | `json3`         | YouTube JSON              | Programmatic parsing    | Best for NLP/AI/transcript processing |
        """
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "format": "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best",
            "outtmpl": output_path.replace(".webm", ""),
            # --- Download subtitles
            "writesubtitles": True,
            "writeautomaticsub": True,
            # 1. Choose languages
            "subtitleslangs": ["en", "zh-Hant"],
            # 2. Preferred subtitle format
            "subtitlesformat": "json3/vtt/lrc/ass",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ydl.download([youtube_url])
            info = ydl.extract_info(youtube_url, download=True)
            return info

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

        subtitles = info.get("subtitles", {}) or {}
        automatic_captions = info.get("automatic_captions", {}) or {}
        formats = info.get("formats", []) or []

        available_formats = []
        for f in formats:
            if f.get("ext") in ("webm", "mp4"):
                available_formats.append(
                    {
                        "format_id": f.get("format_id"),
                        "ext": f.get("ext"),
                        "resolution": f.get("resolution")
                        or f"{f.get('width', 0)}x{f.get('height', 0)}",
                        "filesize": f.get("filesize"),
                        "fps": f.get("fps"),
                        "vcodec": f.get("vcodec"),
                        "acodec": f.get("acodec"),
                    }
                )

        return {
            "title": info.get("title", "Unknown"),
            "description": info.get("description"),
            "duration": info.get("duration", 0.0),
            "thumbnail": info.get("thumbnail"),
            "uploader": info.get("uploader"),
            "upload_date": info.get("upload_date"),
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "categories": info.get("categories"),
            "tags": info.get("tags"),
            "language": info.get("language"),
            "subtitles": list(subtitles.keys()),
            "automatic_captions": list(automatic_captions.keys()),
            "available_formats": available_formats,
        }
