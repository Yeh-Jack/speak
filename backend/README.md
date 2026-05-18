# English Learning Backend

FastAPI-based backend for the AI-powered English education platform.

## Features

- **Single-user application** - no authentication required
- SQLite database with SQLAlchemy async ORM (learning.db)
- Alembic migrations
- GPU auto-detection for LLM inference (NVIDIA only, with CPU fallback)
- Async I/O operations throughout
- Video processing pipeline: YouTube download → chunk → transcribe → study plan
- **Hybrid Dynamic chunking** with ±30s sentence boundary snap
- **Checkpoint-resume** for video processing errors

## Tech Stack

- FastAPI + Python 3.13+ + uv
- SQLite3 (single file: data/db/learning.db)
- llama-cpp-python (Qwen3.5-2B-Q4_K_M.gguf)
- yt-dlp + FFmpeg (video processing)
- faster-whisper (transcription fallback)

## Setup

### Prerequisites

- Python 3.13+
- FFmpeg
- Docker & Docker Compose (optional)

### Development Setup

1. Create virtual environment and install dependencies:
```bash
cd backend
uv sync
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run migrations:
```bash
uv run alembic upgrade head
```

4. Start the development server:
```bash
uv run uvicorn app.main:app --reload
```

### Docker Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec backend uv run alembic upgrade head
```

## Data Storage

Data is stored under `data/`:
- `data/db/learning.db` - SQLite database
- `data/videos/` - Downloaded YouTube videos
- `data/models/` - LLM model files (Qwen3.5-2B-Q4_K_M.gguf)
- `data/transcripts/` - JSON transcripts
- `data/audios/` - Extracted audio for Whisper

In Docker: PROJECT_ROOT is `/app`, so data is at `/app/data/`

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Video Processing States

The video processing pipeline uses a state machine:
```
pending → downloading → downloading_complete → chunking → chunking_complete
→ transcribing → transcribing_complete → studying → ready
                                                         ↓
                                                       failed
```

On failure, the video remains in the last successful state with `error_message` set.
Use `POST /api/videos/{id}/retry` to resume from the checkpoint.

## Database Migrations

```bash
# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Downgrade
uv run alembic downgrade -1
```

## Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=app
```
