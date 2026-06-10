# Backend Documentation

## System Overview

AI-powered English learning platform. Users provide YouTube URLs and the system generates study plans with vocabulary and grammar.

| Component | Technology |
|-----------|------------|
| Framework | FastAPI + Python 3.12 + uv |
| Database | SQLite3 (learning.db) |
| LLM | llama-cpp-python (Qwen3.5-2B-Q4_K_M) |
| Video | FFmpeg + yt-dlp |
| Transcription | faster-whisper |

**Design:**
- Single-user (no authentication)
- YouTube only (no local uploads)
- Fixed LLM model (no switching)
- All async/await (no background queues)
- Traditional Chinese (繁體中文) for all Chinese text

---

## Directory Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI entry, CORS, lifespan
│   ├── api/v1/
│   │   ├── router.py              # Route aggregation
│   │   └── endpoints/
│   │       ├── videos.py          # Video CRUD + YouTube processing
│   │       ├── chat.py            # AI tutor streaming (SSE)
│   │       ├── speaking.py        # Speaking practice
│   │       ├── stats.py           # Dashboard statistics
│   │       ├── llm.py             # GPU/LLM health status
│   │       ├── vocabulary.py      # Vocabulary + SM-2 spaced repetition
│   │       └── migrate.py         # Vocabulary migration tool
│   ├── core/
│   │   ├── config.py              # Settings, paths (DATA_DIR, DATABASE_URL)
│   │   └── logging.py            # Structured logging
│   ├── db/
│   │   ├── base.py                # SQLAlchemy Base + TimestampMixin
│   │   └── session.py             # AsyncSession with SQLite pragmas
│   ├── models/                   # SQLAlchemy models
│   ├── schemas/                   # Pydantic v2 schemas
│   ├── repositories/             # Data access layer (async)
│   ├── services/                  # Business logic (async)
│   └── utils/
│       └── gpu_utils.py          # NVIDIA GPU detection
├── alembic/                      # Database migrations
└── pyproject.toml                # uv project config
```

---

## API Endpoints

### Videos (`/api/v1/videos`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | List all videos |
| `GET` | `/{id}` | Get video by ID |
| `POST` | `/youtube` | Create video from YouTube URL |
| `POST` | `/info` | Get video metadata (no DB) |
| `PATCH` | `/{id}` | Update video |
| `DELETE` | `/{id}` | Delete video |
| `POST` | `/{id}/retry` | Retry from checkpoint |
| `GET` | `/{id}/chunks` | Get video chunks |
| `GET` | `/{id}/chunks/{idx}/audio` | Get chunk audio (MP3) |
| `GET` | `/{id}/stream` | Stream video file |
| `GET` | `/{id}/transcripts/{type}` | Get transcript (user/youtube_author/whisper/youtube_auto) |
| `POST` | `/{id}/transcripts/user` | Upload user transcript |
| `GET` | `/{id}/study-plans` | Get study plans |
| `GET/PATCH` | `/{id}/study-plans/{idx}` | Get/update study plan |
| `GET/PATCH` | `/{id}/progress` | Get/update study progress |

### Other Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat` | Streaming AI tutor (SSE) |
| `GET` | `/api/v1/stats/dashboard` | Dashboard statistics |
| `GET` | `/api/v1/llm/gpu-status` | GPU detection status |
| `GET` | `/api/v1/llm/llm-health` | LLM health check |
| `GET` | `/api/v1/vocabulary/reviewed` | Reviewed vocabulary words |
| `GET` | `/api/v1/vocabulary/favorites` | Favorite words |
| `POST` | `/api/v1/vocabulary/favorites/{word}/toggle` | Toggle favorite |
| `GET` | `/api/v1/vocabulary/{word}` | Get vocabulary item |
| `POST` | `/api/v1/vocabulary/{word}/review` | Review with SM-2 |
| `GET` | `/api/v1/speaking/videos/{id}/segments` | Get speaking segments |
| `GET` | `/api/v1/speaking/videos/{id}/audio-segment` | Extract audio segment |
| `POST` | `/api/v1/speaking/videos/{id}/compare` | Compare recording |

---

## Database Models

### Video
```sql
videos (id, title, description, source_type, youtube_url, file_path,
        duration, chunk_duration, status, error_message, thumbnail,
        uploader, upload_date, view_count, like_count, metadata_json)
```

### VideoChunk
```sql
video_chunks (id, video_id, chunk_index, start_time, end_time,
              duration, transcript, status)
```

### Transcript
```sql
transcripts (id, video_id, source, segments, full_text, language)
```
Sources: `user`, `youtube_author`, `whisper`, `youtube_auto`

### StudyPlan
```sql
study_plans (id, video_id, chunk_index, objectives, vocabulary,
             grammar, notes, notes_zh, overall_difficulty, estimated_time)
```

### Vocabulary (SM-2)
```sql
vocabularies (id, word, definition, context, cefr_level, pronunciation,
              review_count, next_review, interval, ease_factor,
              repetition_number, is_favorite)
```

### StudyProgress
```sql
study_progress (id, video_id, chunk_index, current_timestamp,
                sentence_index, completed, next_review)
```

### SpeakingPracticeRecord
```sql
speaking_practice_records (id, video_id, segment_start, segment_end,
                           character_text, user_recording_path,
                           similarity_score, feedback, attempts)
```

---

## Processing Pipeline

```
POST /api/v1/videos/youtube
         ↓
┌────────────────────────────────────────┐
│ 1. Download (yt-dlp)                    │
│    pending → downloading →             │
│    downloading_complete                │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ 2. Transcribe (always runs Whisper)    │
│    downloading_complete → transcribing │
│    → transcribing_complete             │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ 3. Chunk (Hybrid Dynamic sentence-snap)│
│    transcribing_complete → chunking →  │
│    chunking_complete                   │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ 4. Extract Audio (per chunk MP3)       │
│    chunking_complete → extracting_audio│
│    → audio_extracted                   │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ 5. Generate Study Plan (LLM)            │
│    audio_extracted → studying → ready  │
└────────────────────────────────────────┘
         ↓
   Returns VideoResponse
```

**On failure:** Video stays at last successful state with `error_message`. Retry via `POST /{id}/retry`.

---

## Transcript Priority

1. `user` - User-uploaded (highest)
2. `youtube_author` - Creator-uploaded
3. `whisper` - Whisper transcription (always generated)
4. `youtube_auto` - YouTube auto-generated (lowest)

---

## Services

| Service | Purpose |
|---------|---------|
| VideoService | Orchestrator with state machine |
| DownloadService | yt-dlp YouTube download |
| ChunkingService | Hybrid Dynamic sentence-snap (±30s) |
| TranscriptionService | YouTube subs + Whisper (dual) |
| LLMService | llama-cpp-python Qwen3.5-2B |
| ChatService | AI tutor streaming chat |
| SpeakingService | Audio comparison |
| StatsService | Dashboard calculations |

---

## Configuration

### Fixed (not configurable)
```python
PROJECT_ROOT = /app (Docker) or detected
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_URL = sqlite+aiosqlite:///data/db/learning.db
LLM_MODEL_PATH = data/models
```

### Environment Variables
```bash
DEFAULT_MODEL=Qwen3.5-2B-Q4_K_M.gguf
LLM_GPU_LAYERS=-1        # -1=auto, 0=CPU, N=layers
LLM_CONTEXT_SIZE=8192
LLM_THREADS=4
YOUTUBE_DOWNLOAD_QUALITY=720
YOUTUBE_AUDIO_QUALITY=128k
CHUNK_DURATION=180       # 3 minutes
```

---

## Storage Structure

```
data/
├── db/learning.db         # SQLite database
├── models/                # LLM model files
├── videos/                # Downloaded YouTube videos
├── subtitles/             # Downloaded subtitle files
├── transcripts/
│   ├── youtube/           # YouTube transcripts (JSON)
│   └── whisper/           # Whisper transcripts (JSON)
└── audios/{video_id}/    # Per-chunk MP3 files
```

---

## GPU Configuration

Located: `app/utils/gpu_utils.py`

- Auto-detects NVIDIA GPUs via GPUtil
- VRAM-based layer calculation (~80MB/layer for 2B Q4_K_M)
- Safety buffer of 1GB

```python
LLM_GPU_LAYERS=-1  # Auto-detect
LLM_GPU_LAYERS=0   # CPU only
LLM_GPU_LAYERS=N   # N specific layers
```

---

## Dependencies

```toml
fastapi>=0.100.0, uvicorn[standard]>=0.23.0
pydantic>=2.0.0, pydantic-settings>=2.0.0
sqlalchemy[asyncio]>=2.0.0, aiosqlite>=0.19.0
yt-dlp>=2024.1.0, ffmpeg-python>=0.2.0
pysubs2>=1.6.0, faster-whisper>=0.10.0
llama-cpp-python>=0.2.0, gputil>=1.4.0
```

---

## Testing

```bash
uv run pytest
uv run pytest --cov=app
```