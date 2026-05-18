"""Transcription service: YouTube subtitles first, Whisper fallback."""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import List, Optional

import pysubs2

from app.core.logging import get_logger
from app.services.exceptions import TranscriptionError

logger = get_logger(__name__)


class SubtitleService:
    """Service for parsing subtitle files (SRT, VTT, ASS, SSA)."""

    def parse_subtitle_file(self, subtitle_path: Path) -> List[dict]:
        """Parse subtitle file and return list of entries.

        Args:
            subtitle_path: Path to subtitle file

        Returns:
            List of dicts with start, end, text, speaker
        """
        try:
            subs = pysubs2.load(str(subtitle_path))
        except Exception as e:
            logger.error(f"Failed to parse subtitle file {subtitle_path}: {e}")
            return []

        entries = []
        for line in subs:
            entry = {
                "start": line.start / 1000.0,
                "end": line.end / 1000.0,
                "text": line.text,
                "speaker": self._extract_speaker(line.text),
            }
            entries.append(entry)

        return entries

    def _extract_speaker(self, text: str) -> Optional[str]:
        """Extract speaker label if present (e.g., 'John: Hello')."""
        if ":" in text:
            potential_speaker = text.split(":")[0].strip()
            if potential_speaker and len(potential_speaker) < 50:
                return potential_speaker
        return None


class WhisperTranscriptionService:
    """Service for transcribing audio using faster-whisper."""

    def __init__(self, model_size: str = "base"):
        """Initialize Whisper model.

        Model sizes: tiny, base, small, medium, large-v3
        CPU-friendly: tiny, base, small
        """
        self.model_size = model_size
        self._model = None

    def _load_model(self):
        """Lazy load the Whisper model."""
        if self._model is None:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8",
                cpu_threads=4,
            )

    async def transcribe(
        self,
        audio_path: Path,
        language: str = "en",
        word_timestamps: bool = True,
    ) -> List[dict]:
        """Transcribe audio file with word-level timestamps.

        Args:
            audio_path: Path to audio file
            language: Language code (default: en)
            word_timestamps: Include word-level timestamps

        Returns:
            List of transcript entries with start, end, text
        """
        self._load_model()

        segments, info = await asyncio.to_thread(
            lambda: self._model.transcribe(
                str(audio_path),
                language=language,
                word_timestamps=word_timestamps,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
            ),
        )

        results = []
        for segment in segments:
            entry = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "speaker": None,
            }
            results.append(entry)

        return results


class TranscriptionService:
    """Orchestrates transcription using strategy pattern.

    1. Use downloaded YouTube subtitles (from subtitles/ folder)
    2. Fallback to Whisper transcription
    """

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.subtitles_dir = storage_dir / "subtitles"
        self.transcripts_dir = storage_dir / "transcripts"
        self.audios_dir = storage_dir / "audios"
        self.subtitles_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.audios_dir.mkdir(parents=True, exist_ok=True)

        self.subtitle_service = SubtitleService()
        self.whisper_service = WhisperTranscriptionService(model_size="base")

    async def transcribe(
        self,
        video_path: Path,
        subtitle_paths: list[str] | None = None,
        language: str = "en",
    ) -> List[dict]:
        """Transcribe video using available methods.

        Args:
            video_path: Path to video file
            subtitle_paths: Optional list of pre-downloaded subtitle file paths
            language: Language code (default: en)

        Returns:
            List of transcript entries

        Raises:
            TranscriptionError: If all transcription methods fail
        """
        logger.info(f"Starting transcription for {video_path}")

        if subtitle_paths:
            transcript = await self._parse_subtitle_files(subtitle_paths)
            if transcript:
                logger.info(f"Using downloaded subtitles for {video_path}")
                return transcript

        transcript = await self._try_youtube_subtitles(video_path)
        if transcript:
            logger.info(f"YouTube subtitles found for {video_path}")
            return transcript

        try:
            transcript = await self._transcribe_with_whisper(video_path, language)
            logger.info(f"Whisper transcription completed for {video_path}")
            return transcript
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            raise TranscriptionError(f"Failed to transcribe video: {e}")

    async def _parse_subtitle_files(self, subtitle_paths: list[str]) -> List[dict] | None:
        """Parse downloaded subtitle files into transcript entries.

        Args:
            subtitle_paths: List of subtitle file paths from download

        Returns:
            List of transcript entries if parsing successful, None otherwise
        """
        for path_str in subtitle_paths:
            path = Path(path_str)
            if path.exists():
                entries = self.subtitle_service.parse_subtitle_file(path)
                if entries:
                    return entries
        return None

    async def _try_youtube_subtitles(self, video_path: Path) -> Optional[List[dict]]:
        """Try to extract subtitles from subtitles/ folder (yt-dlp saves them there).

        This is a fallback when subtitle_paths were not provided to transcribe().

        Returns:
            List of transcript entries if found, None otherwise
        """
        try:
            video_id = video_path.stem

            for lang in ["en", "zh-Hant"]:
                for ext in ["json3", "vtt", "srt", "ass", "lrc"]:
                    subtitle_path = self.subtitles_dir / f"{video_id}.{lang}.{ext}"
                    if subtitle_path.exists():
                        entries = self.subtitle_service.parse_subtitle_file(subtitle_path)
                        if entries:
                            return entries

            return None
        except Exception as e:
            logger.debug(f"YouTube subtitle extraction skipped: {e}")
            return None

    async def _transcribe_with_whisper(self, video_path: Path, language: str) -> List[dict]:
        """Transcribe video audio using Whisper."""
        audio_path = await self._extract_audio(video_path)

        try:
            return await self.whisper_service.transcribe(audio_path, language)
        finally:
            if audio_path.exists():
                audio_path.unlink()

    async def _extract_audio(self, video_path: Path) -> Path:
        """Extract audio from video using FFmpeg."""
        audio_path = self.audios_dir / f"{video_path.stem}_audio.wav"

        if audio_path.exists():
            return audio_path

        cmd = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-y",
            str(audio_path),
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise TranscriptionError(f"FFmpeg audio extraction failed: {stderr.decode()}")

        return audio_path

    async def save_transcript(self, video_id: str, transcript: List[dict]) -> Path:
        """Save transcript to JSON file."""
        transcript_path = self.transcripts_dir / f"{video_id}.json"

        with open(transcript_path, "w") as f:
            json.dump(transcript, f, indent=2)

        return transcript_path
