# English Speaking Learning App - System Architecture

## Table of Contents

1. [System Overview](#system-overview)
2. [System Architecture](#system-architecture)
3. [Software Architecture](#software-architecture)
4. [Process Flow](#process-flow)
5. [Phase 1: Foundation](#phase-1-foundation)
6. [Phase 2: Video Pipeline](#phase-2-video-pipeline)
7. [Database Schema](#database-schema)
8. [API Reference](#api-reference)
9. [Directory Structure](#directory-structure)

---

## System Overview

**Project**: AI-Powered English Speaking Learning Platform
**Purpose**: Personalized English speaking learning through YouTube videos (movies, TV shows, TED talks)
**Approach**: Users provide YouTube URLs → System generates study plans, vocabulary lists, and speaking practice
**User Model**: Single-user application (no authentication)

### Key Principles

- **No background tasks**: All operations use async/await with immediate processing
- **Single LLM model**: Fixed Qwen3.5-2B-Q4_K_M.gguf model
- **Virtual chunking**: Chunks are timestamps into original video, not physical files
- **Checkpoint-resume**: Failed processing can be retried from last successful state

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Vue 3.5 + TypeScript)              │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────────────┐ │
│  │   Home    │  │  Course   │  │   Video   │  │     Speaking          │ │
│  │   Page    │  │   List    │  │  Player   │  │     Practice          │ │
│  └───────────┘  └───────────┘  └───────────┘  └───────────────────────┘ │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ REST API (Async)
┌────────────────────────────────────┴────────────────────────────────────┐
│                         BACKEND (FastAPI + Python 3.13+)                │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      SERVICE LAYER (Async I/O)                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │   │
│  │  │    Video    │  │ Transcription│  │     LLM     │  │ Study   │ │   │
│  │  │   Service   │  │   Service    │  │   Service   │  │ Service │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │   │
│  │         │               │                                      │   │
│  │         ▼               ▼                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐                              │   │
│  │  │  Download   │  │  Chunking   │                              │   │
│  │  │  Service    │  │  Service    │                              │   │
│  │  └─────────────┘  └─────────────┘                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    REPOSITORY LAYER (SQLAlchemy 2.0 Async)       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐   │   │
│  │  │  Video   │  │  Chunk   │  │Transcript│  │   StudyPlan    │   │   │
│  │  │  Repo    │  │  Repo    │  │  Repo    │  │     Repo       │   │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
          ┌──────────────────────────┴──────────────────────────┐
          ▼                                                     ▼
┌─────────────────────────────┐                 ┌─────────────────────────────┐
│          SQLite3            │                 │     llama-cpp-python        │
│       (learning.db)         │                 │   (Qwen3.5-2B-Q4_K_M)       │
│                             │                 │                             │
│   - Videos table            │                 │   - GPU auto-detection      │
│   - Chunks table            │                 │   - CUDA/CPU backend        │
│   - Transcripts table       │                 │   - Streaming support       │
│   - Study plans table       │                 │                             │
│   - Vocabulary table        │                 │                             │
└─────────────────────────────┘                 └─────────────────────────────┘
```

---

## Software Architecture

### Layer Responsibilities

| Layer | Component | Technology | Purpose |
|-------|-----------|------------|---------|
| **Frontend** | UI Components | Vue 3.5 + TypeScript | User interaction, video playback |
| **Frontend** | State Management | Pinia | Client-side state |
| **API** | REST Endpoints | FastAPI | HTTP interface |
| **Service** | Business Logic | Python 3.13+ | Processing pipeline |
| **Repository** | Data Access | SQLAlchemy 2.0 | Database operations |
| **LLM** | AI Processing | llama-cpp-python | Study plan generation, chat |
| **Storage** | File System | Local disk | Video, audio, transcript files |

### Design Patterns

#### 1. Repository Pattern
Abstracts database operations behind async interfaces.

```python
class VideoRepository:
    async def get_by_id(self, video_id: UUID) -> Optional[Video]
    async def get_all(self, skip: int, limit: int) -> List[Video]
    async def create(self, video: Video) -> Video
    async def save(self, video: Video) -> Video
    async def delete(self, video_id: UUID) -> bool
```

#### 2. Service Layer Pattern
Business logic separated into dedicated services.

```python
class VideoService:
    """Orchestrates video processing pipeline"""
    async def process_video(self, video_id: UUID) -> Video
    async def retry_video(self, video_id: UUID) -> Video

class DownloadService:
    async def download_video(self, youtube_url: str, video_id: str) -> Path

class ChunkingService:
    async def create_chunks(self, video_duration: float, transcript: List[dict]) -> List[VideoChunk]

class TranscriptionService:
    async def transcribe(self, video_path: Path) -> List[dict]
```

#### 3. State Machine Pattern
Checkpoint-resume via explicit state transitions.

```
pending → downloading → downloading_complete → chunking → chunking_complete
    → transcribing → transcribing_complete → studying → ready
    ↓
  failed
```

---

## Process Flow

### Video Processing Pipeline (Phase 2)

```
User submits YouTube URL
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ POST /api/v1/videos/youtube                                             │
│ Creates video record with status="pending"                              │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STATE: pending → downloading                                            │
│ SERVICE: VideoService.process_video()                                   │
│ OPERATION: DownloadService.download_video(url, video_id)                │
│ TOOL: yt-dlp (YouTube download)                                         │
│ OUTPUT: /data/videos/{video_id}.webm                                    │
│ STATUS: checkpoint saved after completion                               │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STATE: downloading → downloading_complete                               │
│ SERVICE: VideoService.process_video()                                   │
│ OPERATION: Get video metadata (title, duration)                         │
│ TOOL: yt-dlp (info extraction)                                          │
│ OUTPUT: Video.title, Video.duration                                     │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STATE: downloading_complete → chunking                                  │
│ SERVICE: ChunkingService.create_chunks()                                │
│ ALGORITHM: Hybrid Dynamic Sentence-Snap                                 │
│                                                                         │
│  For each ideal 5-min boundary at time T:                               │
│    1. Search transcript entries in range [T-30s, T+30s]                 │
│    2. Find sentence-ending punctuation (".!?") nearest to T             │
│    3. If found: snap chunk end to that boundary                         │
│    4. If not found: use ideal boundary T                                │
│                                                                         │
│ EXAMPLE:                                                                │
│   Ideal: 0:00-5:00, 5:00-10:00, 10:00-15:00                            │
│   Snapped: 0:00-5:12 ("...explain.". at 5:12), 5:12-10:05, ...         │
│                                                                         │
│ OUTPUT: List[VideoChunk] with start_time, end_time                      │
│ NOTE: Virtual chunks - no physical files created                        │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STATE: chunking → chunking_complete                                     │
│ REPOSITORY: ChunkRepository.create_many(chunks)                         │
│ OUTPUT: VideoChunk records in database                                  │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STATE: chunking_complete → transcribing                                 │
│ SERVICE: TranscriptionService.transcribe()                              │
│ STRATEGY: YouTube subtitles first, Whisper fallback                     │
│                                                                         │
│  Step 1: Try YouTube subtitles (if available)                          │
│    - yt-dlp --write-subs was run during download                       │
│    - Parse .srt/.vtt/.ass/.ssa files                                   │
│    - pysubs2 for parsing                                                │
│                                                                         │
│  Step 2: Fallback to Whisper (if no subtitles)                         │
│    - FFmpeg: Extract audio to WAV (16kHz, mono)                        │
│    - faster-whisper: Transcribe with word timestamps                   │
│    - VAD filter: Remove silence                                        │
│                                                                         │
│ OUTPUT: List[TranscriptSegment] with start, end, text                  │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STATE: transcribing → transcribing_complete                             │
│ REPOSITORY: TranscriptRepository.create(video_id, transcript)           │
│ OUTPUT: Transcript record in database + JSON file                       │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STATE: transcribing_complete → studying (Phase 3)                       │
│ SERVICE: LLM Service (not yet implemented in Phase 2)                   │
│ OPERATION: Generate study plan from transcript                          │
│ LLM: Qwen3.5-2B-Q4_K_M via llama-cpp-python                            │
│ OUTPUT: StudyPlan with objectives, vocabulary, grammar                  │
│ STATUS: Phase 2 stub returns empty plan, Phase 3 implements fully       │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STATE: studying → ready                                                 │
│ REPOSITORY: StudyPlanRepository.create(video_id, study_plan)            │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ API Response: Complete Video object                                     │
│   - video.id, video.title, video.status="ready"                         │
│   - video.chunks: List of sentence-snapped segments                     │
│   - video.transcript: Full transcript with timestamps                   │
│   - video.study_plan: Empty in Phase 2, populated in Phase 3            │
└─────────────────────────────────────────────────────────────────────────┘
```

### Error Handling & Retry

```
Processing fails at any step
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ VideoService catches exception                                          │
│ OPERATION: _update_status(video, "failed", error_message=str(e))        │
│ DATABASE: Video.error_message = error details                           │
│ REPOSITORY: VideoRepository.save(video)                                 │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ API returns 500 with error details                                      │
│   {"detail": "Video processing failed: <error>. Video status: failed"}  │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
User can call POST /api/v1/videos/{id}/retry
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ VideoService.retry_video(video_id)                                      │
│ LOGIC: Checks video.status                                              │
│   - If "failed": calls process_video() which resumes from checkpoint    │
│   - If "ready": returns immediately (already complete)                  │
│   - If other state: continues from current state                        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation

### Completed Components

| Component | Status | Description |
|-----------|--------|-------------|
| Database Models | ✅ | Video, Chunk, Transcript, StudyPlan, Vocabulary |
| Repository Layer | ✅ | Async SQLAlchemy 2.0 with all CRUD operations |
| API Structure | ✅ | FastAPI with versioning (/v1/) |
| Configuration | ✅ | Pydantic settings, DATA_DIR management |
| Docker Setup | ✅ | docker-compose with backend/frontend |
| Test Infrastructure | ✅ | pytest, conftest.py fixtures |

### Database Models

```python
class Video(Base):
    id: UUID
    title: str
    description: Optional[str]
    source_type: str = "youtube"
    youtube_url: str
    file_path: Optional[str]
    duration: float
    chunk_duration: float = 300
    status: str = "pending"
    error_message: Optional[str]  # For checkpoint-resume
    created_at: datetime
    updated_at: datetime

class VideoChunk(Base):
    id: UUID
    video_id: UUID (FK)
    chunk_index: int
    start_time: float  # seconds
    end_time: float    # seconds
    duration: float    # seconds
    status: str = "pending"
```

---

## Phase 2: Video Pipeline

### Implemented Services

| Service | File | Lines | Description |
|---------|------|-------|-------------|
| `DownloadService` | `download_service.py` | 97 | YouTube download via yt-dlp |
| `ChunkingService` | `chunking_service.py` | 168 | Hybrid Dynamic sentence-snap |
| `TranscriptionService` | `transcription_service.py` | 244 | YouTube subs + Whisper fallback |
| `VideoService` | `video_service.py` | 212 | Orchestrator with state machine |
| `exceptions` | `exceptions.py` | 39 | Custom exceptions with checkpoint info |

### Key Implementation Details

#### 1. Download Service
```python
# Uses yt-dlp for YouTube download
# Format preference: WebM > MP4 (best quality)
# Output: /data/videos/{video_id}.webm

ydl_opts = {
    "format": "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best",
    "outtmpl": output_path.replace(".webm", ""),
    "quiet": True,
    "no_warnings": True,
}
```

#### 2. Chunking Service (Hybrid Dynamic)
```python
# For each 5-min ideal boundary:
#   1. Search ±30 seconds for sentence-ending punctuation
#   2. Snap to nearest sentence boundary if found
#   3. Fall back to ideal boundary if no sentence found

SEARCH_WINDOW = 30.0  # seconds
SENTENCE_PUNCTUATION = {".", "!", "?"}

def _find_sentence_boundary(self, target_time, transcript, chunk_start, video_duration):
    # Find all sentence endings in [target_time - 30s, target_time + 30s]
    # Return the one nearest to target_time
```

#### 3. Transcription Service
```python
# Strategy: YouTube subtitles first, Whisper fallback

async def transcribe(self, video_path):
    # Step 1: Try YouTube subtitles
    transcript = await self._try_youtube_subtitles(video_path)
    if transcript:
        return transcript

    # Step 2: Whisper fallback
    return await self._transcribe_with_whisper(video_path)
```

#### 4. Video Service (Orchestrator)
```python
# State machine implementation
async def process_video(self, video_id):
    video = await self.video_repo.get_by_id(video_id)

    if video.status == "pending":
        await self._update_status(video, "downloading")
        video.file_path = await self.download_service.download_video(...)
        await self._update_status(video, "downloading_complete")

    if video.status == "downloading_complete":
        await self._update_status(video, "chunking")
        chunks = await self._create_chunks_with_snap(video)
        await self._update_status(video, "chunking_complete")

    # ... continues for transcribing, studying
```

### State Machine

```
┌───────────┐     ┌─────────────┐     ┌──────────────────────┐
│  pending  │────▶│ downloading │────▶│ downloading_complete │
└───────────┘     └─────────────┘     └──────────────────────┘
                                               │
                                               ▼
┌───────────┐     ┌─────────┐     ┌──────────────────────┐
│  failed   │◀────│ studying │◀────│    transcribing      │
└───────────┘     └─────────┘     └──────────────────────┘
     │                                    ▲
     │              ┌─────────────┐       │
     └──────────────│  retry      │───────┘
                    └─────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│                     ready                             │
│  (All processing complete, video available to user)  │
└──────────────────────────────────────────────────────┘
```

### Custom Exceptions

```python
class VideoProcessingError(Exception):
    """Base exception with checkpoint info"""
    def __init__(self, message, checkpoint_state, failed_step):
        self.checkpoint_state = checkpoint_state  # e.g., "downloading"
        self.failed_step = failed_step            # e.g., "download"

class DownloadError(VideoProcessingError):
    def __init__(self, message):
        super().__init__(message, checkpoint_state="downloading", failed_step="download")

class ChunkingError(VideoProcessingError):
    def __init__(self, message):
        super().__init__(message, checkpoint_state="chunking", failed_step="chunking")

class TranscriptionError(VideoProcessingError):
    def __init__(self, message):
        super().__init__(message, checkpoint_state="transcribing", failed_step="transcription")

class StudyPlanError(VideoProcessingError):
    def __init__(self, message):
        super().__init__(message, checkpoint_state="studying", failed_step="study_plan")
```

### Test Coverage

| Test Suite | Tests | Status |
|------------|-------|--------|
| `test_exceptions.py` | 6 | ✅ Pass |
| `test_download_service.py` | 4 | ✅ Pass |
| `test_chunking_service.py` | 7 | ✅ Pass |
| `test_transcription_service.py` | 5 | ✅ Pass |
| `test_video_service.py` | 9 | ✅ Pass |
| **Total** | **31** | **100%** |

---

## Database Schema

### Videos Table

```sql
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    source_type VARCHAR(50) NOT NULL DEFAULT 'youtube',
    youtube_url VARCHAR(1000) NOT NULL,
    file_path VARCHAR(1000),           -- Downloaded file path
    duration FLOAT NOT NULL,           -- Video duration in seconds
    chunk_duration FLOAT DEFAULT 300,  -- Target chunk duration (5 min default)
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,                -- For checkpoint-resume error tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_youtube_url ON videos(youtube_url);
```

### Video Chunks Table

```sql
CREATE TABLE video_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,      -- Sequential: 0, 1, 2...
    start_time FLOAT NOT NULL,         -- In seconds
    end_time FLOAT NOT NULL,           -- In seconds
    duration FLOAT NOT NULL,           -- Calculated: end_time - start_time
    transcript JSONB,                  -- Transcript for this chunk
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(video_id, chunk_index)
);

CREATE INDEX idx_chunks_video_id ON video_chunks(video_id);
```

### Transcripts Table

```sql
CREATE TABLE transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    language VARCHAR(10) DEFAULT 'en',
    segments JSONB NOT NULL,           -- [{start, end, text, speaker}]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_transcripts_video_id ON transcripts(video_id);
```

### Study Plans Table

```sql
CREATE TABLE study_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    objectives JSONB DEFAULT '[]',     -- ["Understand main topic", ...]
    vocabulary JSONB DEFAULT '[]',     -- [{word, definition, context}, ...]
    grammar JSONB DEFAULT '[]',        -- [{rule, examples}, ...]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Relationships

```
videos (1) ──────< video_chunks (many)
videos (1) ──────< transcripts (1)
videos (1) ──────< study_plans (1)
```

---

## API Reference

### Endpoints (Phase 2)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| `GET` | `/api/v1/videos` | List all videos | ✅ |
| `GET` | `/api/v1/videos/{id}` | Get video by ID | ✅ |
| `POST` | `/api/v1/videos/youtube` | Create video from YouTube (full pipeline) | ✅ |
| `POST` | `/api/v1/videos/{id}/retry` | Retry from checkpoint | ✅ |
| `PATCH` | `/api/v1/videos/{id}` | Update video | ✅ |
| `DELETE` | `/api/v1/videos/{id}` | Delete video | ✅ |
| `GET` | `/api/v1/videos/{id}/chunks` | Get video chunks | ✅ |

### POST /api/v1/videos/youtube

**Description**: Create video from YouTube URL and process through full pipeline.

**Request**:
```json
{
    "youtube_url": "https://www.youtube.com/watch?v=...",
    "chunk_duration": 300
}
```

**Response** (201 Created):
```json
{
    "id": "uuid",
    "title": "Video Title",
    "youtube_url": "https://www.youtube.com/watch?v=...",
    "source_type": "youtube",
    "file_path": "/data/videos/uuid.webm",
    "duration": 1234.5,
    "chunk_duration": 300,
    "status": "ready",
    "error_message": null,
    "created_at": "2026-04-26T10:00:00Z",
    "updated_at": "2026-04-26T10:05:00Z",
    "chunks": [
        {
            "id": "uuid",
            "video_id": "uuid",
            "chunk_index": 0,
            "start_time": 0.0,
            "end_time": 312.5,
            "duration": 312.5,
            "status": "pending"
        }
    ]
}
```

**Processing Time**:
- Short videos (<5 min): ~30-60 seconds
- Medium videos (5-15 min): ~2-5 minutes
- Long videos (>15 min): ~10+ minutes

### POST /api/v1/videos/{id}/retry

**Description**: Retry processing from last checkpoint after failure.

**Response** (200 OK):
```json
{
    "id": "uuid",
    "status": "ready",
    "error_message": null,
    ...
}
```

**Error Response** (500):
```json
{
    "detail": "Video processing failed: <error>. Video status: chunking"
}
```

---

## Directory Structure

```
/workspaces/education/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI entry point
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                # Dependencies (db session)
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py          # API router
│   │   │       └── endpoints/
│   │   │           ├── __init__.py
│   │   │           ├── videos.py      # Video endpoints
│   │   │           ├── courses.py     # (future)
│   │   │           ├── learning.py    # (future)
│   │   │           └── speaking.py    # (future)
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # Pydantic settings, DATA_DIR
│   │   │   └── logger.py              # Logging configuration
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Base class for models
│   │   │   ├── session.py             # Database session
│   │   │   └── init_db.py             # Database initialization
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── video.py               # Video, VideoChunk models
│   │   │   ├── transcript.py          # Transcript model
│   │   │   ├── study_plan.py          # StudyPlan model
│   │   │   └── vocabulary.py          # Vocabulary model
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── video.py               # Pydantic schemas
│   │   │
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── video.py               # VideoRepository
│   │   │   ├── chunk.py               # ChunkRepository
│   │   │   ├── transcript.py          # TranscriptRepository
│   │   │   └── study_plan.py          # StudyPlanRepository
│   │   │
│   │   └── services/                  # PHASE 2 IMPLEMENTATION
│   │       ├── __init__.py            # Exports all services
│   │       ├── exceptions.py          # Custom exceptions (39 lines)
│   │       ├── download_service.py    # YouTube download (97 lines)
│   │       ├── chunking_service.py    # Hybrid Dynamic (168 lines)
│   │       ├── transcription_service.py # YouTube+Whisper (244 lines)
│   │       └── video_service.py       # Orchestrator (212 lines)
│   │
│   ├── alembic/
│   │   ├── versions/
│   │   │   ├── 001_initial.py         # Initial migration
│   │   │   └── 002_add_error_message.py # Phase 2 migration
│   │   └── env.py
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py                # Pytest fixtures
│       └── unit/
│           ├── test_exceptions.py     # 6 tests
│           ├── test_download_service.py # 4 tests
│           ├── test_chunking_service.py # 7 tests
│           ├── test_transcription_service.py # 5 tests
│           └── test_video_service.py  # 9 tests
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── views/
│       ├── composables/
│       ├── services/
│       ├── stores/
│       └── router/
│
├── data/                              # Runtime data (mounted in Docker)
│   ├── db/
│   │   └── learning.db               # SQLite database
│   ├── videos/                       # Downloaded YouTube videos
│   ├── transcripts/                  # JSON transcript files
│   └── audios/                       # Extracted audio files
│
├── design-specs.md                    # Design specifications
├── requirements.md                    # Dependencies and requirements
├── ARCHITECTURE.md                    # This document
└── docker-compose.yml                 # Docker Compose configuration
```

---

## Storage Structure

```
PROJECT_ROOT/data/          (or /app/data/ in Docker)
├── db/
│   └── learning.db         # SQLite database
├── models/
│   └── Qwen3.5-2B-Q4_K_M.gguf  # LLM model file
├── videos/
│   └── {video_id}.webm     # Downloaded YouTube videos
├── transcripts/
│   └── {video_id}.json     # JSON transcript files
└── audios/
    └── {video_id}_audio.wav  # Extracted audio (temp)
```

**Important Notes**:
- Video chunks are **virtual** (timestamps only, no physical files)
- Audio files are **temporary** (deleted after Whisper transcription)
- Original video files are **preserved** for playback with seeking

---

## Phase 3 Preview (Not Yet Implemented)

| Feature | Status | Description |
|---------|--------|-------------|
| LLM Service | 🔲 | llama-cpp-python integration |
| Study Plan Generation | 🔲 | LLM analyzes transcript, generates objectives/vocab/grammar |
| Chat Interface | 🔲 | AI tutor for questions about video content |
| Streaming | 🔲 | Real-time token generation for UI |

---

## Document History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-04-26 | 1.0 | AI Assistant | Initial architecture document from Phase 2 implementation |

---

**End of Architecture Document**