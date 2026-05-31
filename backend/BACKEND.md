# English Learning App - Backend Summary

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Directory Structure](#directory-structure)
4. [Database Schema](#database-schema)
5. [API Reference](#api-reference)
6. [Services Layer](#services-layer)
7. [Processing Pipeline](#processing-pipeline)
8. [Configuration](#configuration)
9. [Storage Structure](#storage-structure)
10. [GPU Configuration](#gpu-configuration)
11. [Dependencies](#dependencies)

---

## System Overview

**English Learning App** is an AI-powered English learning platform using LLM as a personalized teacher. Users provide YouTube URLs and the system generates personalized study plans and vocabulary lists.

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.13+ + uv |
| Database | SQLite3 (learning.db) |
| LLM | llama-cpp-python (Qwen3.5-2B-Q4_K_M) |
| Video | FFmpeg + yt-dlp |
| Transcription | faster-whisper |

**Key Design Decisions:**
- Single-user application (no authentication)
- YouTube only (no local uploads)
- Single fixed LLM model (no switching)
- All operations use async/await (no background queues)
- **Traditional Chinese (繁體中文)** for all Chinese text

---

## Architecture

```
Frontend (Vue 3.5 + TypeScript)
         ↓ REST API
Backend (FastAPI) - Async I/O operations
         ↓
Services: Video | Transcription | LLM | Download | Chunking
         ↓
SQLite3 | llama-cpp-python (in-backend)
```

### Backend Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Configuration (Pydantic settings)
│   ├── logging.py                 # Logging setup
│   │
│   ├── api/v1/
│   │   ├── router.py             # API router
│   │   └── endpoints/
│   │       ├── videos.py         # Video endpoints
│   │       ├── courses.py        # Course endpoints
│   │       └── ...
│   │
│   ├── core/                     # Core functionality
│   │   ├── config.py             # Settings, DATA_DIR, paths
│   │   └── logging.py            # Structured logging
│   │
│   ├── db/                        # Database layer
│   │   ├── base.py               # Base model class
│   │   ├── session.py            # Async session
│   │   └── init_db.py            # DB initialization
│   │
│   ├── models/                    # SQLAlchemy models
│   │   ├── video.py              # Video model
│   │   ├── chunk.py              # VideoChunk model
│   │   ├── transcript.py         # Transcript model
│   │   ├── study_plan.py         # StudyPlan model
│   │   └── vocabulary.py         # Vocabulary model
│   │
│   ├── schemas/                   # Pydantic schemas
│   │   ├── video.py
│   │   ├── transcript.py
│   │   └── ...
│   │
│   ├── repositories/              # Data access layer
│   │   ├── video.py
│   │   ├── chunk.py
│   │   └── ...
│   │
│   ├── services/                  # Business logic
│   │   ├── video_service.py      # Orchestrator with state machine
│   │   ├── download_service.py   # YouTube download (yt-dlp)
│   │   ├── chunking_service.py   # Hybrid Dynamic sentence-snap
│   │   ├── transcription_service.py # YouTube subs + Whisper
│   │   ├── llm_service.py       # llama-cpp-python integration
│   │   └── exceptions.py         # Custom exceptions
│   │
│   └── utils/
│       └── gpu_utils.py          # GPU detection & configuration
│
├── alembic/                       # Database migrations
├── tests/                         # Test suite
└── pyproject.toml                 # Project config (uv)
```

---

## Database Schema

### Videos Table
```sql
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    source_type VARCHAR(50) DEFAULT 'youtube',
    youtube_url VARCHAR(1000) NOT NULL,
    file_path VARCHAR(1000),           -- Downloaded file path
    duration FLOAT NOT NULL,           -- Video duration in seconds
    chunk_duration FLOAT DEFAULT 300,  -- Target chunk duration (5 min)
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,                -- Checkpoint-resume error tracking
    thumbnail VARCHAR(500),
    uploader VARCHAR(500),
    upload_date VARCHAR(20),           -- YYYYMMDD format
    view_count INTEGER,
    like_count INTEGER,
    metadata_json JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Video Chunks Table
```sql
CREATE TABLE video_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,      -- Sequential: 0, 1, 2...
    start_time FLOAT NOT NULL,         -- Seconds
    end_time FLOAT NOT NULL,           -- Seconds
    duration FLOAT NOT NULL,
    transcript JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(video_id, chunk_index)
);
```

### Transcripts Table
```sql
CREATE TABLE transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    source VARCHAR(50) NOT NULL,        -- user, youtube_author, whisper, youtube_auto
    language VARCHAR(10) DEFAULT 'en',
    segments JSONB NOT NULL,            -- [{start, end, text}]
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Study Plans Table
```sql
CREATE TABLE study_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    data JSONB NOT NULL,                -- LLM-generated study plan
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Reference

### Video Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/videos` | List all videos |
| `GET` | `/api/v1/videos/{id}` | Get video by ID |
| `POST` | `/api/v1/videos/youtube` | Create video from YouTube URL |
| `POST` | `/api/v1/videos/info` | Get video metadata without DB operations |
| `PATCH` | `/api/v1/videos/{id}` | Update video |
| `DELETE` | `/api/v1/videos/{id}` | Delete video |
| `POST` | `/api/v1/videos/{id}/retry` | Retry processing from checkpoint |
| `GET` | `/api/v1/videos/{id}/chunks` | Get video chunks |
| `GET` | `/api/v1/videos/{id}/chunks/{index}/audio` | Get chunk audio (MP3) |
| `GET` | `/api/v1/videos/{id}/transcripts/{type}` | Get transcript by type |
| `POST` | `/api/v1/videos/{id}/transcripts/user` | Upload user transcript |

### Transcript Types (Priority Order)
1. **user** - User-uploaded subtitles (highest)
2. **youtube_author** - YouTube creator-uploaded subtitles
3. **whisper** - Whisper transcription (always generated)
4. **youtube_auto** - YouTube auto-generated captions (lowest)

### Course Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/courses` | List courses |
| `POST` | `/api/v1/courses` | Create course |
| `GET` | `/api/v1/courses/{id}` | Get course |
| `PATCH` | `/api/v1/courses/{id}` | Update course |
| `DELETE` | `/api/v1/courses/{id}` | Delete course |
| `POST` | `/api/v1/courses/{id}/videos` | Add video to course |
| `PUT` | `/api/v1/courses/{id}/videos/reorder` | Reorder videos |
| `POST` | `/api/v1/courses/{id}/start` | Start learning course |

---

## Services Layer

### VideoService (Orchestrator)
Located: `app/services/video_service.py`

Implements state machine with checkpoint-resume:

```
pending → downloading → downloading_complete →
transcribing → transcribing_complete →
chunking → chunking_complete →
audio_extracted → studying → ready
                                    ↓
                                  failed
```

Key methods:
- `process_video(video_id)` - Full pipeline
- `retry_video(video_id)` - Resume from checkpoint
- `get_transcript_by_priority(video_id)` - Get highest priority transcript

### DownloadService
Located: `app/services/download_service.py`

- Uses **yt-dlp** for YouTube downloads
- Downloads video as WebM format
- Downloads author and auto-generated subtitles (json3, vtt, srt, ass, lrc)
- Falls back to Whisper if subtitle download fails

### ChunkingService
Located: `app/services/chunking_service.py`

**Hybrid Dynamic Sentence-Snap Algorithm:**
1. Calculate ideal 5-min positions: (0:00-5:00), (5:00-10:00), etc.
2. For each ideal boundary, search ±30s for sentence-ending punctuation (`.! ?`)
3. Snap to nearest sentence boundary if found, otherwise use ideal position

### TranscriptionService
Located: `app/services/transcription_service.py`

**Triple Transcript System:**
1. **YouTube subtitles** - From downloaded subtitle files
2. **YouTube auto captions** - ASR-generated captions
3. **Whisper** - Always runs, regardless of YouTube subtitle availability

Uses:
- `pysubs2` for parsing SRT/VTT/ASS/SSA
- `faster-whisper` (base model) for transcription
- FFmpeg for audio extraction (16kHz, mono, WAV)

### LLMService
Located: `app/services/llm_service.py`

- Uses **llama-cpp-python** with **Qwen3.5-2B-Q4_K_M**
- Lazy-loaded model initialization
- Generates structured JSON study plans
- All Chinese text must be Traditional Chinese (繁體中文)
- **Context Size**: 8192 tokens (LLM_CONTEXT_SIZE)
- **Transcript Truncation**: 4000 characters (first portion only)

**Video Length Limitation:**
- With 4000 character transcript limit and ~1000 chars/minute transcript density
- **Estimated limit: ~3-5 minutes** of video content per study plan
- Longer videos: Only the first ~3-5 minutes are used for study plan generation
- For full video coverage, consider future chunked study plan approach

---

## Processing Pipeline

```
POST /api/v1/videos/youtube
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 1. Download (yt-dlp)                                       │
│    - Downloads video + subtitles                           │
│    - Stores in data/videos/{id}.webm                      │
│    - Status: pending → downloading → downloading_complete  │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Transcribe (Whisper - always runs)                      │
│    - Extracts audio (FFmpeg → WAV 16kHz mono)              │
│    - Transcribes with faster-whisper                       │
│    - Stores all available transcripts                      │
│    - Status: downloading_complete → transcribing →         │
│      transcribing_complete                                 │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Chunk (Hybrid Dynamic + Sentence Snap)                  │
│    - Uses transcript for sentence-aware boundaries        │
│    - Creates virtual chunks (timestamps only)              │
│    - Status: transcribing_complete → chunking →            │
│      chunking_complete                                     │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Extract Audio                                            │
│    - Extracts MP3 for each chunk                           │
│    - Stores in data/audios/{video_id}/chunk_{i}.mp3        │
│    - Status: chunking_complete → audio_extracted           │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Generate Study Plan (LLM)                               │
│    - Uses highest priority transcript                      │
│    - LLM generates vocabulary, grammar, notes              │
│    - Status: audio_extracted → studying → ready           │
└─────────────────────────────────────────────────────────────┘
         ↓
   Returns complete VideoResponse
```

### Checkpoint-Resume
On failure:
- Video stays in last successful state
- `error_message` field set with failure details
- User can retry via `POST /api/v1/videos/{id}/retry`

---

## Configuration

### Fixed System Constants (Not Configurable)
```python
PROJECT_ROOT = /app  # Docker) or calculated (local)
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR}/db/learning.db"
LLM_MODEL_PATH = DATA_DIR / "models"
SENTENCE_SNAP = True  # Always enabled
```

### Configurable Environment Variables
```bash
# LLM (llama-cpp-python)
DEFAULT_MODEL=Qwen3.5-2B-Q4_K_M.gguf
LLM_GPU_LAYERS=-1          # -1=auto, 0=CPU only, N=specific layers
LLM_CONTEXT_SIZE=8192
LLM_THREADS=4

# YouTube Download
YOUTUBE_DOWNLOAD_QUALITY=720
YOUTUBE_AUDIO_QUALITY=128k

# Chunking
CHUNK_DURATION=300         # Target duration in seconds (~5 min)
```

---

## Storage Structure

```
PROJECT_ROOT/data/
├── db/
│   └── learning.db         # SQLite database
├── models/
│   └── Qwen3.5-2B-Q4_K_M.gguf  # LLM model file
├── videos/
│   └── {video_id}.webm    # Downloaded YouTube videos
├── subtitles/
│   └── {video_id}.{lang}.{ext}  # Downloaded subtitle files
├── transcripts/
│   ├── youtube/
│   │   └── {video_id}.json
│   └── whisper/
│       └── {video_id}.json
└── audios/
    └── {video_id}/
        ├── chunk_0.mp3
        ├── chunk_1.mp3
        └── ...
```

**Important Notes:**
- Video chunks are **virtual** (timestamps only, no physical files)
- Audio files are **extracted per chunk** for audio-only listening
- Original video files are **preserved** for playback

---

## GPU Configuration

Located: `app/utils/gpu_utils.py`

### GPU Auto-Detection
- Automatically detects NVIDIA GPUs using GPUtil
- Calculates optimal GPU layers based on available VRAM
- Safety buffer of 1GB leaves room for other operations

### VRAM Estimates (Q4_K_M Quantization)
| Model Size | Memory/Layer | Total Layers |
|------------|-------------|-------------|
| 0.5B | 35MB | 24 |
| 1.5B | 45MB | 28 |
| 2B | 50MB | 28 |
| 3B | 80MB | 28 |
| 4B | 90MB | 34 |

### Configuration Options
```python
# LLM_GPU_LAYERS=-1: Auto-detect based on available VRAM
# LLM_GPU_LAYERS=0: CPU-only mode
# LLM_GPU_LAYERS=N: Offload N specific layers
```

### GPU Detection Flow
```
1. Detect all NVIDIA GPUs
2. Sort by free VRAM (highest first)
3. Calculate optimal layers = min(available_vram / layer_memory, total_layers)
4. Return config with n_gpu_layers and backend (cuda/cpu)
```

---

## Dependencies

```toml
# Core
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Database
sqlalchemy[asyncio]>=2.0.0
aiosqlite>=0.19.0
alembic>=1.12.0

# Video Processing
ffmpeg-python>=0.2.0
yt-dlp>=2024.1.0

# Transcription
pysubs2>=1.6.0
faster-whisper>=0.10.0

# LLM
llama-cpp-python>=0.2.0

# GPU
gputil>=1.4.0

# Async
httpx>=0.24.0
```

---

## Language Requirements

**MANDATORY: All Chinese text must use Traditional Chinese (繁體中文).**

This applies to:
- LLM-generated content (vocabulary definitions, grammar explanations, notes)
- API responses containing Chinese text
- Any Chinese feedback or explanations

LLM prompts must include:
```
IMPORTANT: When generating any Chinese text (definitions, explanations, notes, feedback),
you MUST use Traditional Chinese (繁體中文). Do NOT use Simplified Chinese.
Examples of Traditional Chinese: 是、開發、學習、詞彙、語法
Examples to AVOID (Simplified): 是、开发、学习、词汇、语法
```

---

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/unit/test_video_service.py
```

---

**End of Backend Summary**