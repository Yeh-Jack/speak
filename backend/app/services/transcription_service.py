"""Transcription service: Dual transcript system with YouTube subtitles + Whisper."""

import asyncio
import json
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
        if subtitle_path.suffix == ".json3" or subtitle_path.suffix == ".json":
            return self._parse_youtube_json3(subtitle_path)

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

    def _parse_youtube_json3(self, subtitle_path: Path) -> List[dict]:
        """Parse YouTube JSON3 subtitle format.

        YouTube JSON3 structure:
        {
            "events": [
                {
                    "tStartMs": 0,
                    "dDurationMs": 132940,
                    "segs": [
                        {"utf8": "Washington"},
                        {"utf8": " D.C.,", "tOffsetMs": 840}
                    ]
                }
            ]
        }
        """
        try:
            with open(subtitle_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read JSON3 file {subtitle_path}: {e}")
            return []

        entries = []
        events = data.get("events", [])
        for event in events:
            t_start_ms = event.get("tStartMs", 0)
            d_duration_ms = event.get("dDurationMs", 0)
            segs = event.get("segs", [])

            if not segs:
                continue

            start = t_start_ms / 1000.0
            end = (t_start_ms + d_duration_ms) / 1000.0

            text_parts = []
            for seg in segs:
                utf8 = seg.get("utf8", "")
                text_parts.append(utf8)

            text = "".join(text_parts).strip()
            if text:
                entry = {
                    "start": start,
                    "end": end,
                    "text": text,
                    "speaker": self._extract_speaker(text),
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
    """Orchestrates dual transcription.

    1. Always runs Whisper transcription
    2. Also tries to get YouTube subtitles if available
    3. Both are stored separately and user can choose which to use
    """

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.subtitles_dir = storage_dir / "subtitles"
        self.transcripts_dir = storage_dir / "transcripts"
        self.youtube_transcripts_dir = storage_dir / "transcripts" / "youtube"
        self.whisper_transcripts_dir = storage_dir / "transcripts" / "whisper"
        self.audios_dir = storage_dir / "audios"
        self.subtitles_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.youtube_transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.whisper_transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.audios_dir.mkdir(parents=True, exist_ok=True)

        self.subtitle_service = SubtitleService()
        self.whisper_service = WhisperTranscriptionService(model_size="base")

    async def get_youtube_transcript(self, video_path: Path) -> Optional[List[dict]]:
        """Get YouTube subtitle transcript if available.

        Args:
            video_path: Path to video file

        Returns:
            YouTube transcript entries if found, None otherwise
        """
        try:
            video_id = video_path.stem

            for lang in ["en", "zh-Hant"]:
                for ext in ["json3", "vtt", "srt", "ass", "lrc"]:
                    subtitle_path = self.subtitles_dir / f"{video_id}.{lang}.{ext}"
                    if subtitle_path.exists():
                        entries = self.subtitle_service.parse_subtitle_file(subtitle_path)
                        if entries:
                            logger.info(f"YouTube subtitles found for {video_path}")
                            return entries

            return None
        except Exception as e:
            logger.debug(f"YouTube subtitle extraction skipped: {e}")
            return None

    async def transcribe_with_whisper(self, video_path: Path, language: str = "en") -> List[dict]:
        """Transcribe video audio using Whisper.

        Args:
            video_path: Path to video file
            language: Language code (default: en)

        Returns:
            Whisper transcript entries

        Raises:
            TranscriptionError: If Whisper transcription fails
        """
        try:
            audio_path = await self._extract_audio(video_path)
            try:
                transcript = await self.whisper_service.transcribe(audio_path, language)
                logger.info(f"Whisper transcription completed for {video_path}")
                await self.save_transcript(video_path.stem, transcript, source="whisper")
                return transcript
            finally:
                if audio_path.exists():
                    audio_path.unlink()
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            raise TranscriptionError(f"Whisper transcription failed: {e}")

    async def get_dual_transcripts(
        self,
        video_path: Path,
        subtitle_paths: dict[str, list[str]] | None = None,
        language: str = "en",
    ) -> tuple[Optional[List[dict]], Optional[List[dict]], List[dict]]:
        """Get YouTube author, YouTube auto, and Whisper transcripts.

        Always runs Whisper. Tries to get YouTube subtitles if available.

        Args:
            video_path: Path to video file
            subtitle_paths: Dict with 'author' and 'auto' subtitle file paths
            language: Language code (default: en)

        Returns:
            Tuple of (youtube_author_transcript, youtube_auto_transcript, whisper_transcript)
            youtube_author_transcript may be None if not available
            youtube_auto_transcript may be None if not available
        """
        logger.info(f"Starting triple transcription for {video_path}")

        youtube_author_transcript = None
        youtube_auto_transcript = None

        if subtitle_paths:
            author_paths = subtitle_paths.get("author", [])
            auto_paths = subtitle_paths.get("auto", [])

            if author_paths:
                youtube_author_transcript = await self._parse_subtitle_files(author_paths)

            if auto_paths:
                youtube_auto_transcript = await self._parse_subtitle_files(auto_paths)

        if not youtube_author_transcript and not youtube_auto_transcript:
            youtube_author_transcript = await self.get_youtube_transcript(video_path)

        whisper_transcript = await self.transcribe_with_whisper(video_path, language)

        return youtube_author_transcript, youtube_auto_transcript, whisper_transcript

    async def _parse_subtitle_files(self, subtitle_paths: list[str]) -> Optional[List[dict]]:
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

    async def _transcribe_with_whisper(self, video_path: Path, language: str) -> List[dict]:
        """Transcribe video audio using Whisper (legacy method for compatibility)."""
        return await self.transcribe_with_whisper(video_path, language)

    async def transcribe(
        self,
        video_path: Path,
        subtitle_paths: list[str] | None = None,
        language: str = "en",
    ) -> List[dict]:
        """Transcribe video (legacy method - use get_dual_transcripts instead).

        Args:
            video_path: Path to video file
            subtitle_paths: Optional list of pre-downloaded subtitle file paths
            language: Language code (default: en)

        Returns:
            Whisper transcript entries (for backward compatibility)
        """
        return await self.transcribe_with_whisper(video_path, language)

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

    async def save_transcript(
        self, video_id: str, transcript: List[dict], source: str = "whisper"
    ) -> Path:
        """Save transcript to JSON file.

        Args:
            video_id: Video ID
            transcript: List of transcript entries
            source: 'youtube' or 'whisper'
        """
        if source == "youtube":
            transcript_dir = self.youtube_transcripts_dir
        else:
            transcript_dir = self.whisper_transcripts_dir

        transcript_dir.mkdir(parents=True, exist_ok=True)
        transcript_path = transcript_dir / f"{video_id}.json"

        with open(transcript_path, "w") as f:
            json.dump(transcript, f, indent=2)

        return transcript_path
