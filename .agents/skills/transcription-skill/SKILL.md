# Transcription Skill

## Description
Audio transcription using faster-whisper, subtitle parsing with pysubs2, and speaker diarization with pyannote.audio.

## When to Use
Use this skill when transcribing video audio, parsing subtitle files, or identifying speakers.

## Guidelines

### Transcription Priority
1. **YouTube subtitles** (via yt-dlp, preferred)
2. **Whisper transcription** (faster-whisper, fallback)

### Subtitle Parsing

```python
import pysubs2
from pathlib import Path
from typing import List, Optional

class SubtitleService:
    def parse_subtitle_file(self, subtitle_path: Path) -> List[dict]:
        """Parse SRT, VTT, ASS, SSA files."""
        subs = pysubs2.load(str(subtitle_path))

        entries = []
        for line in subs:
            entries.append({
                "start": line.start,  # milliseconds
                "end": line.end,      # milliseconds
                "text": line.text,
                "speaker": self._extract_speaker(line.text)
            })

        return entries

    def _extract_speaker(self, text: str) -> Optional[str]:
        """Extract speaker label if present (e.g., 'John: Hello')."""
        if ":" in text:
            potential_speaker = text.split(":")[0].strip()
            if potential_speaker and len(potential_speaker) < 50:
                return potential_speaker
        return None

    def convert_to_internal_format(
        self,
        subtitle_path: Path,
        output_path: Path
    ) -> Path:
        """Convert to standardized JSON format."""
        subs = pysubs2.load(str(subtitle_path))

        import json
        entries = []
        for line in subs:
            entries.append({
                "start_ms": line.start,
                "end_ms": line.end,
                "start": self._ms_to_timestamp(line.start),
                "end": self._ms_to_timestamp(line.end),
                "text": line.text.replace("\\N", " "),
                "speaker": self._extract_speaker(line.text)
            })

        with open(output_path, "w") as f:
            json.dump(entries, f, indent=2)

        return output_path

    def _ms_to_timestamp(self, ms: int) -> str:
        """Convert milliseconds to HH:MM:SS.mmm format."""
        hours = ms // 3600000
        minutes = (ms % 3600000) // 60000
        seconds = (ms % 60000) // 1000
        milliseconds = ms % 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
```

### Whisper Transcription

```python
from faster_whisper import WhisperModel
from pathlib import Path
from typing import List, Dict, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

class WhisperTranscriptionService:
    def __init__(self, model_size: str = "large-v3"):
        """
        Initialize Whisper model.

        Model sizes: tiny, base, small, medium, large-v1, large-v2, large-v3
        CPU-friendly: tiny, base, small, medium
        Best quality: large-v3
        """
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
            cpu_threads=4
        )
        self.executor = ThreadPoolExecutor(max_workers=2)

    async def transcribe(
        self,
        audio_path: Path,
        language: str = "en",
        word_timestamps: bool = True
    ) -> List[dict]:
        """
        Transcribe audio file with word-level timestamps.
        """
        segments, info = await asyncio.to_thread(
            lambda: self.model.transcribe(
                str(audio_path),
                language=language,
                word_timestamps=word_timestamps,
                vad_filter=True,  # Voice Activity Detection
                vad_parameters=dict(min_silence_duration_ms=500)
            )
        )

        results = []
        for segment in segments:
            entry = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "speaker": None,  # Will be populated by diarization
                "words": []
            }

            if word_timestamps and segment.words:
                entry["words"] = [
                    {
                        "word": word.word,
                        "start": word.start,
                        "end": word.end
                    }
                    for word in segment.words
                ]

            results.append(entry)

        return results

    async def transcribe_with_diarization(
        self,
        audio_path: Path,
        diarization_result: List[dict],
        language: str = "en"
    ) -> List[dict]:
        """
        Transcribe and assign speakers from diarization.
        """
        transcripts = await self.transcribe(audio_path, language)

        # Assign speakers based on time overlap
        for transcript in transcripts:
            transcript["speaker"] = self._assign_speaker(
                transcript["start"],
                transcript["end"],
                diarization_result
            )

        return transcripts

    def _assign_speaker(
        self,
        start: float,
        end: float,
        diarization: List[dict]
    ) -> Optional[str]:
        """Assign speaker based on time overlap."""
        best_speaker = None
        best_overlap = 0

        for segment in diarization:
            overlap_start = max(start, segment["start"])
            overlap_end = min(end, segment["end"])
            overlap = max(0, overlap_end - overlap_start)

            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = segment["speaker"]

        return best_speaker
```

### Speaker Diarization

```python
from pyannote.audio import Pipeline
from pathlib import Path
from typing import List, Dict
import asyncio
from concurrent.futures import ThreadPoolExecutor

class SpeakerDiarizationService:
    def __init__(self, auth_token: str):
        """
        Initialize diarization pipeline.

        Requires HuggingFace token with pyannote.audio access.
        Get token: https://huggingface.co/pyannote/speaker-diarization
        """
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=auth_token
        )
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def diarize(
        self,
        audio_path: Path,
        num_speakers: Optional[int] = None,
        min_speakers: int = 1,
        max_speakers: int = 10
    ) -> List[dict]:
        """
        Identify different speakers in audio.

        Args:
            audio_path: Path to audio file
            num_speakers: Exact number of speakers (optional)
            min_speakers: Minimum number of speakers
            max_speakers: Maximum number of speakers
        """
        diarization = await asyncio.to_thread(
            self.pipeline,
            str(audio_path),
            num_speakers=num_speakers,
            min_speakers=min_speakers,
            max_speakers=max_speakers
        )

        results = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            results.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker,
                "duration": turn.end - turn.start
            })

        return results

    def get_unique_speakers(self, diarization: List[dict]) -> List[str]:
        """Get list of unique speaker labels."""
        return sorted(set(segment["speaker"] for segment in diarization))
```

### Orchestration Strategy Pattern

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List

class TranscriptionStrategy(ABC):
    """Abstract transcription extraction strategy."""

    @abstractmethod
    async def extract(self, video_path: Path) -> Optional[List[dict]]:
        pass

    @abstractmethod
    def get_priority(self) -> int:
        """Lower number = higher priority."""
        pass

class UserSubtitleStrategy(TranscriptionStrategy):
    """User-provided SRT/VTT files - Highest priority."""

    async def extract(self, video_path: Path) -> Optional[List[dict]]:
        """Look for .srt/.vtt files next to video."""
        base_name = video_path.stem
        parent = video_path.parent

        for ext in [".srt", ".vtt", ".ass", ".ssa"]:
            subtitle_path = parent / f"{base_name}{ext}"
            if subtitle_path.exists():
                service = SubtitleService()
                return service.parse_subtitle_file(subtitle_path)
        return None

    def get_priority(self) -> int:
        return 1

class EmbeddedSubtitleStrategy(TranscriptionStrategy):
    """Embedded subtitles from video."""

    async def extract(self, video_path: Path) -> Optional[List[dict]]:
        """Extract using FFmpeg."""
        import asyncio
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".srt", delete=False) as tmp:
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-map", "0:s:0",
                tmp.name
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                service = SubtitleService()
                return service.parse_subtitle_file(Path(tmp.name))
            return None

    def get_priority(self) -> int:
        return 2

class WhisperStrategy(TranscriptionStrategy):
    """Whisper transcription - Lowest priority."""

    def __init__(self, whisper_service: WhisperTranscriptionService):
        self.whisper = whisper_service

    async def extract(self, video_path: Path) -> Optional[List[dict]]:
        """Use faster-whisper."""
        import tempfile

        # Extract audio first
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_tmp:
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                audio_tmp.name
            ]

            process = await asyncio.create_subprocess_exec(*cmd)
            await process.communicate()

            if process.returncode == 0:
                return await self.whisper.transcribe(Path(audio_tmp.name))
            return None

    def get_priority(self) -> int:
        return 3

class TranscriptService:
    """Orchestrates subtitle extraction using strategies."""

    def __init__(self):
        self.strategies: List[TranscriptionStrategy] = []

    def add_strategy(self, strategy: TranscriptionStrategy):
        self.strategies.append(strategy)
        self.strategies.sort(key=lambda s: s.get_priority())

    async def get_transcript(self, video_path: Path) -> List[dict]:
        for strategy in self.strategies:
            transcript = await strategy.extract(video_path)
            if transcript:
                return transcript
        raise ValueError("No transcript available")
```

## Dependencies
```
# Subtitle parsing
pysubs2>=1.6.0

# Whisper transcription
faster-whisper>=0.10.0

# Speaker diarization (optional - requires HF token)
pyannote.audio>=3.1.0
```

## Environment Variables
```
HF_AUTH_TOKEN=your_huggingface_token_for_pyannote
```

## Notes
- faster-whisper is CPU-friendly and faster than openai-whisper
- pyannote.audio requires HuggingFace authentication
- Word-level timestamps help with synchronized subtitle display
- Speaker diarization helps users practice specific characters
