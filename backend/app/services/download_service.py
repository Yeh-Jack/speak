"""YouTube video download service using yt-dlp."""

import asyncio
from pathlib import Path
from typing import Optional

import yt_dlp

from app.core.logging import get_logger
from app.services.exceptions import DownloadError

logger = get_logger(__name__)


class DownloadService:
    """Service for downloading YouTube videos using yt-dlp."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.videos_dir = output_dir / "videos"
        self.subtitles_dir = output_dir / "subtitles"
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        self.subtitles_dir.mkdir(parents=True, exist_ok=True)

    async def download_video(self, youtube_url: str, video_id: str) -> dict:
        """Download video and subtitles from YouTube URL.

        Args:
            youtube_url: Full YouTube URL
            video_id: Unique identifier for the video

        Returns:
            dict with video info including:
                - video_path: Path to downloaded video file
                - subtitle_paths: List of subtitle file paths
                - title, duration, etc.

        Raises:
            DownloadError: If download fails
        """
        logger.info(f"Downloading video {video_id} from {youtube_url}")

        try:
            info = await asyncio.to_thread(self._download_sync, youtube_url, video_id)
        except Exception as e:
            logger.error(f"Download failed for {video_id}: {e}")
            raise DownloadError(f"Failed to download video: {e}")

        video_path = Path(info.get("video_path", self.videos_dir / f"{video_id}.webm"))
        if not video_path.exists():
            raise DownloadError(f"Download completed but file not found: {video_path}")

        logger.info(f"Video downloaded successfully: {video_path}")
        logger.info(f"Subtitles downloaded: {info.get('subtitle_paths', [])}")
        return info

    def _download_sync(self, youtube_url: str, video_id: str) -> dict:
        """Synchronous download using yt-dlp.

        Downloads video and auto-generated subtitles simultaneously.
        Subtitles are saved to the subtitles/ folder after download.
        The transcription service will look for them during processing.

        If subtitle download fails (e.g., due to rate limiting), the video
        is still returned successfully - transcription will fall back to Whisper.

        Subtitle formats:
            | Format          | Type                      | Best Use                |
            | --------------- | ------------------------- | ----------------------- |
            | `json3`         | YouTube JSON              | NLP/AI/transcript proc  |
            | `vtt`           | WebVTT text               | General subtitle usage  |
            | `srt`           | SubRip text               | Media players/editors   |
            | `ass`           | Advanced SubStation Alpha | Styled subtitles        |
            | `lrc`           | Lyric format              | Karaoke/audio sync      |

        Returns:
            dict with video info including 'subtitle_paths' list
        """
        video_output = str(self.videos_dir / video_id)
        video_path = self.videos_dir / f"{video_id}.webm"

        subtitleslangs = ["en"]
        ydl_opts = {
            "quiet": True,
            "no_warnings": False,
            "extract_flat": False,
            "format": "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best",
            "outtmpl": video_output,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": subtitleslangs,
            "subtitlesformat": "json3/vtt/lrc/ass/srt",
        }

        info = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
        except Exception as e:
            if not video_path.exists():
                logger.error(f"Video download failed: {e}")
                raise DownloadError(f"Video download failed: {e}")
            logger.warning(f"Subtitle download failed (will fallback to Whisper): {e}")

        if not video_path.exists():
            logger.error(f"Video file not found after download")
            raise DownloadError("Video file not found after download - download may have failed")

        subtitle_paths = []
        for lang in subtitleslangs:
            for ext in ["json3", "vtt", "srt", "ass", "lrc"]:
                path = self.videos_dir / f"{video_id}.{lang}.{ext}"
                if path.exists():
                    subtitle_paths.append(str(path))
                    moved_path = self.subtitles_dir / f"{video_id}.{lang}.{ext}"
                    path.rename(moved_path)
                    logger.info(f"Moved subtitle to: {moved_path}")

        info["subtitle_paths"] = subtitle_paths
        info["video_path"] = str(video_path)
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
