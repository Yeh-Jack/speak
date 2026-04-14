# Video Processing Skill

## Description

Video processing with FFmpeg for chunking, format conversion, and subtitle extraction. Supports both **time-based** and **character-based** chunking modes. YouTube video downloading with yt-dlp. Speaker diarization for character-based learning.

## When to Use

Use this skill when working with:
- Video uploads and chunking
- Time-based or character-based video segmentation
- Speaker diarization and character selection
- YouTube video downloads
- FFmpeg video/audio processing

## Chunking Modes

### Mode A: Time-Based (Default)
- Fixed duration chunks (default 5 minutes)
- Sequential learning path
- Configurable: 1-10 minutes per chunk

### Mode B: Character-Based (Scene-Based)
- Extract scenes where selected character speaks
- Merge consecutive segments (<2s gap)
- Split long scenes (>10 min) at natural pauses
- Includes overlapping speech

---

## Time-Based Chunking

### FFmpeg Commands

#### Split Video into Chunks (5 min default)
```bash
# Split without re-encoding (fast)
ffmpeg -i input.mp4 -c copy -map 0 -segment_time 300 -f segment chunk_%03d.mp4

# Split with custom duration (e.g., 10 minutes = 600 seconds)
ffmpeg -i input.mp4 -c copy -map 0 -segment_time 600 -f segment chunk_%03d.mp4
```

#### Extract Audio for Whisper
```bash
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 audio.wav
```

#### Extract Embedded Subtitles
```bash
ffmpeg -i input.mp4 -map 0:s:0 subtitle.srt
```

### Python Implementation

```python
import asyncio
import subprocess
from pathlib import Path
from typing import List
from uuid import UUID

class TimeBasedChunkingService:
    """Split video into fixed-duration chunks."""

    def __init__(self, storage_service):
        self.storage = storage_service

    async def chunk_video(
        self,
        video_path: Path,
        chunk_duration: int = 300,  # 5 minutes
    ) -> List[Path]:
        """Split video into chunks without re-encoding."""
        output_pattern = video_path.parent / f"chunk_%03d{video_path.suffix}"

        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-c", "copy",  # No re-encoding
            "-map", "0",
            "-segment_time", str(chunk_duration),
            "-f", "segment",
            str(output_pattern)
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise VideoProcessingError(f"FFmpeg failed: {stderr.decode()}")

        return sorted(video_path.parent.glob(f"chunk_*{video_path.suffix}"))
```

---

## Character-Based Chunking

### Database Schema

#### speakers Table
```python
class Speaker(Base):
    """Detected speaker in a video."""
    __tablename__ = "speakers"

    id: UUID
    video_id: UUID
    speaker_label: str        # "SPEAKER_00", "SPEAKER_01"
    display_name: Optional[str]
    total_speaking_time: float
    speaking_percentage: float
    sample_text: Optional[str]
    created_at: datetime
```

#### video_chunks Table (Character Fields)
```python
class VideoChunk(Base):
    """Video chunk with character support."""
    __tablename__ = "video_chunks"

    id: UUID
    video_id: UUID
    chunk_index: int
    start_time: float
    end_time: float
    duration: float
    file_path: str

    # Character-based fields
    chunk_type: str                    # 'time_based' or 'character_based'
    primary_speaker_id: Optional[UUID]
    speaker_ids: List[UUID]            # Overlapping speakers
    scene_context: Optional[str]       # Surrounding dialogue
    transcript: List[dict]             # [{speaker, text, start, end}]

    status: str
    created_at: datetime
```

### Speaker Diarization Service

```python
from pyannote.audio import Pipeline
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SpeakerSegment:
    speaker: str      # "SPEAKER_00"
    start: float      # Start time in seconds
    end: float        # End time in seconds
    text: Optional[str] = None

@dataclass
class SpeakerProfile:
    speaker_label: str
    display_name: Optional[str]
    total_speaking_time: float
    speaking_percentage: float
    sample_text: Optional[str]
    segment_count: int

class SpeakerDiarizationService:
    """
    Extract speakers from video using pyannote.audio.
    Requires HF_TOKEN environment variable.
    """

    def __init__(self, auth_token: Optional[str] = None):
        self.auth_token = auth_token or os.getenv("HF_TOKEN")
        self._pipeline = None

    async def _load_pipeline(self):
        """Lazy load pyannote pipeline."""
        if self._pipeline is None:
            from pyannote.audio import Pipeline
            self._pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.auth_token
            )

    async def diarize(
        self,
        audio_path: Path,
        num_speakers: Optional[int] = None,
        min_speakers: int = 1,
        max_speakers: int = 10
    ) -> List[SpeakerSegment]:
        """Identify different speakers in audio."""
        await self._load_pipeline()

        diarization = self._pipeline(
            str(audio_path),
            num_speakers=num_speakers,
            min_speakers=min_speakers,
            max_speakers=max_speakers
        )

        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append(SpeakerSegment(
                speaker=speaker,
                start=turn.start,
                end=turn.end
            ))

        return segments

    async def get_speaker_profiles(
        self,
        segments: List[SpeakerSegment],
        video_duration: float
    ) -> List[SpeakerProfile]:
        """Calculate statistics for each speaker."""
        from collections import defaultdict

        speaker_stats = defaultdict(lambda: {
            "total_time": 0.0,
            "segments": [],
            "text_samples": []
        })

        for segment in segments:
            speaker_stats[segment.speaker]["total_time"] += segment.end - segment.start
            speaker_stats[segment.speaker]["segments"].append(segment)
            if segment.text:
                speaker_stats[segment.speaker]["text_samples"].append(segment.text)

        profiles = []
        for speaker, stats in speaker_stats.items():
            total_time = stats["total_time"]
            percentage = (total_time / video_duration) * 100 if video_duration > 0 else 0

            profiles.append(SpeakerProfile(
                speaker_label=speaker,
                display_name=None,
                total_speaking_time=total_time,
                speaking_percentage=round(percentage, 2),
                sample_text=" ".join(stats["text_samples"][:3]) if stats["text_samples"] else None,
                segment_count=len(stats["segments"])
            ))

        profiles.sort(key=lambda p: p.total_speaking_time, reverse=True)
        return profiles
```

### Character Chunking Service

```python
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

@dataclass
class ChunkingConfig:
    """Configuration for character-based chunking."""
    merge_gap_threshold: float = 2.0   # Merge segments within 2s
    max_chunk_duration: float = 600.0  # 10 minutes maximum
    min_chunk_duration: float = 0.0    # No minimum
    pause_threshold: float = 0.5       # Natural pause > 0.5s

@dataclass
class SceneChunk:
    """A character-based video chunk."""
    index: int
    start_time: float
    end_time: float
    duration: float
    primary_speaker: str
    speaker_ids: List[str]  # All speakers (overlapping)
    transcript_segments: List[SpeakerSegment]
    scene_context: str      # Surrounding dialogue

class CharacterChunkingService:
    """Scene-based chunking for character dialogue."""

    def __init__(self, config: Optional[ChunkingConfig] = None):
        self.config = config or ChunkingConfig()

    async def create_character_chunks(
        self,
        video_path: Path,
        speaker_id: str,
        speaker_segments: List[SpeakerSegment],
        all_segments: List[SpeakerSegment]
    ) -> List[SceneChunk]:
        """
        Create character-based chunks.

        Algorithm:
        1. Filter segments for selected speaker
        2. Merge consecutive segments (if gap < threshold)
        3. Split if exceeds max duration (at natural pause)
        4. Build scene context
        """
        # Step 1: Filter for selected speaker
        character_segments = [s for s in speaker_segments if s.speaker == speaker_id]
        if not character_segments:
            return []

        # Step 2: Merge consecutive segments
        merged = self._merge_consecutive_segments(character_segments)

        # Step 3: Split long scenes
        final_segments = []
        for segment in merged:
            if segment.end - segment.start > self.config.max_chunk_duration:
                split = self._split_long_scene(segment, all_segments)
                final_segments.extend(split)
            else:
                final_segments.append(segment)

        # Step 4: Build chunks with context
        chunks = []
        for idx, segment in enumerate(final_segments):
            context = self._build_scene_context(segment, all_segments)
            overlapping = self._get_overlapping_speakers(segment, all_segments)

            chunks.append(SceneChunk(
                index=idx,
                start_time=segment.start,
                end_time=segment.end,
                duration=segment.end - segment.start,
                primary_speaker=speaker_id,
                speaker_ids=overlapping,
                transcript_segments=[segment],
                scene_context=context
            ))

        return chunks

    def _merge_consecutive_segments(
        self,
        segments: List[SpeakerSegment]
    ) -> List[SpeakerSegment]:
        """Merge segments where gap < threshold."""
        if not segments:
            return []

        sorted_segments = sorted(segments, key=lambda s: s.start)
        merged = [sorted_segments[0]]

        for current in sorted_segments[1:]:
            last = merged[-1]
            gap = current.start - last.end

            if gap <= self.config.merge_gap_threshold:
                # Merge: extend end time, combine text
                last.end = current.end
                if current.text:
                    last.text = (last.text or "") + " " + current.text
            else:
                merged.append(current)

        return merged

    def _split_long_scene(
        self,
        segment: SpeakerSegment,
        all_segments: List[SpeakerSegment],
        num_parts: Optional[int] = None
    ) -> List[SpeakerSegment]:
        """Split scene exceeding max duration at natural pause points."""
        duration = segment.end - segment.start
        if duration <= self.config.max_chunk_duration:
            return [segment]

        # Calculate number of parts
        if num_parts is None:
            num_parts = int(duration / self.config.max_chunk_duration) + 1
        target_duration = duration / num_parts

        split_points = []
        for i in range(1, num_parts):
            target_time = segment.start + (target_duration * i)
            pause_point = self._find_nearest_pause(target_time, all_segments)
            split_points.append(pause_point)

        # Create split segments
        parts = []
        prev_end = segment.start
        for split_point in split_points:
            parts.append(SpeakerSegment(
                speaker=segment.speaker,
                start=prev_end,
                end=split_point
            ))
            prev_end = split_point

        parts.append(SpeakerSegment(
            speaker=segment.speaker,
            start=prev_end,
            end=segment.end
        ))

        return parts

    def _find_nearest_pause(
        self,
        target_time: float,
        all_segments: List[SpeakerSegment],
        window: float = 5.0
    ) -> float:
        """Find natural pause point near target time."""
        min_time = target_time - window
        max_time = target_time + window

        gaps = []
        for i in range(len(all_segments) - 1):
            current_end = all_segments[i].end
            next_start = all_segments[i + 1].start

            if current_end >= min_time and next_start <= max_time:
                gap_duration = next_start - current_end
                if gap_duration >= self.config.pause_threshold:
                    gap_center = current_end + (gap_duration / 2)
                    distance = abs(gap_center - target_time)
                    gaps.append((distance, gap_center))

        if gaps:
            gaps.sort(key=lambda x: x[0])
            return gaps[0][1]

        return target_time

    def _build_scene_context(
        self,
        segment: SpeakerSegment,
        all_segments: List[SpeakerSegment],
        context_window: float = 30.0
    ) -> str:
        """Build scene context with surrounding dialogue."""
        context_start = max(0, segment.start - context_window)
        context_end = segment.end + context_window

        context_segments = [
            s for s in all_segments
            if s.start >= context_start and s.end <= context_end and s.text
        ]

        return " ".join([
            f"[{s.speaker}]: {s.text}"
            for s in sorted(context_segments, key=lambda x: x.start)
        ])

    def _get_overlapping_speakers(
        self,
        segment: SpeakerSegment,
        all_segments: List[SpeakerSegment]
    ) -> List[str]:
        """Find all speakers active during this segment (overlapping speech)."""
        overlapping = set()
        for s in all_segments:
            if s.start < segment.end and s.end > segment.start:
                overlapping.add(s.speaker)
        return list(overlapping)

    async def extract_video_segment(
        self,
        input_path: Path,
        output_path: Path,
        start_time: float,
        end_time: float
    ) -> Path:
        """Extract video segment using FFmpeg without re-encoding."""
        cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-ss", str(start_time),
            "-t", str(end_time - start_time),
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            "-y",
            str(output_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
```

### Video Service with Chunking Support

```python
class VideoService:
    """Video processing with character-based chunking."""

    def __init__(
        self,
        video_repo,
        chunk_repo,
        speaker_repo,
        diarization_service: SpeakerDiarizationService,
        chunking_service: CharacterChunkingService
    ):
        self.video_repo = video_repo
        self.chunk_repo = chunk_repo
        self.speaker_repo = speaker_repo
        self.diarization = diarization_service
        self.chunking = chunking_service

    async def process_video(self, video_id: UUID) -> None:
        """
        Full pipeline:
        1. Extract audio
        2. Speaker diarization
        3. Transcription
        4. Store speaker profiles
        5. Create default time-based chunks
        """
        video = await self.video_repo.get_by_id(video_id)

        # 1. Extract audio
        audio_path = await self._extract_audio(video.file_path)

        # 2. Speaker diarization
        segments = await self.diarization.diarize(audio_path)

        # 3. Transcribe segments
        segments = await self._transcribe_segments(segments, audio_path)

        # 4. Store speaker profiles
        profiles = await self.diarization.get_speaker_profiles(
            segments, video.duration
        )
        for profile in profiles:
            await self.speaker_repo.create(video_id, profile)

        # 5. Create default time-based chunks
        await self._create_time_based_chunks(video_id, video.file_path)

    async def switch_chunking_mode(
        self,
        video_id: UUID,
        user_id: UUID,
        mode: str,  # 'time_based' or 'character_based'
        speaker_id: Optional[UUID] = None
    ) -> List[VideoChunk]:
        """Switch between chunking modes."""
        # Store preference
        await self._set_user_preference(user_id, video_id, mode, speaker_id)

        if mode == "time_based":
            return await self.chunk_repo.get_by_video(video_id, "time_based")

        elif mode == "character_based":
            if not speaker_id:
                raise ValueError("speaker_id required for character_based mode")

            # Check if exists
            existing = await self.chunk_repo.get_by_video(video_id, "character_based")
            if existing:
                return existing

            # Generate new chunks
            return await self._create_character_based_chunks(video_id, speaker_id)

        else:
            raise ValueError(f"Invalid chunking mode: {mode}")

    async def _create_character_based_chunks(
        self,
        video_id: UUID,
        speaker_id: UUID
    ) -> List[VideoChunk]:
        """Generate character-based chunks on demand."""
        video = await self.video_repo.get_by_id(video_id)
        speaker = await self.speaker_repo.get_by_id(speaker_id)
        all_segments = await self.speaker_repo.get_segments(video_id)

        # Create chunks
        scene_chunks = await self.chunking.create_character_chunks(
            video_path=Path(video.file_path),
            speaker_id=speaker.speaker_label,
            speaker_segments=all_segments,
            all_segments=all_segments
        )

        # Extract and store
        chunks = []
        for scene in scene_chunks:
            chunk_path = await self._get_chunk_path(video_id, scene.index)

            await self.chunking.extract_video_segment(
                Path(video.file_path), chunk_path,
                scene.start_time, scene.end_time
            )

            chunk = await self.chunk_repo.create(
                video_id=video_id,
                chunk_index=scene.index,
                start_time=scene.start_time,
                end_time=scene.end_time,
                duration=scene.duration,
                file_path=str(chunk_path),
                chunk_type="character_based",
                primary_speaker_id=speaker_id,
                speaker_ids=scene.speaker_ids,
                scene_context=scene.scene_context,
                transcript=[s.__dict__ for s in scene.transcript_segments]
            )
            chunks.append(chunk)

        return chunks
```

---

## YouTube Download

```python
import asyncio
from pathlib import Path

class YouTubeDownloadService:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    async def download_video(
        self,
        youtube_url: str,
        video_id: str
    ) -> Path:
        """Download YouTube video as WebM."""
        output_path = self.output_dir / f"{video_id}.webm"

        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best",
            "-o", str(output_path),
            youtube_url
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise VideoProcessingError(f"yt-dlp failed: {stderr.decode()}")

        return output_path

    async def get_video_info(self, youtube_url: str) -> dict:
        """Get video metadata without downloading."""
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--skip-download",
            youtube_url
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise VideoProcessingError(f"Failed to get info: {stderr.decode()}")

        import json
        return json.loads(stdout.decode())
```

---

## API Endpoints

```python
# GET /api/videos/{id}/speakers
# Returns list of detected speakers with statistics

# POST /api/videos/{id}/speakers/{speaker_id}/select
# User selects character for learning

# POST /api/videos/{id}/chunking-mode
# Body: {"mode": "character_based", "speaker_id": "uuid"}
# Switch between time-based and character-based modes

# GET /api/videos/{id}/chunks
# Query params: mode=character_based&speaker_id=uuid
# Returns chunks based on selected mode
```

---

## Storage Structure

```
/data/
├── users/
│   └── {user_id}/
│       ├── videos/              # Original uploads
│       ├── chunks/
│       │   ├── time_based/      # Default chunks
│       │   └── character_based/ # Character-specific chunks
│       │       └── {speaker_id}/
│       ├── transcripts/         # SRT, VTT, JSON
│       ├── audio/               # Extracted audio
│       ├── speakers/            # Speaker profiles
│       ├── courses/             # Course data
│       └── exams/               # Exam history
```

---

## Configuration

```python
# Chunking settings
CHUNKING_CONFIG = {
    "time_based": {
        "default_duration": 300,  # 5 minutes
        "min_duration": 60,       # 1 minute
        "max_duration": 600       # 10 minutes
    },
    "character_based": {
        "merge_gap_threshold": 2.0,     # 2 seconds
        "max_chunk_duration": 600.0,    # 10 minutes
        "min_chunk_duration": 0.0,      # No minimum
        "pause_threshold": 0.5,          # 0.5 seconds
        "context_window": 30.0          # 30 seconds context
    }
}
```

---

## Dependencies

```toml
[project.dependencies]
ffmpeg-python = ">=0.2.0"
yt-dlp = ">=2024.1.0"
pyannote.audio = ">=3.1.0"
faster-whisper = ">=0.10.0"
```

## Environment Variables

```bash
# HuggingFace token for pyannote.audio
HF_TOKEN=your_token_here

# Chunking configuration
DEFAULT_CHUNKING_MODE=time_based
DEFAULT_CHUNK_DURATION=300
CHARACTER_MAX_CHUNK_DURATION=600
```

## Error Handling

```python
class VideoProcessingError(Exception):
    """Base video processing error."""
    pass

class SpeakerNotFoundError(VideoProcessingError):
    """Selected speaker not found."""
    pass

class ChunkingModeError(VideoProcessingError):
    """Invalid chunking mode."""
    pass

class FFmpegError(VideoProcessingError):
    """FFmpeg processing failed."""
    pass
```

## Testing

```python
# tests/unit/test_character_chunking.py
@pytest.mark.asyncio
async def test_merge_consecutive_segments(chunking_service):
    segments = [
        SpeakerSegment("SPEAKER_00", 0.0, 5.0),
        SpeakerSegment("SPEAKER_00", 6.5, 10.0),  # 1.5s gap (merge)
        SpeakerSegment("SPEAKER_00", 15.0, 20.0), # 5s gap (no merge)
    ]

    merged = chunking_service._merge_consecutive_segments(segments)
    assert len(merged) == 2
    assert merged[0].end == 10.0

@pytest.mark.asyncio
async def test_split_long_scene(chunking_service):
    # 15 minute scene should split into 2 parts
    segment = SpeakerSegment("SPEAKER_00", 0.0, 900.0)

    split = chunking_service._split_long_scene(segment, [segment])
    assert len(split) == 2
    assert split[0].end - split[0].start <= 600.0
```

## See Also

- [Transcription Skill](../transcription-skill/SKILL.md) - Whisper integration
- [FastAPI Skill](../fastapi-skill/SKILL.md) - API patterns
- [Design Specs](../../../design-specs.md) - Full database schema
