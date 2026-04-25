# English Learning App - Agent Instructions

## Project Overview

An AI-powered English education platform using LLM as a personalized teacher. Users provide YouTube URLs (movies, TV shows, TED talks) and the system generates personalized study plans and vocabulary lists. **Single-user application** - no authentication required.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.13+ + uv |
| Frontend | Vue 3.5 + TypeScript + Vite |
| Database | SQLite3 (learning.db) |
| LLM | llama-cpp-python (Qwen3.5-2B-Q4_K_M) |
| Video | FFmpeg + yt-dlp |
| Transcription | faster-whisper |

## Architecture

```
Frontend (Vue 3.5 + TypeScript)
  ↓ REST API
Backend (FastAPI) - Async I/O operations
  ↓
Services: Video | LLM | Study | Speaking
  ↓
SQLite3 | llama-cpp-python (in-backend)
```

**No external queue services** - All operations use async/await with immediate processing. API calls wait for completion and return results directly.

## Directory Structure

```
/course/Python/education/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Config, logging
│   │   ├── db/             # Database models
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic (async)
│   │   └── main.py         # FastAPI entry
│   ├── alembic/            # Database migrations
│   └── tests/
├── frontend/               # Vue 3.5 application
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── views/          # Page components (Vue views)
│   │   ├── composables/    # Vue composables
│   │   ├── services/       # API services
│   │   ├── stores/         # Pinia state management
│   │   └── router/         # Vue Router configuration
│   └── tests/
├── .agents/
│   └── skills/             # Agent skills (see below)
├── requirements.md         # Full requirements
└── design-specs.md         # Design specifications
```

## Agent Skills Available

Located in `.agents/skills/`:

1. **fastapi-skill** - FastAPI patterns, Pydantic, SQLAlchemy
2. **video-processing-skill** - FFmpeg, yt-dlp, time-based video chunking with sentence snap
3. **transcription-skill** - Whisper, pysubs2
4. **llm-task-skill** - llama-cpp-python, GPU config, streaming

## Key Design Patterns

### Backend

1. **Repository Pattern** - Abstract DB operations
2. **Service Layer** - Business logic separation (async)
3. **Async I/O** - All I/O operations use async/await
4. **No Authentication** - Single user, no auth required

### Frontend

1. **Vue Composables** - Data fetching and state
2. **Service Layer** - API client abstraction
3. **Component Composition** - Reusable Vue components
4. **Pinia Stores** - State management

## Coding Standards

### Python
- Type hints mandatory
- Async/await for ALL I/O operations (DB, file, HTTP, LLM)
- Pydantic v2 for validation
- SQLAlchemy 2.0 async
- **No background tasks** - Process immediately and wait

### TypeScript
- Strict type checking
- Vue 3.5 Composition API with `<script setup>`
- Composables for logic

## Task Priorities

1. **Phase 1**: Foundation (Docker, DB, Single LLM setup)
2. **Phase 2**: Video Pipeline (YouTube download → chunk → transcribe in one async flow)
3. **Phase 3**: LLM Integration (Qwen3.5-2B fixed model)
4. **Phase 4**: Learning Features (Study plans, vocabulary)
5. **Phase 5**: Speaking Practice
6. **Phase 6**: Polish & Testing

**No separate queue/course phase** - Video processing happens immediately when URL submitted.

## LLM Configuration

- **Fixed Model**: Qwen3.5-2B-Q4_K_M.gguf
- **Quantization**: Q4_K_M (GGUF format)
- **Framework**: llama-cpp-python (Python bindings, no separate container)
- **GPU Support**: NVIDIA GPU detection and auto-configuration
- **NVIDIA**: GPUtil + CUDA backend
- **GPU Configuration**:
  - `LLM_GPU_LAYERS=-1`: Auto-detect based on available VRAM
  - `LLM_GPU_LAYERS=N`: Offload N specific layers
  - `LLM_GPU_LAYERS=0`: Force CPU-only mode
- **VRAM Calculation**: Automatically calculates optimal layers (~80MB/layer for 2B Q4_K_M)
- **Safety Buffer**: Leaves 1GB VRAM free for other operations
- **Streaming**: Supported for real-time token generation
- **No Task Queue** - All LLM calls are async and wait for completion
- **No Model Switching** - Single fixed model only

## Video Processing

### Source
- **YouTube only** - Users provide YouTube URLs
- No local file uploads or NAS support

### Processing Flow (Immediate, Async)
```
POST /api/videos/youtube
↓
1. Download (yt-dlp) - async
2. Segment (timestamp-based, 5-min) - async
3. Snap to sentence boundaries - align chunks to transcript sentence head/tail
4. Transcribe (YouTube subtitle first, Whisper fallback) - async
5. Generate study plan (LLM) - async
6. Return complete video object
```

API waits for all steps to complete before returning response.

### Chunking Strategy
- **Time-based with sentence snap**: ~5 minutes, snap to head/tail of sentences
- **No physical splitting**: Use original video with timestamp segments
- Sentence-aware boundaries: Chunks align with transcript sentences
- Sequential virtual chunks: (0:00-5:00), (5:00-10:00), etc. with sentence boundaries
- Video player seeks to timestamp when navigating chunks

## Storage Structure

Data is stored under PROJECT_ROOT/data/:

```
PROJECT_ROOT/data/
├── db/
│   └── learning.db     # SQLite database file
├── models/             # LLM model files (Qwen3.5-2B-Q4_K_M.gguf)
├── videos/             # Downloaded from YouTube (original file)
├── transcripts/        # JSON (YouTube subtitles or Whisper output)
├── audios/             # Extracted audio
└── courses/            # Course data
```

In Docker: PROJECT_ROOT is explicitly set to `/app` via environment variable, so data is at `/app/data/`

**Note**: No physical chunk files - chunks are virtual with timestamps into the original video. Chunks snap to sentence boundaries.

## API Behavior

### All Endpoints Are Synchronous (Wait for Completion)

```python
# API waits for full processing before returning
@app.post("/api/videos/youtube")
async def create_video_from_youtube(request: YouTubeRequest):
    # 1. Download (async)
    video_path = await download_youtube(request.url)
    # 2. Segment (async - virtual chunks with timestamps)
    chunks = await segment_video(video_path, chunk_duration=300)
    # 3. Snap to sentences (async - align to transcript)
    chunks = await snap_to_sentences(chunks, transcript)
    # 4. Transcribe (async)
    transcript = await transcribe_video(video_path)
    # 5. Generate study plan (async)
    study_plan = await generate_study_plan(transcript)
    # Return complete result
    return VideoResponse(
        video=video,
        chunks=chunks,
        transcript=transcript,
        study_plan=study_plan
    )
```

Frontend shows loading state while waiting for completion.

## Testing

- **Unit**: pytest (backend), Vitest (frontend)
- **Integration**: pytest + testcontainers
- **E2E**: Playwright

## Common Commands

### Backend (using uv)

```bash
cd backend

# Create virtual environment and install dependencies
uv sync

# Install with dev dependencies
uv sync --extra dev

# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Run the application
uv run uvicorn app.main:app --reload

# Run with specific Python version
uv run --python 3.13 uvicorn app.main:app --reload

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Update dependencies
uv sync --upgrade

# Lock dependencies
uv lock
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

### Docker

```bash
docker-compose up -d
docker-compose logs -f
```

### Database

```bash
# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Downgrade
uv run alembic downgrade -1
```

### LLM Setup (NVIDIA GPU)

```bash
# Install with CUDA support
cd backend
uv pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121

# Re-lock dependencies
uv lock
```

## Resources

- FastAPI: https://fastapi.tiangolo.com
- SQLAlchemy: https://docs.sqlalchemy.org
- Vue: https://vuejs.org
- llama-cpp-python: https://github.com/abetlen/llama-cpp-python
