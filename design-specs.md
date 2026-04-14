# Design Specifications & Coding Guidelines

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Directory Structure](#directory-structure)
3. [Design Patterns](#design-patterns)
4. [Coding Guidelines](#coding-guidelines)
5. [API Design](#api-design)
6. [Database Design](#database-design)
7. [Security Guidelines](#security-guidelines)
8. [Testing Strategy](#testing-strategy)
9. [Logging & Monitoring](#logging--monitoring)
10. [Performance Guidelines](#performance-guidelines)

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ Frontend (React)                                                │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐       │
│ │ Login    │ │ Course   │ │ Video    │ │ Exam System    │       │
│ │ Email    │ │ List     │ │ Player   │ │ (SM-2)         │       │
│ └──────────┘ └──────────┘ └──────────┘ └────────────────┘       │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API + WebSocket
┌────────────────────────────┴────────────────────────────────────┐
│ Backend (FastAPI) - Async I/O                                   │
│ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────┐       │
│ │ Auth      │ │ Video     │ │ LLM       │ │ Study       │       │
│ │ Service   │ │ Service   │ │ Service   │ │ Service     │       │
│ └───────────┘ └───────────┘ └───────────┘ └─────────────┘       │
│ ┌───────────┐ ┌───────────┐ ┌───────────┐                       │
│ │ Speaking  │ │ Exam      │ │ Vocab     │                       │
│ │ Service   │ │ Service   │ │ Service   │                       │
│ └───────────┘ └───────────┘ └───────────┘                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
┌───────────────────────┐  ┌─────────────────────────────────────┐
│ PostgreSQL            │  │ llama-cpp-python + GPUtil           │
│ (Database)            │  │ (GPU auto-detect)                   │
└───────────────────────┘  └─────────────────────────────────────┘

**No Queue** - All operations use async/await and wait for completion
```

### Component Responsibilities

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| **Frontend** | UI rendering, user interaction, video playback, audio recording | React 18+, TypeScript, Vite, pnpm |
| **API Gateway** | Request routing, authentication, rate limiting | FastAPI, JWT |
| **Auth Service** | User authentication (email/password), token management | JWT |
| **Video Service** | YouTube download, chunking, storage management | FFmpeg, yt-dlp |
| **Transcript Service** | YouTube subtitle extraction, Whisper transcription | pysubs2, faster-whisper |
| **LLM Service** | Model switching, chat completion, study plan generation, GPU auto-config | llama-cpp-python, GPUtil |
| **Study Service** | Progress tracking, vocabulary management, learning analytics | SQLAlchemy |
| **Exam Service** | Question generation, SM-2 algorithm, scoring | Custom implementation |

**No Background Task Queue** - All processing is immediate async I/O.

---

## Directory Structure

### Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   │
│   ├── api/                       # API layer
│   │   ├── __init__.py
│   │   ├── deps.py                # Dependencies (auth, db session)
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py        # Auth endpoints (email/password)
│   │   │   │   ├── courses.py     # Course endpoints
│   │   │   │   ├── videos.py      # Video endpoints (YouTube only)
│   │   │   │   ├── learning.py    # Learning endpoints
│   │   │   │   ├── speaking.py    # Speaking endpoints
│   │   │   │   ├── exams.py       # Exam endpoints
│   │   │   │   ├── models.py      # LLM model endpoints
│   │   │   │   └── chat.py        # Chat endpoints
│   │   │   └── router.py          # API router
│   │   └── v2/                    # Future API versions
│   │
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py            # JWT, password hashing
│   │   ├── config.py              # Pydantic settings
│   │   └── logger.py              # Logging configuration
│   │
│   ├── db/                        # Database layer
│   │   ├── __init__.py
│   │   ├── base.py                # Base class for models
│   │   ├── session.py             # Database session
│   │   └── init_db.py             # Database initialization
│   │
│   ├── models/                    # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── video.py
│   │   ├── course.py
│   │   ├── transcript.py
│   │   ├── study_plan.py
│   │   ├── vocabulary.py
│   │   └── exam.py
│   │
│   ├── schemas/                   # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── video.py
│   │   ├── course.py
│   │   ├── transcript.py
│   │   ├── study_plan.py
│   │   ├── vocabulary.py
│   │   ├── exam.py
│   │   └── chat.py
│   │
│   ├── services/                  # Business logic (async)
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── video_service.py       # Async YouTube download + chunk
│   │   ├── transcript_service.py  # Async transcription
│   │   ├── llm_service.py         # Async LLM calls
│   │   ├── study_service.py
│   │   ├── speaking_service.py
│   │   └── exam_service.py
│   │
│   └── utils/                     # Utilities
│       ├── __init__.py
│       ├── file_utils.py          # File operations
│ ├── chunk_utils.py # Video chunking (user-adjustable 1-10 min, default 5)
│       ├── subtitle_utils.py      # Subtitle parsing
│       ├── gpu_utils.py           # GPU detection and VRAM calculation
│       └── sm2_utils.py           # SM-2 algorithm
│
├── alembic/                       # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── scripts/                       # Utility scripts
│   ├── init_db.py
│   └── seed_data.py
│
├── pyproject.toml                 # Project configuration (uv/pip compatible)
├── uv.lock                        # Locked dependencies (uv)
├── Dockerfile                     # Backend Docker image
└── docker-compose.yml             # Docker Compose config

# Note: No tasks/ directory - all processing is immediate async
```

### Frontend Structure

```
frontend/
├── src/
│   ├── main.tsx                   # React entry point
│   ├── App.tsx                    # Root component
│   ├── vite-env.d.ts              # Vite type definitions
│   │
│   ├── components/                # Reusable components
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Spinner.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── video/
│   │   │   ├── VideoPlayer.tsx
│   │   │   ├── SubtitleTrack.tsx
│   │   │   ├── ChunkNavigator.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── learning/
│   │   │   ├── VocabularyCard.tsx
│   │   │   ├── StudyPlanView.tsx
│   │   │   ├── ProgressTracker.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── speaking/
│   │   │   ├── AudioRecorder.tsx
│   │   │   ├── PronunciationView.tsx
│   │   │   └── index.ts
│   │   │
│   │   └── exam/
│   │       ├── QuestionView.tsx
│   │       ├── ExamTimer.tsx
│   │       └── index.ts
│   │
│   ├── pages/                     # Page components
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── CourseListPage.tsx
│   │   ├── CourseDetailPage.tsx
│   │   ├── VideoPlayerPage.tsx
│   │   ├── SpeakingPracticePage.tsx
│   │   ├── ExamPage.tsx
│   │   └── SettingsPage.tsx
│   │
│   ├── hooks/                     # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useVideo.ts
│   │   ├── useLearning.ts
│   │   ├── useSpeaking.ts
│   │   ├── useExam.ts
│   │   └── index.ts
│   │
│   ├── services/                  # API services
│   │   ├── api.ts                 # Axios instance
│   │   ├── auth.service.ts
│   │   ├── course.service.ts
│   │   ├── video.service.ts
│   │   ├── learning.service.ts
│   │   ├── speaking.service.ts
│   │   ├── exam.service.ts
│   │   └── index.ts
│   │
│   ├── stores/                    # State management (Zustand/Redux)
│   │   ├── auth.store.ts
│   │   ├── course.store.ts
│   │   ├── video.store.ts
│   │   └── index.ts
│   │
│   ├── types/                     # TypeScript types
│   │   ├── user.ts
│   │   ├── course.ts
│   │   ├── video.ts
│   │   ├── transcript.ts
│   │   ├── exam.ts
│   │   └── index.ts
│   │
│   ├── utils/                     # Utility functions
│   │   ├── formatTime.ts
│   │   ├── formatDate.ts
│   │   ├── sm2.ts
│   │   └── index.ts
│   │
│   └── constants/                 # Constants
│       ├── routes.ts
│       ├── config.ts
│       └── index.ts
│
├── public/                        # Static assets
│   ├── favicon.ico
│   └── logo.svg
│
├── tests/                         # Test files
│   ├── components/
│   ├── pages/
│   └── utils/
│
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── index.html
```

---

## Design Patterns

### 1. Repository Pattern (Backend)

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from uuid import UUID

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base repository with CRUD operations"""

    def __init__(self, session):
        self.session = session

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]:
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        pass

    @abstractmethod
    async def create(self, obj: T) -> T:
        pass

    @abstractmethod
    async def update(self, id: UUID, obj: T) -> Optional[T]:
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        pass
```

### 2. Service Layer Pattern (Async)

```python
from typing import Optional
from uuid import UUID

class VideoService:
    """Business logic layer for videos (YouTube only, async)"""

    def __init__(self, video_repo, llm_service, storage_service):
        self.video_repo = video_repo
        self.llm_service = llm_service
        self.storage_service = storage_service

    async def get_video(self, video_id: UUID) -> Optional[Video]:
        """Get video by ID"""
        return await self.video_repo.get_by_id(video_id)

    async def create_video_from_youtube(self, url: str, user_id: UUID) -> Video:
        """
        Create new video from YouTube URL.
        Processes immediately: download → chunk → transcribe → study plan.
        """
        # 1. Create video record
        video = Video(youtube_url=url, user_id=user_id, source_type="youtube")
        video = await self.video_repo.create(video)

        # 2. Download (async I/O)
        video_path = await self._download_youtube(url)
        await self.video_repo.update_path(video.id, video_path)

        # 3. Chunk (async I/O via subprocess)
        chunks = await self._create_chunks(video_path)
        await self.chunk_repo.create_many(video.id, chunks)

        # 4. Transcribe (async I/O)
        transcript = await self._transcribe(video_path)
        await self.transcript_repo.create(video.id, transcript)

        # 5. Generate study plan (async LLM call)
        study_plan = await self._generate_study_plan(transcript)
        await self.study_plan_repo.create(video.id, study_plan)

        # 6. Update status
        await self.video_repo.update_status(video.id, "ready")

        return await self.video_repo.get_by_id(video.id)

    async def _download_youtube(self, url: str) -> Path:
        """Download video from YouTube (async)."""
        import asyncio
        process = await asyncio.create_subprocess_exec(
            "yt-dlp", url, "-o", "%(id)s.%(ext)s",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise VideoDownloadError(stderr.decode())
        # Return path to downloaded file
        ...

    async def _create_chunks(self, video_path: Path, chunk_duration: int = 300) -> List[VideoChunk]:
        """Create chunks with user-adjustable duration (async I/O)."""
        ...

    async def _transcribe(self, video_path: Path) -> Transcript:
        """Extract YouTube subtitles or Whisper (async)."""
        ...

    async def _generate_study_plan(self, transcript: Transcript) -> StudyPlan:
        """Generate study plan via LLM (async)."""
        ...
```

### 3. Factory Pattern (LLM Provider)

```python
from abc import ABC, abstractmethod
from typing import List, Optional, AsyncGenerator
from pydantic import BaseModel
from llama_cpp import Llama

class ChatMessage(BaseModel):
    role: str
    content: str

class LLMProvider(ABC):
    """Abstract LLM provider interface"""

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        pass

    @abstractmethod
    async def chat_completion_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> AsyncGenerator[str, None]:
        """Stream tokens as they're generated"""
        pass

class LlamaCppProvider(LLMProvider):
    """llama-cpp-python implementation with GPU auto-detection"""

    def __init__(
        self,
        model_path: str,
        gpu_layers: int = -1,
        context_size: int = 4096,
        model_size: str = "7B",
        total_layers: int = 35
    ):
        from app.utils.gpu_utils import gpu_manager

        self.model_path = model_path
        self.context_size = context_size
        self._llm: Optional[Llama] = None

        # Auto-detect GPU layers if not specified
        if gpu_layers == -1:
            import os
            self.gpu_layers = gpu_manager.get_gpu_layers_config(
                env_value=os.getenv("LLM_GPU_LAYERS"),
                model_size=model_size,
                total_layers=total_layers
            )
        else:
            self.gpu_layers = gpu_layers

    async def _load_model(self):
        """Lazy load the model with GPU configuration"""
        if self._llm is None:
            self._llm = Llama(
                model_path=self.model_path,
                n_gpu_layers=self.gpu_layers,
                n_ctx=self.context_size,
                verbose=False
            )

    async def chat_completion(self, messages, temperature=0.7, max_tokens=2048):
        await self._load_model()
        response = self._llm.create_chat_completion(
            messages=[m.dict() for m in messages],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response['choices'][0]['message']['content']

    async def chat_completion_stream(
        self, messages, temperature=0.7, max_tokens=2048
    ) -> AsyncGenerator[str, None]:
        """Stream tokens for real-time UI updates"""
        await self._load_model()
        stream = self._llm.create_chat_completion(
            messages=[m.dict() for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        for chunk in stream:
            delta = chunk['choices'][0].get('delta', {})
            if 'content' in delta:
                yield delta['content']

class LLMService:
    """LLM service with provider switching and GPU auto-detection"""

    def __init__(self):
        self.providers = {}
        self.current_provider: Optional[str] = None

    def register_provider(self, name: str, provider: LLMProvider):
        self.providers[name] = provider

    def set_provider(self, name: str):
        if name not in self.providers:
            raise ValueError(f"Provider {name} not found")
        self.current_provider = name

    async def chat(self, messages: List[ChatMessage], stream: bool = False, **kwargs):
        if not self.current_provider:
            raise ValueError("No provider selected")
        provider = self.providers[self.current_provider]
        if stream:
            return provider.chat_completion_stream(messages, **kwargs)
        return await provider.chat_completion(messages, **kwargs)
```

---

## Coding Guidelines

### General Principles

1. **Follow SOLID Principles**
   - Single Responsibility: Each class/function has one job
   - Open/Closed: Open for extension, closed for modification
   - Liskov Substitution: Subtypes must be substitutable
   - Interface Segregation: Many specific interfaces > one general
   - Dependency Inversion: Depend on abstractions

2. **DRY (Don't Repeat Yourself)**
   - Extract common logic into utilities
   - Use inheritance and composition

3. **KISS (Keep It Simple, Stupid)**
   - Prefer simple solutions
   - Avoid over-engineering

### Python Guidelines

#### 1. Type Hints (Mandatory)

```python
# ✅ Good
from typing import Optional, List, Dict
from uuid import UUID

def get_user(user_id: UUID) -> Optional[User]:
    ...

def process_videos(videos: List[Video]) -> Dict[str, int]:
    ...

# ❌ Bad
def get_user(user_id):
    ...
```

#### 2. Async/Await (ALL I/O Operations)

```python
# ✅ Good - Use async for ALL I/O operations
async def download_video(url: str) -> Path:
    """Download from YouTube (I/O bound)."""
    import asyncio
    process = await asyncio.create_subprocess_exec(
        "yt-dlp", url, ...
    )
    await process.communicate()
    return path

async def transcribe_audio(audio_path: Path) -> Transcript:
    """Transcribe audio (I/O bound)."""
    ...

async def generate_study_plan(transcript: Transcript) -> StudyPlan:
    """Generate study plan via LLM (async I/O)."""
    response = await llm.chat([...])
    return response

# ✅ Good - Sync for CPU-bound operations
def parse_subtitle(text: str) -> List[Subtitle]:
    """Parse subtitle text (CPU bound)."""
    return parser.parse(text)
```

#### 3. Error Handling

```python
# ✅ Good - Specific exceptions
from app.exceptions import VideoNotFoundError, TranscriptionError

async def process_video(video_id: UUID):
    try:
        video = await video_repo.get_by_id(video_id)
        if not video:
            raise VideoNotFoundError(f"Video {video_id} not found")
        await transcribe(video)
    except VideoNotFoundError:
        logger.error(f"Video not found: {video_id}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise TranscriptionError(f"Failed to process video: {e}")

# ❌ Bad - Bare except
async def process_video(video_id: UUID):
    try:
        ...
    except:
        pass
```

#### 4. Dependency Injection

```python
# ✅ Good - Inject dependencies
class VideoService:
    def __init__(
        self,
        video_repo: VideoRepository,
        llm_service: LLMService,
        storage_service: StorageService
    ):
        self.video_repo = video_repo
        self.llm_service = llm_service
        self.storage_service = storage_service

# ❌ Bad - Import globals
class VideoService:
    def __init__(self):
        from app.db.repositories import VideoRepository  # Bad!
        self.video_repo = VideoRepository()
```

#### 5. Pydantic Models

```python
# ✅ Good - Use Pydantic for validation
from pydantic import BaseModel, Field, validator

class YouTubeVideoCreate(BaseModel):
    youtube_url: str = Field(..., min_length=10)
    title: Optional[str] = Field(None, max_length=200)

    @validator('youtube_url')
    def validate_youtube_url(cls, v):
        if 'youtube.com' not in v and 'youtu.be' not in v:
            raise ValueError('Invalid YouTube URL')
        return v

# ❌ Bad - Plain dicts
def create_video(data: dict):
    ...
```

#### 6. Logging

```python
# ✅ Good - Use structured logging
import logging

logger = logging.getLogger(__name__)

async def process_video(video_id: UUID, user_id: UUID):
    logger.info(f"Starting video processing", extra={
        "video_id": str(video_id),
        "user_id": str(user_id)
    })

    try:
        ...
        logger.info(f"Video processed successfully", extra={
            "video_id": str(video_id),
            "duration": duration
        })
    except Exception as e:
        logger.error(f"Video processing failed: {e}", exc_info=True)
        raise

# ❌ Bad - Print statements
print(f"Processing video {video_id}")
```

### TypeScript Guidelines

#### 1. Strict Type Safety

```typescript
// ✅ Good - Explicit types
interface User {
  id: string;
  email: string;
  createdAt: Date;
}

async function getUser(id: string): Promise<User | null> {
  const response = await api.get<User>(`/api/users/${id}`);
  return response.data;
}

// ❌ Bad - Any types
async function getUser(id: any): any {
  ...
}
```

#### 2. React Best Practices

```typescript
// ✅ Good - Functional components with hooks
import React, { useState, useEffect } from 'react';

interface VideoPlayerProps {
  videoId: string;
  onProgress: (progress: number) => void;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({
  videoId,
  onProgress
}) => {
  const [currentTime, setCurrentTime] = useState(0);

  const handleTimeUpdate = (time: number) => {
    setCurrentTime(time);
    onProgress(time);
  };

  return (
    <video
      src={`/api/videos/${videoId}/stream`}
      onTimeUpdate={(e) => handleTimeUpdate(e.currentTarget.currentTime)}
    />
  );
};
```

---

## API Design

### RESTful Principles

1. **Resource-based URLs**
```
GET /api/v1/videos           # List videos
POST /api/videos/youtube     # Create video from YouTube (sync, waits for processing)
GET /api/v1/videos/{id}      # Get video
DELETE /api/v1/videos/{id}   # Delete video
```

2. **Use HTTP Methods Correctly**
   - GET: Retrieve resources (safe, idempotent)
   - POST: Create resources (may be long-running, waits for completion)
   - PUT: Replace resources (idempotent)
   - PATCH: Partial update
   - DELETE: Remove resources (idempotent)

3. **Standard Response Format**
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2025-04-08T10:00:00Z"
}
```

4. **Error Response Format**
```json
{
  "success": false,
  "error": {
    "code": "VIDEO_NOT_FOUND",
    "message": "Video with ID 'xxx' not found",
    "details": { ... }
  },
  "timestamp": "2025-04-08T10:00:00Z"
}
```

5. **Pagination**
```
GET /api/v1/videos?page=1&limit=20&sort=created_at&order=desc
```

Response:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

---

## Database Design

### Key Tables

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Videos (YouTube only)
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    source_type VARCHAR(50) NOT NULL DEFAULT 'youtube',
    youtube_url VARCHAR(1000) NOT NULL,
    file_path VARCHAR(1000),              -- Downloaded file path
    duration FLOAT NOT NULL,
    chunk_duration FLOAT DEFAULT 300,     -- User-adjustable: 60-600 seconds, default 300
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Video Chunks (virtual - timestamps only, no physical files)
CREATE TABLE video_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,         -- Sequential: 0, 1, 2...
    start_time FLOAT NOT NULL,            -- In seconds (e.g., 0, 300, 600...)
    end_time FLOAT NOT NULL,              -- In seconds (e.g., 300, 600, 900...)
    duration FLOAT NOT NULL,              -- Calculated: end_time - start_time
    -- Note: No file_path - use original video file with timestamps
    transcript JSONB,                     -- [{start: 0.0, end: 5.0, text: "..."}]
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(video_id, chunk_index)
);

-- Courses
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    current_video_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Course Videos (junction table)
CREATE TABLE course_videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    order_index INTEGER NOT NULL,
    study_plan JSONB,                     -- Generated by LLM
    exam_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(course_id, order_index)
);

-- Study Progress
CREATE TABLE study_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    current_timestamp FLOAT NOT NULL,
    sentence_index INTEGER,
    completed BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, video_id, chunk_index)
);

-- Vocabulary
CREATE TABLE vocabularies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    word VARCHAR(200) NOT NULL,
    definition TEXT,
    context TEXT,
    cefr_level VARCHAR(10),
    review_count INTEGER DEFAULT 0,
    next_review DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, word)
);

-- Indexes
CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_chunks_video_id ON video_chunks(video_id);
CREATE INDEX idx_courses_user_id ON courses(user_id);
CREATE INDEX idx_progress_user_video ON study_progress(user_id, video_id);
CREATE INDEX idx_vocabularies_user ON vocabularies(user_id);

-- Note: No task/background_tasks table - processing is immediate
```

---

## Security Guidelines

### 1. Authentication

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
```

### 2. Input Validation

```python
# ✅ Good - Validate all inputs
from pydantic import BaseModel, Field, validator

class YouTubeVideoCreate(BaseModel):
    youtube_url: str = Field(..., min_length=10)
    title: Optional[str] = Field(None, max_length=200)

    @validator('youtube_url')
    def validate_youtube_url(cls, v):
        if 'youtube.com' not in v and 'youtu.be' not in v:
            raise ValueError('Invalid YouTube URL')
        return v
```

### 3. CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Testing Strategy

### Test Levels

1. **Unit Tests** - Test individual functions/classes
2. **Integration Tests** - Test component interactions
3. **E2E Tests** - Test complete user flows

### Python Testing (pytest)

```python
# tests/unit/test_video_service.py
import pytest
from app.services.video_service import VideoService

@pytest.mark.asyncio
async def test_create_video_from_youtube(video_service):
    video = await video_service.create_video_from_youtube(
        url="https://youtube.com/watch?v=xxx",
        user_id="uuid"
    )
    assert video.youtube_url == "https://youtube.com/watch?v=xxx"
    assert video.user_id == "uuid"
    # Verify all processing completed (download, chunk, transcribe, study plan)
    assert video.status == "ready"
    chunks = await video_service.get_chunks(video.id)
    assert len(chunks) > 0

@pytest.mark.asyncio
async def test_video_processing_pipeline(video_service):
    """Test complete pipeline runs without errors."""
    video = await video_service.create_video_from_youtube(
        url="https://youtube.com/watch?v=test",
        user_id="user-uuid"
    )
    assert video.status == "ready"
    assert video.file_path is not None
    chunks = await video_service.get_chunks(video.id)
    assert len(chunks) > 0
    transcript = await video_service.get_transcript(video.id)
    assert transcript is not None
    study_plan = await video_service.get_study_plan(video.id)
    assert study_plan is not None
```

### Frontend Testing (Vitest + React Testing Library)

```typescript
// tests/components/VideoPlayer.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { VideoPlayer } from '@/components/video/VideoPlayer';

test('displays video title', async () => {
  render(<VideoPlayer videoId="test-id" title="Test Video" />);
  expect(screen.getByText('Test Video')).toBeInTheDocument();
});
```

---

## Video Chunking (Time-Based Only)

### Overview

The system uses **virtual time-based chunking** (user-adjustable 1-10 minutes, default 5).
- No physical splitting - use original video with timestamps
- No character-based or scene-based chunking
- No speaker diarization
- Sequential virtual chunks: (0:00-5:00), (5:00-10:00), etc.
- Video player seeks to timestamp for navigation

### Processing Flow (Immediate, Async)

```
┌─────────────────────────────────────────────────────────────┐
│ POST /api/videos/youtube                                    │
└────────┬────────────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Download Video (yt-dlp) → WebM                           │
│    async subprocess call                                      │
└────────┬────────────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Extract Audio (FFmpeg) → WAV                             │
│    async subprocess call                                    │
└────────┬────────────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Calculate Segments (5-min intervals, timestamps only)      │
│    Virtual chunks: (0:00-5:00), (5:00-10:00), etc.            │
│    No physical file splitting                                  │
└────────┬────────────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Extract/Generate Subtitles                                 │
│    - Try YouTube subtitles (yt-dlp --write-subs)            │
│    - Fallback to Whisper (faster-whisper)                     │
└────────┬────────────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Generate Study Plan (LLM)                                │
│    - Analyze transcript                                       │
│    - Generate objectives, vocabulary, grammar                 │
└────────┬────────────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Return Complete Video Object                             │
│    - video metadata                                          │
│    - chunks list                                             │
│    - transcript                                              │
│    - study plan                                              │
└─────────────────────────────────────────────────────────────┘
```

### API Response Example

```python
@app.post("/api/videos/youtube")
async def create_video_from_youtube(request: YouTubeRequest):
    """
    Create video from YouTube URL.
    This is a LONG-RUNNING endpoint that waits for all processing.
    """
    # All operations are async and awaited
    video = await video_service.create_video_from_youtube(
        url=request.url,
        user_id=request.user_id
    )

    # Return complete result
    return VideoResponse(
        video=VideoSchema(
            id=video.id,
            title=video.title,
            status="ready",
            youtube_url=video.youtube_url
        ),
        chunks=[
            ChunkSchema(
                index=chunk.index,
                start_time=chunk.start_time,
                end_time=chunk.end_time,
                file_path=chunk.file_path
            )
            for chunk in video.chunks
        ],
        transcript=TranscriptSchema(
            segments=[...]
        ),
        study_plan=StudyPlanSchema(
            objectives=[...],
            vocabulary=[...],
            grammar=[...]
        )
    )
```

### Chunking Service

```python
# app/services/chunking_service.py
from pathlib import Path
import asyncio
from typing import List
from dataclasses import dataclass

@dataclass
class VideoChunk:
    """A virtual video chunk with timestamps (no physical file)."""
    index: int
    start_time: float  # seconds (e.g., 0, 300, 600...)
    end_time: float    # seconds (e.g., 300, 600, 900...)
    duration: float    # seconds (should be ~300)
    # Note: No file_path - use original video with timestamps

class ChunkingService:
    """
    Virtual time-based chunking with timestamps only.
    No physical splitting - video player seeks to timestamps.
    """

    async def create_chunks(
        self,
        video_duration: float,
        chunk_duration: int = 300  # User-adjustable 60-600 seconds
    ) -> List[VideoChunk]:
        """
        Calculate virtual chunks with timestamps.
        No physical file creation - just timestamp math.
        
        Args:
            video_duration: Total video duration in seconds
            chunk_duration: Desired chunk duration (default 300s = 5min)
        
        Returns:
            List of VideoChunk with timestamps
        """
        chunks = []
        current_time = 0.0
        chunk_index = 0
        
        while current_time < video_duration:
            end_time = min(current_time + chunk_duration, video_duration)
            
            chunks.append(VideoChunk(
                index=chunk_index,
                start_time=current_time,
                end_time=end_time,
                duration=end_time - current_time
            ))
            
            current_time = end_time
            chunk_index += 1
        
        return chunks

    async def get_video_duration(self, video_path: Path) -> float:
        """Get video duration using ffprobe (async)."""
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        return float(stdout.decode().strip())
```

---

## Character Speaking Mode (Impersonation Practice)

### Overview

A specialized practice mode where users learn to speak like a specific character from the video.

### Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. SHOW                                                     │
│    - Display character's subtitle on screen                 │
│    - Highlight current sentence                             │
└────────┬────────────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. PLAY (Once)                                              │
│    - Play character's original audio once                   │
│    - Video player seeks to sentence timestamp                 │
│    - Auto-stop at end of sentence                             │
└────────┬────────────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. ROLLBACK                                                 │
│    - Auto-seek 3 seconds back (or to sentence start)          │
│    - Pause, ready for user recording                          │
└────────┬────────────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. USER SPEAK                                                 │
│    - Show recording UI (red dot, waveform)                  │
│    - User presses record and speaks the line                  │
│    - Auto-stop recording (or manual stop)                   │
└────────┬────────────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. REPEAT OPTION (User Choice)                                │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│    │ Compare  │  │ Retry    │  │ Next     │                 │
│    │ (Step 6) │  │ (Step 2) │  │ Sentence │                 │
│    └──────────┘  └──────────┘  └──────────┘                 │
└────────┬────────────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. COMPARISON (Optional)                                      │
│    - Play original audio                                      │
│    - Play user recording                                      │
│    - Show Whisper similarity score                            │
│    - Show pronunciation feedback                              │
└─────────────────────────────────────────────────────────────┘
```

### UI Components

```typescript
// CharacterSpeakingMode.tsx
interface CharacterSpeakingModeProps {
  videoId: string;
  characterName: string;  // "Iron Man", "TED Speaker", etc.
  transcript: TranscriptSegment[];
}

interface SpeakingState {
  phase: 'show' | 'play' | 'rollback' | 'record' | 'compare';
  currentSentence: TranscriptSegment;
  userRecording: Blob | null;
  comparisonResult: ComparisonResult | null;
}
```

### Backend API

```python
# Speaking Service
class SpeakingService:
    
    async def extract_audio_segment(
        self,
        video_path: Path,
        start_time: float,
        end_time: float
    ) -> Path:
        """Extract audio segment for a specific sentence (async)."""
        output_path = Path(f"/tmp/audio_{start_time}_{end_time}.wav")
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-ss", str(start_time),
            "-t", str(end_time - start_time),
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            str(output_path)
        ]
        process = await asyncio.create_subprocess_exec(*cmd)
        await process.communicate()
        return output_path
    
    async def compare_recordings(
        self,
        original_audio_path: Path,
        user_audio_path: Path
    ) -> ComparisonResult:
        """Compare user's recording with original using Whisper."""
        # Transcribe both
        original_text = await self.transcribe(original_audio_path)
        user_text = await self.transcribe(user_audio_path)
        
        # Calculate similarity
        similarity = calculate_similarity(original_text, user_text)
        
        return ComparisonResult(
            similarity_score=similarity,
            feedback=self.generate_feedback(original_text, user_text)
        )
```

### Data Model

```python
# User speaking practice record
class SpeakingPracticeRecord:
    id: UUID
    user_id: UUID
    video_id: UUID
    segment_start: float      # Timestamp in video
    segment_end: float
    character_text: str       # Original character line
    user_recording_path: str  # Path to user's audio
    similarity_score: float   # 0.0 - 1.0
    feedback: str             # LLM-generated feedback
    attempts: int             # Number of retries
    created_at: datetime
```

---

## GPU Configuration Utilities

### NVIDIA and AMD GPU Detection

The project supports NVIDIA (CUDA) and AMD (ROCm) GPUs with automatic vendor detection and backend selection.

#### GPU Vendors and Backends

| Vendor | Detection Method | Backend | Notes |
|--------|-----------------|---------|-------|
| **NVIDIA** | GPUtil | CUDA | Best performance, most mature |
| **AMD** | rocm-smi / pyamdgpuinfo | ROCm | Linux only for pyamdgpuinfo |

```python
# app/utils/gpu_utils.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

class GPUVendor(Enum):
    NVIDIA = "nvidia"
    AMD = "amd"
    UNKNOWN = "unknown"

class GPUBackend(Enum):
    CUDA = "cuda"
    ROCM = "rocm"
    CPU = "cpu"

@dataclass
class GPUInfo:
    id: int
    name: str
    vendor: GPUVendor
    total_memory_mb: float
    free_memory_mb: float
    backend: GPUBackend

class GPUManager:
    """GPU manager for NVIDIA and AMD LLM configuration."""

    def detect_all_gpus(self) -> List[GPUInfo]:
        """Detect GPUs from NVIDIA and AMD."""
        self._gpus = []
        self._detect_nvidia()  # GPUtil
        self._detect_amd()     # rocm-smi or pyamdgpuinfo
        return self._gpus

    def _detect_nvidia(self) -> bool:
        """Detect NVIDIA GPUs using GPUtil."""
        try:
            import gputil
            gpus = gputil.getGPUs()
            for gpu in gpus:
                self._gpus.append(GPUInfo(
                    id=len(self._gpus),
                    name=gpu.name,
                    vendor=GPUVendor.NVIDIA,
                    total_memory_mb=gpu.memoryTotal,
                    free_memory_mb=gpu.memoryFree,
                    backend=GPUBackend.CUDA
                ))
            return True
        except ImportError:
            return False

    def _detect_amd(self) -> bool:
        """Detect AMD GPUs using rocm-smi or pyamdgpuinfo."""
        # Try pyamdgpuinfo first (Linux only)
        try:
            import pyamdgpuinfo
            for device in pyamdgpuinfo.get_devices():
                self._gpus.append(GPUInfo(
                    id=len(self._gpus),
                    name=device.name or "AMD GPU",
                    vendor=GPUVendor.AMD,
                    total_memory_mb=device.memory_info.vram_total / (1024**2),
                    free_memory_mb=device.memory_info.vram_free / (1024**2),
                    backend=GPUBackend.ROCM
                ))
            return True
        except ImportError:
            pass
        # Fallback to rocm-smi
        return self._detect_amd_rocm_smi()

    def get_best_gpu(self) -> Optional[GPUInfo]:
        """Get the best GPU (priority: NVIDIA > AMD)."""
        if not self._gpus:
            self.detect_all_gpus()

        priority = {GPUVendor.NVIDIA: 2, GPUVendor.AMD: 1}
        sorted_gpus = sorted(
            self._gpus,
            key=lambda g: (priority.get(g.vendor, 0), g.free_memory_mb),
            reverse=True
        )
        return sorted_gpus[0] if sorted_gpus else None

    def get_llama_config(self, model_path: str, env_gpu_layers: str = "-1") -> dict:
        """Get complete llama-cpp-python configuration."""
        config = {"model_path": model_path, "n_ctx": 4096}

        if env_gpu_layers == "0":
            config["n_gpu_layers"] = 0
            config["backend"] = "cpu"
            return config

        gpu = self.get_best_gpu()
        if not gpu:
            config["n_gpu_layers"] = 0
            config["backend"] = "cpu"
            return config

        # Calculate optimal layers (~150MB per layer for 7B)
        layer_memory = 150  # MB
        available_vram = gpu.free_memory_mb - 1024  # Safety buffer
        max_layers = int(available_vram / layer_memory)
        layers = min(max_layers, 35)  # 35 layers for 7B model

        config["n_gpu_layers"] = layers
        config["backend"] = gpu.backend.value
        return config

# Singleton instance
gpu_manager = GPUManager()
```

### Multi-Vendor Installation (using uv)

```bash
# NVIDIA (CUDA)
uv pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121

# AMD (ROCm)
uv pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/rocm62

# After installing GPU-specific wheels, re-lock dependencies
uv lock
```

### GPU Configuration Environment Variables

```bash
# GPU Configuration
LLM_GPU_LAYERS=-1                    # -1=auto-detect, 0=CPU, N=specific layers
LLM_MODEL_SIZE=7B                  # 3B, 5B, 7B, 8B (for VRAM calculation)
LLM_CONTEXT_SIZE=4096              # Model context window

# llama-cpp-python will auto-detect backend:
# NVIDIA -> CUDA
# AMD -> ROCm
# No GPU detected -> CPU
```

### Usage in LLM Service

```python
from app.utils.gpu_utils import gpu_manager
from llama_cpp import Llama
import os

# Get complete configuration
config = gpu_manager.get_llama_config(
    model_path="/data/models/qwen2.5-7b-q4_k_m.gguf",
    env_gpu_layers=os.getenv("LLM_GPU_LAYERS", "-1")
)

# Initialize LLM with calculated configuration
llm = Llama(**config)
```

### VRAM Estimates by Model Size

| Model Size | Layers | VRAM/Layer | Total GPU VRAM (Full) |
|------------|--------|------------|------------------------|
| 3B (Llama 3.2) | 28 | ~80MB | ~2.2GB |
| 5B (Gemma 4) | 28 | ~100MB | ~2.8GB |
| 7B (Qwen2.5) | 35 | ~150MB | ~5.3GB |
| 8B (Gemma 4) | 36 | ~170MB | ~6.1GB |

---

## Logging & Monitoring

### Logging Configuration

```python
# app/core/logger.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
```

### Log Levels

| Level | Usage |
|-------|-------|
| DEBUG | Detailed debugging info |
| INFO | General operational info |
| WARNING | Unexpected but handled |
| ERROR | Error preventing operation |
| CRITICAL | System-wide failure |

---

## Performance Guidelines

### 1. Database Optimization

- Use indexes on frequently queried columns
- Use async database operations (SQLAlchemy async)
- Implement connection pooling
- Use database migrations (Alembic)

### 2. Caching Strategy

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_model(model_name: str):
    # Cache model loading
    pass
```

### 3. Video Processing (Immediate Async)

- **No queue** - Process immediately using async/await
- Use async subprocess for FFmpeg/yt-dlp
- Stream large files instead of loading into memory
- Use virtual chunking (timestamps only, no file splitting)
- Frontend shows loading state while processing

### 4. Frontend Optimization

- Code splitting with React.lazy
- Lazy load images and videos
- Debounce/throttle user inputs
- Use React.memo for expensive components
- Show loading indicators for long API calls

---

## Document History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-04-08 | 1.0 | AI Assistant | Initial specification |
| 2025-04-10 | 2.0 | AI Assistant | Simplified: YouTube-only, no OAuth, fixed chunks |
| 2025-04-10 | 3.0 | AI Assistant | Removed job queue: all processing immediate async |

---

**End of Design Specifications**
