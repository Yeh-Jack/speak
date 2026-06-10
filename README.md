# English Speaking Learning App

AI-powered English learning platform using LLM as a personalized teacher.

## Overview

Users submit YouTube URLs (movies, TV shows, TED talks) and the system generates:
- **Personalized study plans** with learning objectives
- **Vocabulary lists** with CEFR levels
- **Grammar points** extracted from content
- **Speaking practice** with pronunciation feedback

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.12 + uv |
| Frontend | Vue 3.5 + TypeScript + Vite |
| Database | SQLite3 (learning.db) |
| LLM | llama-cpp-python (Qwen3.5-2B-Q4_K_M) |
| Video | FFmpeg + yt-dlp |
| Transcription | faster-whisper |

## Quick Start

### Local Development

**Backend (on Linux):**
```bash
# Install ffmpeg (example for Debian/Ubuntu)
sudo apt update && sudo apt install -y curl ffmpeg openssl

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# --- Install NVIDIA driver and CUDA tool kit if NVIDIA GPU ia available. ---

# Create virtual environment.
cd backend
uv venv
source .venv/bin/activate

# HTTPS is required for audio recording from microphone by MediaRecorder.
# Generate a self-signed SSL certificate for running HTTPS.
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=IP.OF.THE.HOST"

# Install dependent packages.
uv sync

# Configure the virtual environment.
cp .env.example .env
vi .env
cp ../frontend/.env.example ../frontend/.env
vi ../frontend/.env

# Start the backend server (also serves the frontend, PROJECT_ROOT is for serving frontend).
PROJECT_ROOT=/project/path uv run --python 3.12 uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload --ssl-keyfile key.pem --ssl-certfile cert.pem
```

**Frontend (for development with hot-deploy):**
```bash
cd frontend
pnpm install
pnpm dev
```

### Docker
**Not available yet.**
```bash
docker-compose up -d
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080/api/v1/

## Project Structure

```
.
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/       # API endpoints
│   │   ├── core/      # Config, logging
│   │   ├── db/        # Database session
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── repositories/  # Data access layer
│   │   └── services/  # Business logic
│   └── alembic/       # Database migrations
├── frontend/          # Vue 3.5 application
│   ├── src/
│   │   ├── components/  # Vue components
│   │   ├── views/       # Page components
│   │   ├── composables/ # Vue composables
│   │   ├── services/    # API client
│   │   └── stores/      # Pinia stores
├── data/              # Data storage (gitignored)
│   ├── db/            # SQLite database
│   ├── videos/        # Downloaded videos
│   ├── subtitles/      # Downloaded auto-generated subtitles
│   ├── transcripts/   # JSON transcripts
│   └── models/        # LLM model files
└── docs/              # Documentation
```

## Processing Pipeline

When a user submits a YouTube URL:

```
1. Download (yt-dlp) → MP4/WebM + auto-generated subtitles
2. Transcribe (Whisper - always, regardless of YouTube subtitles)
3. Chunk (Hybrid Dynamic + ±30s sentence snap, using transcript)
4. Generate Study Plan (LLM: Qwen3.5-2B)
```

All processing is **immediate async** - no background queues.
Frontend shows loading state while waiting for completion.

## Hybrid Dynamic Chunking

Video chunks are calculated using Hybrid Dynamic chunking with sentence-aware boundaries:
- Target: ~5 minutes per chunk
- For each ideal boundary, search ±30s for nearest sentence-ending punctuation
- Snap chunk end to the full sentence boundary
- Chunks are **virtual** - use original video with timestamps for navigation

## Checkpoint-Resume

If processing fails at any step, the video stays in the last successful state with `error_message` set. Users can retry via `POST /api/videos/{id}/retry`.

## Key Design Decisions

- **Single-user app** - No authentication
- **YouTube only** - Video source supports YouTube only
- **Single fixed LLM** - Qwen3.5-2B-Q4_K_M.gguf only (no model switching)
- **No background queues** - All processing immediate async with await

## Documentation

- [Design Specifications](design-specs.md) - Architecture, patterns, database schema
- [Requirements](requirements.md) - Full technical specification
- [AGENTS.md](AGENTS.md) - Agent instructions and skills

## License

MIT