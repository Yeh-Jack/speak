# English Learning App - Technical Specification

## Project Overview

An AI-powered English education platform using LLM as a personalized teacher. **Single-user application** - no authentication required. Users provide YouTube URLs (movies, TV shows, TED talks) and the system generates personalized study plans and vocabulary lists.

**Target Users**: Individual English learners seeking personalized, self-paced video-based education

**Key Differentiator**: Uses YouTube video content with AI-generated study plans and vocabulary lists. No exams - focus on learning, not testing.

---

## Tech Stack

| Component | Technology | Version/Notes |
|-----------|------------|---------------|
| **Backend** | FastAPI | Python 3.13+ |
| **Frontend** | Vue 3.5 + TypeScript + pnpm | Modern browsers (5 years) |
| **Database** | SQLite3 | Single file (learning.db) with WAL mode |
| **Authentication** | None | Single user, no auth required |
| **LLM Engine** | llama-cpp-python | Single fixed model: Qwen3.5-2B-Q4_K_M.gguf |
| **Storage** | Local SSD | No NAS support |

---

## LLM Configuration

- **Fixed Model**: Qwen3.5-2B-Q4_K_M.gguf (single model, no switching)
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
- **No Model Switching** - Single fixed model only

---

## Core Requirements

### 1. Video Management

#### 1.1 Video Source
- **YouTube URLs only** - Users submit YouTube video URLs
- **No local file uploads** - No MP4/WebM upload support
- **No NAS storage** - Local storage only
- **Processing**: Immediate async processing (no queue)

#### 1.2 Video Processing Flow (Immediate, Async)

```
POST /api/videos/youtube
↓
1. Download YouTube video + auto-generated subtitles (yt-dlp) - async I/O
   Subtitles saved to subtitles/ folder
2. Transcribe (YouTube subtitles first, Whisper fallback) - async
   Uses subtitles as basis for transcript
3. Segment video (calculate timestamps, ~5-min with sentence snap) - async
   Uses transcript for sentence-aware chunk boundaries
4. Generate study plan (LLM) - async
5. Return complete video object with all data
```

**API Behavior**: The endpoint waits for ALL processing to complete before returning. Frontend shows loading state.

**Key Design**: Transcription happens BEFORE chunking to enable sentence-aware chunk boundary detection.

#### 1.3 Video Chunking with Sentence Snap

**Hybrid Dynamic Chunking Algorithm:**
- **Duration**: ~5 minutes (default 300s, user-adjustable 60-600s)
- **Method**: Calculate ideal 5-min positions, then search ±30s for nearest sentence boundary
- **Prerequisite**: Transcript must be generated FIRST (from downloaded subtitles)
- **Sentence Detection**: Look for `.`, `!`, `?` punctuation in transcript
- **Snap Behavior**: If sentence boundary found within ±30s of ideal position, extend/shrink chunk to it
- **Storage**: Keep original video only, use timestamps for navigation
- **Error Handling**: Checkpoint-resume - if processing fails, retry from last successful state

**Example:**
- Target chunk: 0:00-5:00 (ideal)
- Search range: 4:30-5:30 for sentence boundary
- Transcript: sentence ends at 4:52 with `.`
- Actual chunk: 0:00-4:52 (snaps to sentence)
- Next chunk: 4:52-9:52 (searches for next boundary)

#### 1.4 Storage Structure

Data is stored under PROJECT_ROOT/data/:

```
PROJECT_ROOT/data/
├── db/
│   └── learning.db     # SQLite database file
├── models/             # LLM model files (Qwen3.5-2B-Q4_K_M.gguf)
├── videos/             # Downloaded from YouTube (original file)
├── subtitles/          # Downloaded auto-generated subtitles (.json3, .vtt, .srt, .ass, .lrc)
├── transcripts/        # JSON (YouTube subtitles or Whisper output)
├── audios/             # Extracted audio for Whisper
└── courses/            # Course data
```

In Docker: PROJECT_ROOT is `/app`, so data is at `/app/data/`

**Note**: No physical chunk files - chunks are virtual with timestamps into the original video. Chunks snap to sentence boundaries.

---

### 2. Subtitle/Transcript Processing

#### 2.1 Subtitle/Transcript Strategy
- **Simultaneous download**: Video and auto-generated subtitles downloaded together via yt-dlp
- **Subtitles storage**: Saved to `subtitles/` folder with language suffix (e.g., `video_id.en.json3`)
- **YouTube subtitles first**: Parse downloaded subtitles as basis for transcript
- **Whisper fallback**: If YouTube subtitles unavailable or insufficient, transcribe using faster-whisper
- **Transcribe before chunk**: Transcript is generated first, then used for sentence-aware chunk boundary detection

---

### 3. Video Courses

#### 3.1 Course Creation
- Pick multiple YouTube videos
- Create a training course
- Videos are listed in order (no background processing queue)

#### 3.2 Data Model
```python
class VideoCourse:
    id: UUID
    title: str                      # e.g., "English through TED Talks - Week 1"
    description: str
    videos: List[VideoCourseItem]
    current_index: int              # Current position in course
    status: pending | active | completed
    created_at: datetime
    updated_at: datetime

class VideoCourseItem:
    id: UUID
    course_id: UUID
    video_id: UUID
    order_index: int                # Position in course
    study_plan: JSON                # Generated by LLM (at video creation time)
    created_at: datetime
```

#### 3.3 Course Processing
- Videos are processed **immediately** when added (no queue)
- Each video returns complete with study plan before being added to course
- Allow reordering of videos in course

---

### 4. Learning Modes

#### 4.1 Reading Mode
- Display subtitles synchronized with video
- Vocabulary highlighting (CEFR levels)
- Hover definitions for difficult words
- Navigate by sentence or timestamp

#### 4.2 Listening Mode
- Audio playback with video
- Adjustable playback speed: 0.5x - 1.5x
- Loop specific sentences
- Hide subtitles (blind listening)

#### 4.3 Speaking Mode (Shadowing)
- **Shadowing**: Play audio → User repeats → Compare
- **Pronunciation Check**:
  - User records via Web Speech API
  - Compare with reference using Whisper
  - Show similarity score and feedback
- Adjustable playback speed
- Sentence-by-sentence practice

#### 4.4 Resume Functionality
- Save breakpoint: `timestamp` + `sentence_index`
- Resume options:
  - 5 seconds backward from timestamp
  - 3 sentences backward from current sentence
- Automatic save every 30 seconds

---

### 5. Study Plan Generation

#### 5.1 LLM-Generated Study Plan
- Analyze transcript + video metadata
- Generate structured learning path per video/chunk
- Include:
  - Learning objectives
  - Key vocabulary with definitions
  - Grammar points
  - Cultural notes (if applicable)
  - Estimated time

#### 5.2 Study Plan Structure
```json
{
  "video_id": "uuid",
  "title": "Video Title",
  "duration": "10:00",
  "chunks": [
    {
      "index": 0,
      "start": "00:00",
      "end": "05:00",
      "objectives": ["Learn 10 new vocabulary words"],
      "vocabulary": [
        {"word": "innovation", "definition": "...", "cefr": "B2", "context": "..."}
      ],
      "grammar": ["Present perfect tense"],
      "notes": "..."
    }
  ],
  "overall_difficulty": "B1",
  "estimated_time": "2 hours"
}
```

#### 5.3 Vocabulary Extraction
- Extract difficult words from transcript
- CEFR level estimation (A1-C2)
- Context sentences from video
- Store in vocabulary list for review

---

### 6. LLM Processing (Immediate, Async)

#### 6.1 Processing Model
- **No task queue** - All LLM calls are immediate async operations
- **Single fixed model** - Qwen3.5-2B-Q4_K_M.gguf only, no model switching
- API endpoints wait for completion before returning
- Frontend shows loading indicators for long operations

#### 6.2 LLM Operations
| Operation | Description | When Called |
|-----------|-------------|-------------|
| `generate_study_plan` | Generate learning plan for video | During video creation (immediate) |
| `chat_with_teacher` | LLM conversational response | When user sends chat message |
| `analyze_vocabulary` | Extract vocabulary from transcript | During video creation (immediate) |

#### 6.3 Processing Flow
```
User Request → FastAPI → Async I/O Operations → LLM → Return Result → User
                              ↓ ↓
                    (wait for completion) (streaming supported)
```

---

### 7. API Endpoints

#### 7.1 Video Courses
```
POST /api/courses                    # Create course
GET /api/courses                     # List courses
GET /api/courses/{id}                # Get course details
PUT /api/courses/{id}               # Update course
DELETE /api/courses/{id}            # Delete course
POST /api/courses/{id}/videos       # Add video to course (waits for processing)
PUT /api/courses/{id}/videos/reorder # Reorder videos
POST /api/courses/{id}/start        # Start learning course
```

#### 7.2 Videos (YouTube Only) - Immediate Processing
```
POST /api/videos/youtube            # Submit YouTube URL → waits for full processing
GET /api/videos                     # List videos
GET /api/videos/{id}                # Get video details
GET /api/videos/{id}/chunks         # Get video chunks (with sentence snap)
POST /api/videos/{id}/transcript    # Regenerate transcript
```

**Note**: `POST /api/videos/youtube` is a **long-running synchronous endpoint**. It:
1. Downloads the video (async)
2. Chunks it with sentence snap (async)
3. Generates transcript (async)
4. Generates study plan via LLM (async)
5. Returns complete video object only when all done

#### 7.3 Learning
```
GET /api/courses/{id}/study-plan     # Get generated study plan
GET /api/progress/{video_id}        # Get current progress
PUT /api/progress/{video_id}        # Update progress (resume)
GET /api/vocabularies               # Get vocabulary list
POST /api/vocabularies/{word}/review # Mark word as reviewed
```

#### 7.4 Speaking
```
POST /api/speaking/record           # Submit audio recording
GET /api/speaking/compare/{id}      # Get pronunciation comparison
POST /api/speaking/shadowing       # Submit shadowing practice
```

#### 7.5 LLM & Chat
```
POST /api/chat                      # Chat with LLM teacher
POST /api/chat/stream               # Streaming chat response
```

**Note**: No authentication endpoints, no user management, no exam endpoints.

---

## Implementation Phases

### Phase 1: Foundation (1 week)
- Project structure setup
- Docker + docker-compose configuration
- SQLite schema design (single user, no auth)
- Basic FastAPI structure

### Phase 2: Video Pipeline (1 week)
- YouTube download integration (yt-dlp)
- **Hybrid Dynamic chunking** with ±30s sentence snap
- **Checkpoint-resume state machine** for error recovery
- **Immediate async processing** (no queue)
- Local storage configuration
- Video processing states: pending → downloading → downloading_complete → chunking → chunking_complete → transcribing → transcribing_complete → studying → ready (or failed)

### Phase 3: Transcription (1 week)
- YouTube subtitle extraction (yt-dlp)
- Whisper integration (faster-whisper)
- Sentence boundary detection
- Transcript storage and retrieval

### Phase 4: LLM Integration (1 week)
- llama.cpp Python bindings setup
- Single fixed model: Qwen3.5-2B-Q4_K_M.gguf
- Study plan generation endpoint
- Chat endpoint with streaming
- **No model switching** - single model only

### Phase 5: Learning Features (1 week)
- Video player with subtitle sync
- Study plan display
- Vocabulary extraction and storage
- CEFR level estimation
- Shadowing mode

### Phase 6: Speaking Practice (1 week)
- Web Speech API integration
- Audio recording and upload
- Pronunciation comparison (Whisper)
- Shadowing mode with adjustable speed
- Feedback generation

### Phase 7: Statistics & Polish (1 week)
- Study progress tracking
- Interactive charts with pyecharts
- Time-based comparisons
- UI/UX improvements
- Error handling
- Performance optimization
- Documentation

**Total Estimated Duration: 7 weeks**

---

## Technical Constraints

### Video Constraints
- **YouTube URLs only** - No local file uploads
- Download as WebM using yt-dlp
- Video format: **MP4 and WebM only**
- Audio format: **MP3 and WebM only**
- No video format conversion (only chunking)
- **Chunking with sentence snap**: ~5 minutes, align to transcript sentences

### LLM Constraints
- **Single fixed model**: Qwen3.5-2B-Q4_K_M.gguf (no switching)
- Use llama-cpp-python (Python bindings, no separate container)
- OpenAI-compatible API via Python bindings
- Q4_K_M quantization (GGUF format)
- GPU auto-detection with CPU fallback
- Streaming output supported
- **No model switching** - single model only

### Storage Constraints
- Local storage only (no NAS)
- SQLite single-file database
- Videos downloaded from YouTube stored locally

### Performance Constraints
- Single concurrent user per deployment (single user app)
- **No background queues** - All processing is immediate async
- Chunk-based LLM processing (no timeout limits)
- API endpoints wait for completion (show loading UI)

---

## Success Criteria

### Functional Requirements
- [ ] Users can submit YouTube URLs
- [ ] System processes videos immediately (download → chunk with sentence snap → transcribe → study plan)
- [ ] Videos chunked into ~5-minute segments with sentence boundaries
- [ ] Subtitles extracted from YouTube first, Whisper fallback if unavailable
- [ ] Users can create courses with multiple videos
- [ ] LLM generates study plans immediately during video creation
- [ ] Resume functionality (5 sec or 3 sentences back)
- [ ] Reading, listening, and speaking modes functional
- [ ] **Single fixed LLM model** (Qwen3.5-2B-Q4_K_M.gguf)
- [ ] **No authentication required** (single user)
- [ ] **No exam system** (focus on learning)

### Non-Functional Requirements
- [ ] Single concurrent user support
- [ ] Video player works in modern browsers (5 years)
- [ ] LLM responses under 30 seconds (no timeout)
- [ ] All API operations use async I/O
- [ ] No authentication required
- [ ] Frontend loading states for long operations
- [ ] Interactive charts for progress tracking

---

## Document History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-04-08 | 1.0 | AI Assistant | Initial specification |
| 2025-04-10 | 2.0 | AI Assistant | Simplified: YouTube-only, no OAuth, fixed chunks |
| 2025-04-10 | 3.0 | AI Assistant | Removed job queue: all processing immediate async |
| 2025-04-24 | 4.0 | AI Assistant | Simplified: single user, no auth, no exams, fixed LLM, sentence snap |

---

## Appendix

### A. FFmpeg Commands

```bash
# Extract audio for Whisper
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 audio.wav
```

### B. Docker Compose Services

```yaml
services:
  backend: FastAPI + Python 3.13+ + llama-cpp-python
  frontend: Vue 3.5 + TypeScript
# Note: No PostgreSQL, no Redis, no Celery, no task queue, no auth service
```

**Note**: llama-cpp-python is integrated into the backend container, no separate LLM service needed.

### C. Environment Variables

**Fixed System Constants** (set automatically, not configurable):
- `PROJECT_ROOT` - Application root directory (Docker: `/app`, Local: calculated from file location)
- `STORAGE_BASE_PATH` - Fixed at `PROJECT_ROOT/data`
- `DATABASE_URL`      - Fixed at `PROJECT_ROOT/data/db/learning.db`
- `LLM_MODEL_PATH`    - Fixed at `PROJECT_ROOT/data/models`
- `SENTENCE_SNAP`     - Fixed at `True`

**Configurable Environment Variables**:

```bash
# In Docker, PROJECT_ROOT is explicitly set by Dockerfile
PROJECT_ROOT=/app

# LLM (llama-cpp-python) - Single fixed model
DEFAULT_MODEL=Qwen3.5-2B-Q4_K_M.gguf
LLM_GPU_LAYERS=-1             # -1=auto, 0=CPU only, N=specific layers
LLM_CONTEXT_SIZE=4096         # Model context window
LLM_THREADS=4                 # CPU threads for inference

# YouTube Download
YOUTUBE_DOWNLOAD_QUALITY=720  # 360, 480, 720, 1080
YOUTUBE_AUDIO_QUALITY=128k    # Audio quality for extraction

# Chunking
CHUNK_DURATION=300            # Target duration in seconds (~5 min)
```

---

**End of Specification**
