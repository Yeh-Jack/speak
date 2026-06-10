# English Learning Backend

FastAPI-based backend for AI-powered English learning platform.

## Features

- **Single-user application** - no authentication required
- SQLite database with SQLAlchemy async ORM (learning.db)
- Alembic migrations
- GPU auto-detection for LLM inference (NVIDIA, with CPU fallback)
- Async I/O operations throughout
- Video processing: YouTube download → chunk → transcribe → study plan
- Hybrid Dynamic chunking with ±30s sentence boundary snap
- Checkpoint-resume for video processing errors

## Tech Stack

- FastAPI + Python 3.12 + uv
- SQLite3 (data/db/learning.db)
- llama-cpp-python (Qwen3.5-2B-Q4_K_M.gguf) - **requires Python 3.12 for CUDA**
- yt-dlp + FFmpeg
- faster-whisper

## Setup

### Prerequisites

- Python 3.12 (required for CUDA/llama-cpp-python support - Python 3.13+ not supported)
- FFmpeg
- Docker & Docker Compose (optional)

### Development

```bash
cd backend
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Docker

```bash
docker-compose up -d
docker-compose logs -f
docker-compose exec backend uv run alembic upgrade head
```

## Data Storage

```
data/
├── db/learning.db         # SQLite
├── videos/                # Downloaded YouTube videos
├── subtitles/             # Subtitle files
├── transcripts/          # JSON transcripts
├── audios/               # Extracted audio chunks
└── models/               # LLM model files
```

In Docker: PROJECT_ROOT is `/app`, so data is at `/app/data/`

## API Documentation

- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## Processing States

```
pending → downloading → downloading_complete → transcribing →
transcribing_complete → chunking → chunking_complete →
extracting_audio → audio_extracted → studying → ready
                                                    ↓
                                                  failed
```

Use `POST /api/v1/videos/{id}/retry` to resume from checkpoint.

## API Endpoints

### Videos (`/api/v1/videos`)
- `GET /` - List videos
- `GET /{id}` - Get video
- `POST /youtube` - Create from YouTube
- `POST /info` - Get video metadata
- `PATCH /{id}` - Update video
- `DELETE /{id}` - Delete video
- `POST /{id}/retry` - Retry processing

### Chunks & Audio
- `GET /{id}/chunks` - Get chunks
- `GET /{id}/chunks/{idx}/audio` - Get chunk audio

### Transcripts
- `GET /{id}/transcripts/{type}` - Get transcript (user/youtube_author/whisper/youtube_auto)
- `POST /{id}/transcripts/user` - Upload user transcript

### Study Plans
- `GET /{id}/study-plans` - Get study plans
- `GET/PATCH /{id}/study-plans/{idx}` - Get/update study plan

### Chat (`/api/v1/chat`)
- `POST /` - Streaming AI tutor (SSE)

### Stats (`/api/v1/stats`)
- `GET /dashboard` - Dashboard statistics

### LLM (`/api/v1/llm`)
- `GET /gpu-status` - GPU detection status
- `GET /llm-health` - LLM health check

### Vocabulary (`/api/v1/vocabulary`)
- `GET /reviewed` - Reviewed words
- `GET /favorites` - Favorite words
- `POST /favorites/{word}/toggle` - Toggle favorite
- `POST /{word}/review` - SM-2 spaced repetition review

### Speaking (`/api/v1/speaking`)
- `GET /videos/{id}/segments` - Get speaking segments
- `GET /videos/{id}/audio-segment` - Extract audio segment
- `POST /videos/{id}/compare` - Compare recording

## Testing

```bash
uv run pytest
uv run pytest --cov=app
```