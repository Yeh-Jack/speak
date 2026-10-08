# Graph Report - speak  (2026-10-08)

## Corpus Check
- 150 files · ~79,376 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 6, .example 2, .toml 1)

## Summary
- 1903 nodes · 2916 edges · 125 communities (102 shown, 23 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 107 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6b67366a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Base
- TestProcessVideo
- test_transcription_service.py
- test_chunking_service.py
- Design Specifications & Coding Guidelines
- video_service.py
- English Speaking Learning App - System Architecture
- videos.py
- ShadowingMode.vue
- VideoPlayerView.vue
- VideoPlayer.vue
- Study Progress Statistics Design Document
- Frontend Documentation
- GPUManager
- compilerOptions
- TranscriptionService
- Video Processing Skill
- DashboardView.vue
- schemas/__init__.py
- English Speaking Learning App - Project Presentation
- English Speaking Learning App - Project Presentation
- AGENTS.md
- schemas/progress.py
- Backend Documentation
- VideoService
- LLMService
- get_log_level
- API Endpoints
- endpoints/speaking.py
- main.py
- video.service.ts
- LLM Task Skill
- endpoints/vocabulary.py
- useI18n.ts
- StudyProgress
- MarkdownText.vue
- test_video_service.py
- asyncio
- Study Statistics Implementation Plan
- Exam System Skill
- chat
- StudyPlanRepository
- SpeakingService
- StatsService
- TestModuleLevelConstants
- TestSettings
- StudyPlanDisplay.vue
- devDependencies
- dependencies
- compare_recording
- .get_with_chunks
- schemas/study_plan.py
- ChunkRepository
- SQLite3 Migration Implementation Plan
- conftest.py
- TranscriptRepository
- TestCalculateSimilarity
- design-specs.md
- Transcription Skill
- Phase 2: Video Processing Pipeline Implementation Plan
- English Speaking Learning App
- create_video_from_youtube
- package.json
- VocabularyCard.vue
- Guidelines
- asyncio
- BaseRepository
- test_speaking_service.py
- schemas/transcript.py
- TestGenerateFeedback
- English Learning Frontend
- compilerOptions
- English Speaking Learning App - Technical Specification
- sqlalchemy
- ChatService
- English Speaking Learning App - Agent Instructions
- TestRetryVideo
- logging.py
- TestSettingsEnvOverride
- Implementation Phases
- TestSpeakingServiceInitialization
- api.ts
- Core Requirements
- TestLogLevel
- scripts
- pull_request_template.md
- BaseButton.vue
- ChunkingService
- 7. API Endpoints
- 1. Video Management
- 4. Learning Modes
- Technical Constraints
- Settings
- 3. Video Courses
- 6. LLM Processing (Immediate, Async)
- Coding Standards
- .__init__
- Appendix
- Video
- build_img.sh
- db/__init__.py
- app/__init__.py
- vite.config.ts
- tests/unit/__init__.py
- english-learning-backend
- env.py
- AI Tutor Chat Streaming Spec
- streamChat
- .dict

## God Nodes (most connected - your core abstractions)
1. `VideoService` - 40 edges
2. `VideoRepository` - 30 edges
3. `Base` - 25 edges
4. `Video` - 25 edges
5. `BaseRepository` - 24 edges
6. `Vocabulary` - 23 edges
7. `StudyPlanRepository` - 22 edges
8. `TranscriptRepository` - 22 edges
9. `DownloadService` - 20 edges
10. `VideoProcessingError` - 19 edges

## Surprising Connections (you probably didn't know these)
- `Implemented Services` --references--> `DownloadService`  [INFERRED]
  ARCHITECTURE.md → backend/app/services/download_service.py
- `Implemented Services` --references--> `TranscriptionService`  [INFERRED]
  ARCHITECTURE.md → backend/app/services/transcription_service.py
- `Implemented Services` --references--> `VideoService`  [INFERRED]
  ARCHITECTURE.md → backend/app/services/video_service.py
- `Self-Review` --references--> `streamChat()`  [INFERRED]
  docs/superpowers/plans/2026-08-05-chat-streaming-fix.md → frontend/src/services/video.service.ts
- `Task 1: Mutate the assistant message through the reactive proxy` --references--> `streamChat()`  [INFERRED]
  docs/superpowers/plans/2026-08-05-chat-streaming-fix.md → frontend/src/services/video.service.ts

## Import Cycles
- None detected.

## Communities (125 total, 23 thin omitted)

### Community 0 - "Base"
Cohesion: 0.16
Nodes (22): AsyncAttrs, Base, SQLAlchemy base class for all models., Base class for all SQLAlchemy models., Mixin to add created_at and updated_at timestamps., TimestampMixin, Chunk of a video with sentence-snapped boundaries., VideoChunk (+14 more)

### Community 1 - "TestProcessVideo"
Cohesion: 0.18
Nodes (9): MockVideo, asyncio, process_video should raise VideoProcessingError if video not found., Mock Video model for testing., process_video should set error_message on failure., process_video should return (video, timings) if video already ready., Tests for process_video state progression., TestProcessVideo (+1 more)

### Community 2 - "test_transcription_service.py"
Cohesion: 0.10
Nodes (22): Core module for the English Learning application., Tests for config module., download_service(), fixture, Tests for DownloadService., Create DownloadService with temp directory., asyncio, fixture (+14 more)

### Community 3 - "test_chunking_service.py"
Cohesion: 0.06
Nodes (34): ChunkingConfig, Configuration for Hybrid Dynamic chunking., chunking_service(), asyncio, fixture, Tests for ChunkingConfig dataclass., ChunkingConfig should have correct default values., ChunkingConfig should accept custom values. (+26 more)

### Community 4 - "Design Specifications & Coding Guidelines"
Cohesion: 0.04
Nodes (45): 1. Input Validation, 1. Repository Pattern (Backend), 1. Strict Type Safety, 1. Type Hints (Mandatory), 2. Async/Await (ALL I/O Operations), 2. Service Layer Pattern (Async), 2. Vue 3.5 Best Practices, 3. CORS Configuration (+37 more)

### Community 5 - "video_service.py"
Cohesion: 0.07
Nodes (40): asyncio, Hybrid Dynamic chunking service with ±30s sentence boundary snap., DownloadService, Path, YouTube video download service using yt-dlp., Get video metadata without downloading. Args: youtube_url: Full YouTube URL…, Synchronous info extraction using yt-dlp. Note on YouTube subtitles: -…, Service for downloading YouTube videos using yt-dlp. (+32 more)

### Community 6 - "English Speaking Learning App - System Architecture"
Cohesion: 0.05
Nodes (40): 1. Download Service, 1. Repository Pattern, 2. Chunking Service (Hybrid Dynamic), 2. Service Layer Pattern, 3. State Machine Pattern, 3. Transcription Service, 4. Video Service (Orchestrator), API Reference (+32 more)

### Community 7 - "videos.py"
Cohesion: 0.11
Nodes (41): delete_video(), get_chunk_audio(), get_progress(), get_study_plan_by_chunk(), get_video(), get_video_chunks(), get_video_study_plans(), get_video_transcript() (+33 more)

### Community 8 - "ShadowingMode.vue"
Cohesion: 0.06
Nodes (36): allCompleted, audioLevel, beginRecording(), calculateSimilarity(), currentSentence, currentSentenceIndex, emit, fallbackToTTS() (+28 more)

### Community 9 - "VideoPlayerView.vue"
Cohesion: 0.06
Nodes (30): videoService, chatError, chatInput, chatMessages, chatMessagesContainer, currentTime, currentTranscriptSegments, error (+22 more)

### Community 10 - "VideoPlayer.vue"
Cohesion: 0.07
Nodes (32): buffered, containerRef, currentSubtitle, currentTime, duration, emit, formattedCurrentTime, formattedDuration (+24 more)

### Community 11 - "Study Progress Statistics Design Document"
Cohesion: 0.06
Nodes (35): API Caching, API Endpoints, Architecture, Backend, Chart 1: Study Timeline (Line/Area with DataZoom), Chart 2: Activity Heatmap (Calendar View), Chart 3: Weekly Comparison (Grouped Bar with Timeline), Chart 4: Video Progress (Horizontal Bar) (+27 more)

### Community 12 - "Frontend Documentation"
Cohesion: 0.06
Nodes (30): api (Axios instance), Components, Composables, DashboardView (`/`), Directory Structure, Environment Variables, Frontend Documentation, languageStore (+22 more)

### Community 13 - "GPUManager"
Cohesion: 0.16
Nodes (12): detect_all_gpus(), get_best_gpu(), GPUInfo, GPUManager, Detect NVIDIA GPUs using GPUtil., Get the best GPU for LLM inference., Calculate optimal GPU layers based on available VRAM., Get complete llama-cpp-python configuration. Returns dict with: - model_path:… (+4 more)

### Community 14 - "compilerOptions"
Cohesion: 0.09
Nodes (21): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleResolution (+13 more)

### Community 15 - "TranscriptionService"
Cohesion: 0.10
Nodes (19): Path, Extract speaker label if present (e.g., 'John: Hello')., Service for transcribing audio using faster-whisper., Initialize Whisper model. Model sizes: tiny, base, small, medium, large-v3 CPU-…, Lazy load the Whisper model., Transcribe audio file with word-level timestamps. Args: audio_path: Path to…, Service for parsing subtitle files (SRT, VTT, ASS, SSA)., Orchestrates dual transcription. 1. Always runs Whisper transcription 2. Also… (+11 more)

### Community 16 - "Video Processing Skill"
Cohesion: 0.07
Nodes (26): API Endpoints, Character-Based Chunking, Character Chunking Service, Chunking configuration, Chunking Modes, Chunking settings, Database Schema, Description (+18 more)

### Community 17 - "DashboardView.vue"
Cohesion: 0.08
Nodes (27): startRecording(), useAuth(), t(), videoService, chunkDuration, chunkDurationOptions, closeAddModal(), createVideoFromYouTube() (+19 more)

### Community 18 - "schemas/__init__.py"
Cohesion: 0.11
Nodes (26): Pydantic schemas for the English Learning application., ProcessingTimings, BaseModel, Enum, str, Video and VideoChunk schemas., Elapsed time metrics for video processing stages., Video processing state machine states. (+18 more)

### Community 19 - "English Speaking Learning App - Project Presentation"
Cohesion: 0.08
Nodes (25): English Speaking Learning App - Project Presentation, 問題 1：CUDA 支援與 Python 版本, 問題 2：瀏覽器音訊錄製, 問題 3：繁體中文支援, 如何建構 AI 賦能的 Python 應用程式, 投影片 10：問題與解決方案, 投影片 11：問題與解決方案, 投影片 12：問題與解決方案 (+17 more)

### Community 20 - "English Speaking Learning App - Project Presentation"
Cohesion: 0.08
Nodes (25): 1: CUDA Support & Python Version (CUDA 支援與 Python 版本), Checkpoint-Resume State Machine, English Speaking Learning App - Project Presentation, How to Build an AI-Enabled Python Application, Key Design Decisions, Problem 2: Audio Recording from Browser (瀏覽器音頻錄製), Problem 3: Traditional Chinese Support (繁體中文支援), Slide 10: Problems Encountered & Solutions (問題與解決方案) (+17 more)

### Community 21 - "AGENTS.md"
Cohesion: 0.08
Nodes (24): Add a dev dependency, Add a new dependency, API waits for full processing before returning, Apply migrations, Create migration, Create virtual environment and install dependencies, Downgrade, Generate study plan with highest priority transcript (user > whisper > youtube) (+16 more)

### Community 22 - "schemas/progress.py"
Cohesion: 0.21
Nodes (12): BaseModel, Study Progress schemas., Base study progress schema., Schema for creating study progress., Schema for updating study progress., Study progress response schema., Resume information for a video., ResumeInfo (+4 more)

### Community 23 - "Backend Documentation"
Cohesion: 0.08
Nodes (24): API Endpoints, Backend Documentation, Configuration, Database Models, Dependencies, Directory Structure, Environment Variables, Fixed (not configurable) (+16 more)

### Community 24 - "VideoService"
Cohesion: 0.19
Nodes (9): Path, Extract audio for each chunk in mp3 format. Args: video: Video model with…, Extract a specific audio chunk from video. Args: video_path: Path to video file…, Orchestrator for video processing pipeline. State Machine: pending ->…, VideoService, Tests for VideoService initialization., VideoService should initialize with custom service instances., VideoService should create default services when not provided. (+1 more)

### Community 25 - "LLMService"
Cohesion: 0.09
Nodes (15): LLM Operations, LLMService, Any, Path, Format transcript segments into a text string., Generate LLM response using chat completion., Stream LLM response token by token. Args: messages: List of message dicts with…, Extract and parse JSON from LLM response. (+7 more)

### Community 27 - "get_log_level"
Cohesion: 0.06
Nodes (28): _get_handlers(), get_log_level(), Get log level from environment variable or provided value. Args: env_value: Log…, Configure application-wide logging. Args: log_level: Log level string (default:…, Get logging handlers based on environment. Args: level: The logging level…, setup_logging(), Should use DEBUG_FORMAT when verbose is True., Should use DEFAULT_FORMAT when verbose is False. (+20 more)

### Community 28 - "API Endpoints"
Cohesion: 0.09
Nodes (21): API Documentation, API Endpoints, Chat (`/api/v1/chat`), Chunks & Audio, Data Storage, Development, Docker, English Learning Backend (+13 more)

### Community 29 - "endpoints/speaking.py"
Cohesion: 0.08
Nodes (27): get_db(), AsyncSession, Dependencies for API endpoints., Get database session for dependency injection. Commits on success. Endpoints…, Chat endpoints for AI tutor functionality., get_gpu_status(), get_llm_health(), get (+19 more)

### Community 30 - "main.py"
Cohesion: 0.07
Nodes (28): is_verbose(), Check if verbose mode is enabled via environment variable., _ensure_data_directories(), _ensure_database(), frontend_config(), health_check(), lifespan(), get (+20 more)

### Community 31 - "video.service.ts"
Cohesion: 0.15
Nodes (16): ChatMessage, StreamChatOptions, StudyPlanResponse, TranscriptResponse, VideoResponse, useVideoStore, GrammarItem, StudyObjective (+8 more)

### Community 32 - "LLM Task Skill"
Cohesion: 0.12
Nodes (16): API Endpoints, Architecture, Chat with Teacher, Dependencies, Description, Environment Variables, GPU Auto-Detection, Guidelines (+8 more)

### Community 33 - "endpoints/vocabulary.py"
Cohesion: 0.07
Nodes (39): FavoriteListResponse, FavoriteWord, get_favorite_vocabulary(), get_reviewed_vocabulary(), get_vocabulary(), AsyncSession, BaseModel, get (+31 more)

### Community 34 - "useI18n.ts"
Cohesion: 0.11
Nodes (18): { t }, videoStore, languageStore, isLearningPage, languageStore, route, { t }, useI18n() (+10 more)

### Community 35 - "StudyProgress"
Cohesion: 0.19
Nodes (9): Progress tracking for video chunks., StudyProgress, ProgressRepository, AsyncSession, UUID, Repository for StudyProgress model., Get progress for a specific video chunk., Get all progress for a video. (+1 more)

### Community 36 - "MarkdownText.vue"
Cohesion: 0.31
Nodes (6): props, rendered, renderMarkdown(), dompurify, marked, vitest

### Community 37 - "test_video_service.py"
Cohesion: 0.21
Nodes (8): ProcessingTimings, Elapsed time metrics for each processing stage., Tests for VideoService., Tests for ProcessingTimings dataclass., ProcessingTimings.to_dict should return properly formatted dict., ProcessingTimings should have sensible defaults., ProcessingTimings should round values to 2 decimal places., TestProcessingTimings

### Community 38 - "asyncio"
Cohesion: 0.13
Nodes (12): asyncio, Tests for save_recording method., save_recording should create file with audio data., save_recording should create parent directories if needed., Tests for extract_audio_segment method., extract_audio_segment should raise ValueError on FFmpeg failure., extract_audio_segment should use custom output path if provided., Tests for compare_recordings method. (+4 more)

### Community 39 - "Study Statistics Implementation Plan"
Cohesion: 0.12
Nodes (16): Chart Types:, File Structure Overview, Key Interactive Features Implemented:, Study Statistics Implementation Plan, Summary of Implementation, Task 10: Create Statistics Chart Component, Task 11: Final Integration and Testing, Task 1: Add pyecharts Dependency (+8 more)

### Community 40 - "Exam System Skill"
Cohesion: 0.12
Nodes (15): API Endpoints, Dependencies, Description, Environment Variables, Exam Generation with LLM, Exam Submission and Scoring, Exam System Skill, Guidelines (+7 more)

### Community 41 - "chat"
Cohesion: 0.18
Nodes (10): chat(), AsyncSession, post, Streaming chat endpoint for AI tutor (SSE). Streams tokens as they are…, ChatMessage, BaseModel, Chat schemas for AI tutor interface., Request for streaming chat. (+2 more)

### Community 42 - "StudyPlanRepository"
Cohesion: 0.17
Nodes (9): AsyncSession, UUID, Repository for StudyPlan model., Get study plan for a video (overall plan, chunk_index is null)., Get study plan for a specific chunk., Get all study plans for a video (including chunk-specific)., Create a study plan for a video and save vocabulary items to database., Save vocabulary items to the vocabulary table. (+1 more)

### Community 43 - "SpeakingService"
Cohesion: 0.18
Nodes (9): Path, Calculate simple text similarity between two strings. Uses word overlap ratio…, Compare user's recording with original using Whisper. Args:…, Service for speaking practice with audio comparison., Generate feedback based on comparison. Args: original_text: Original transcript…, Save user's recording to disk. Args: audio_data: Raw audio bytes (WebM/Opus)…, Extract audio segment from video for a specific time range. Args: video_path:…, Transcribe audio file using Whisper. Args: audio_path: Path to audio file… (+1 more)

### Community 44 - "StatsService"
Cohesion: 0.17
Nodes (9): AsyncSession, Count completed study chunks (proxy for sentences practiced)., Calculate total minutes studied today., Service for calculating dashboard statistics., Calculate dashboard statistics from study progress. Args: daily_goal_minutes:…, Count vocabulary items that have been reviewed at least once., Calculate total hours learned from all progress records., Calculate consecutive days with study activity. (+1 more)

### Community 45 - "TestModuleLevelConstants"
Cohesion: 0.12
Nodes (9): Tests for module-level constants., PROJECT_ROOT should be a Path object., DATA_DIR should be PROJECT_ROOT / 'data'., DATABASE_URL should be SQLite with aiosqlite., STORAGE_BASE_PATH should equal DATA_DIR., LLM_MODEL_PATH should be DATA_DIR / 'models'., SUBTITLES_DIR should be DATA_DIR / 'subtitles'., SENTENCE_SNAP should be True. (+1 more)

### Community 46 - "TestSettings"
Cohesion: 0.09
Nodes (12): Tests for Settings class., Settings should have DEFAULT_MODEL., Settings should have LLM_GPU_LAYERS., Settings should have LLM_CONTEXT_SIZE., Settings should have LLM_THREADS as positive int., Settings should have YOUTUBE_DOWNLOAD_QUALITY., Settings should have YOUTUBE_AUDIO_QUALITY., Settings should have CHUNK_DURATION as positive int. (+4 more)

### Community 47 - "StudyPlanDisplay.vue"
Cohesion: 0.12
Nodes (12): activeTab, completedVocabulary, emit, GrammarItem, grammarItems, progress, Props, StudyObjective (+4 more)

### Community 48 - "devDependencies"
Cohesion: 0.13
Nodes (15): devDependencies, autoprefixer, eslint, eslint-plugin-vue, jsdom, postcss, @types/node, typescript (+7 more)

### Community 49 - "dependencies"
Cohesion: 0.20
Nodes (10): dependencies, axios, clsx, dompurify, marked, pinia, tailwindcss, vue (+2 more)

### Community 50 - "compare_recording"
Cohesion: 0.21
Nodes (13): compare_recording(), get_audio_segment(), get_speaking_service(), get_video_segments(), AsyncSession, get, post, UUID (+5 more)

### Community 51 - ".get_with_chunks"
Cohesion: 0.40
Nodes (3): UUID, Get video with its chunks., Update video status and optionally error_message.

### Community 52 - "schemas/study_plan.py"
Cohesion: 0.24
Nodes (10): BaseModel, Base study plan schema., Schema for creating a study plan., Schema for updating a study plan., Study plan response schema., StudyPlan, StudyPlanBase, StudyPlanCreate (+2 more)

### Community 53 - "ChunkRepository"
Cohesion: 0.16
Nodes (8): ChunkRepository, AsyncSession, UUID, Repository for VideoChunk model., Get all chunks for a video., Get a specific chunk by video ID and index., Delete all chunks for a video and return count., Create multiple chunks.

### Community 54 - "SQLite3 Migration Implementation Plan"
Cohesion: 0.13
Nodes (14): File Structure Overview, Spec Coverage Check, SQLite3 Migration Implementation Plan, Task 10: Update Environment Example File, Task 11: Test Database Setup, Task 1: Update Configuration for SQLite3, Task 2: Update Database Session for SQLite3, Task 3: Update Base Model for SQLite UUID Compatibility (+6 more)

### Community 55 - "conftest.py"
Cohesion: 0.24
Nodes (9): tempfile, event_loop(), fixture, Pytest configuration for unit tests., Create event loop for async tests., Create temporary path for tests., Sample transcript for testing chunking service., sample_transcript() (+1 more)

### Community 56 - "TranscriptRepository"
Cohesion: 0.19
Nodes (8): AsyncSession, UUID, Repository for Transcript model., Get a single transcript for a video (first one found)., Get all transcripts for a video., Get transcript by video ID and source., Create a transcript for a video., TranscriptRepository

### Community 57 - "TestCalculateSimilarity"
Cohesion: 0.14
Nodes (8): Tests for calculate_similarity method., Full word match should return 1.0., Partial word match should return proportion., No common words should return 0.0., Empty original text should return 0.0., Empty user text should return 0.0., Comparison should be case insensitive., TestCalculateSimilarity

### Community 58 - "design-specs.md"
Cohesion: 0.14
Nodes (11): After installing GPU-specific wheels, re-lock dependencies, app/core/logger.py, app/services/chunking_service.py, app/utils/gpu_utils.py, Get complete configuration, GPU Configuration, Initialize LLM with calculated configuration, NVIDIA (CUDA) (+3 more)

### Community 59 - "Transcription Skill"
Cohesion: 0.15
Nodes (12): Dependencies, Description, Environment Variables, Guidelines, Notes, Orchestration Strategy Pattern, Speaker Diarization, Subtitle Parsing (+4 more)

### Community 60 - "Phase 2: Video Processing Pipeline Implementation Plan"
Cohesion: 0.15
Nodes (12): File Structure, Phase 2: Video Processing Pipeline Implementation Plan, Self-Review Checklist, Task 1: Create Custom Exceptions, Task 2: Create Download Service, Task 3: Create Chunking Service (Hybrid Dynamic), Task 4: Create Transcription Service, Task 5: Create Video Service (Orchestrator) (+4 more)

### Community 61 - "English Speaking Learning App"
Cohesion: 0.15
Nodes (13): Checkpoint-Resume, Docker, Documentation, English Speaking Learning App, Hybrid Dynamic Chunking, Key Design Decisions, License, Local Development (+5 more)

### Community 62 - "create_video_from_youtube"
Cohesion: 0.25
Nodes (8): create_video_from_youtube(), get_video_info(), post, Get metadata of a video from YouTube URL without DB operations., Create video from YouTube URL and process through full pipeline. This endpoint:…, Schema for creating a video from YouTube URL., VideoCreate, field_validator

### Community 63 - "package.json"
Cohesion: 0.11
Nodes (18): name, private, type, version, autoprefixer, clsx, eslint, eslint-plugin-vue (+10 more)

### Community 64 - "VocabularyCard.vue"
Cohesion: 0.20
Nodes (9): cardBorderClass, cefrColor, emit, isFlipped, isPlaying, playAudio(), Props, saveWord() (+1 more)

### Community 65 - "Guidelines"
Cohesion: 0.18
Nodes (10): Coding Patterns, Dependencies, Description, Example: Dependency Injection, Example: Service Layer, FastAPI Skill, Guidelines, Project Structure (+2 more)

### Community 66 - "asyncio"
Cohesion: 0.12
Nodes (13): asyncio, get_video_info should return video metadata without downloading., get_video_info should return defaults if extraction fails., Tests for DownloadService initialization., DownloadService should create videos and subtitles directories., Tests for download_video method., download_video should return video info dict on success., download_video should raise DownloadError if file doesn't exist after download. (+5 more)

### Community 67 - "BaseRepository"
Cohesion: 0.18
Nodes (10): ABC, BaseRepository, Any, AsyncSession, Base repository with CRUD operations., Get all entities with pagination., Update an existing entity., Delete an entity by ID. (+2 more)

### Community 68 - "test_speaking_service.py"
Cohesion: 0.25
Nodes (6): Speaking practice service for character impersonation mode., fixture, Tests for SpeakingService., Create SpeakingService with temp directory., speaking_service(), subprocess

### Community 69 - "schemas/transcript.py"
Cohesion: 0.27
Nodes (9): BaseModel, Schema for creating a transcript (user-uploaded)., Transcript response schema., Schema for user-uploaded subtitle content., A single transcript segment., TranscriptCreate, TranscriptResponse, TranscriptSegment (+1 more)

### Community 70 - "TestGenerateFeedback"
Cohesion: 0.20
Nodes (6): Low similarity (< 0.4) should give keep practicing feedback., Tests for _generate_feedback method., High similarity (>= 0.8) should give excellent feedback., Medium-high similarity (>= 0.6, < 0.8) should give good feedback., Medium similarity (>= 0.4, < 0.6) should give nice try feedback., TestGenerateFeedback

### Community 71 - "English Learning Frontend"
Cohesion: 0.20
Nodes (9): Docker, English Learning Frontend, Environment Variables, Key Features, Prerequisites, Project Structure, Setup, Tech Stack (+1 more)

### Community 72 - "compilerOptions"
Cohesion: 0.22
Nodes (8): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, strict, include

### Community 73 - "English Speaking Learning App - Technical Specification"
Cohesion: 0.20
Nodes (10): Document History, English Speaking Learning App - Technical Specification, Functional Requirements, Language Requirements, LLM Configuration, Mandatory Traditional Chinese (繁體中文), Non-Functional Requirements, Project Overview (+2 more)

### Community 74 - "sqlalchemy"
Cohesion: 0.13
Nodes (17): get_db(), init_sqlite_pragmas(), Database session management., Initialize SQLite pragmas for better performance and foreign key support., Get database session for dependency injection., Base repository with common CRUD operations., Video chunk repository., Repository layer for database operations. (+9 more)

### Community 75 - "ChatService"
Cohesion: 0.20
Nodes (5): ChatService, Cleanup model resources., Service for chat-based LLM interactions (AI tutor)., Lazy load the llama-cpp-python model., Generate a streaming chat response. Args: messages: List of message dicts with…

### Community 76 - "English Speaking Learning App - Agent Instructions"
Cohesion: 0.14
Nodes (14): Agent Skills Available, Architecture, Backend, Directory Structure, English Speaking Learning App - Agent Instructions, Frontend, Key Design Patterns, LLM Configuration (+6 more)

### Community 77 - "TestRetryVideo"
Cohesion: 0.33
Nodes (4): Tests for retry_video., retry_video should return immediately if video is ready., retry_video should raise error if video not found., TestRetryVideo

### Community 78 - "logging.py"
Cohesion: 0.07
Nodes (33): Application configuration using Pydantic settings., get_logger(), LogLevel, Enum, str, Centralized logging configuration for the application., Log level enumeration matching standard logging levels., Get a logger instance with the standard format. Args: name: Logger name… (+25 more)

### Community 79 - "TestSettingsEnvOverride"
Cohesion: 0.25
Nodes (5): Tests for Settings environment variable override., LLM_GPU_LAYERS should be overridable via env var., CHUNK_DURATION should be overridable via env var., ENVIRONMENT should be overridable via env var., TestSettingsEnvOverride

### Community 80 - "Implementation Phases"
Cohesion: 0.25
Nodes (8): Implementation Phases, Phase 1: Foundation (1 week), Phase 2: Video Pipeline (1 week), Phase 3: Transcription (1 week), Phase 4: LLM Integration (1 week), Phase 5: Learning Features (1 week), Phase 6: Speaking Practice (1 week), Phase 7: Statistics & Polish (1 week)

### Community 81 - "TestSpeakingServiceInitialization"
Cohesion: 0.50
Nodes (3): Tests for SpeakingService initialization., SpeakingService should create recordings directory., TestSpeakingServiceInitialization

### Community 82 - "api.ts"
Cohesion: 0.29
Nodes (5): api, Window, DashboardStats, statsService, axios

### Community 83 - "Core Requirements"
Cohesion: 0.29
Nodes (7): 2.1 Subtitle/Transcript Strategy, 2. Subtitle/Transcript Processing, 5.1 LLM-Generated Study Plan, 5.2 Study Plan Structure, 5.3 Vocabulary Extraction, 5. Study Plan Generation, Core Requirements

### Community 85 - "TestLogLevel"
Cohesion: 0.33
Nodes (4): Tests for LogLevel enum., LogLevel should have correct string values., LogLevel should be usable as string., TestLogLevel

### Community 86 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, test

### Community 87 - "pull_request_template.md"
Cohesion: 0.33
Nodes (5): Checklist:, Description, How Has This Been Tested?, Related issue: #, Type of change

### Community 88 - "BaseButton.vue"
Cohesion: 0.25
Nodes (6): Props, sizeClasses, variantClasses, emit, onInput(), Props

### Community 89 - "ChunkingService"
Cohesion: 0.14
Nodes (13): Implemented Services, ChunkingService, Create ideal chunks without sentence snap (fallback when no transcript)., A virtual video chunk with sentence-snapped timestamps., Hybrid Dynamic chunking with sentence-aware boundaries. Algorithm: 1. Calculate…, Check if text ends with sentence-ending punctuation., Find nearest sentence boundary within ±30s of target_time. Args: target_time:…, Create chunks with Hybrid Dynamic sentence-snap. Args: video_duration: Total… (+5 more)

### Community 92 - "7. API Endpoints"
Cohesion: 0.33
Nodes (6): 7.1 Video Courses, 7.2 Videos (YouTube Only) - Immediate Processing, 7.3 Learning, 7.4 Speaking, 7.5 LLM & Chat, 7. API Endpoints

### Community 93 - "1. Video Management"
Cohesion: 0.40
Nodes (5): 1.1 Video Source, 1.2 Video Processing Flow (Immediate, Async), 1.3 Video Chunking with Sentence Snap, 1.4 Storage Structure, 1. Video Management

### Community 94 - "4. Learning Modes"
Cohesion: 0.40
Nodes (5): 4.1 Reading Mode, 4.2 Listening Mode, 4.3 Speaking Mode (Shadowing), 4.4 Resume Functionality, 4. Learning Modes

### Community 95 - "Technical Constraints"
Cohesion: 0.40
Nodes (5): LLM Constraints, Performance Constraints, Storage Constraints, Technical Constraints, Video Constraints

### Community 96 - "Settings"
Cohesion: 0.50
Nodes (4): Config, Application settings loaded from environment variables., Settings, BaseSettings

### Community 97 - "3. Video Courses"
Cohesion: 0.50
Nodes (4): 3.1 Course Creation, 3.2 Data Model, 3.3 Course Processing, 3. Video Courses

### Community 98 - "6. LLM Processing (Immediate, Async)"
Cohesion: 0.50
Nodes (4): 6.1 Processing Model, 6.2 LLM Operations, 6.3 Processing Flow, 6. LLM Processing (Immediate, Async)

### Community 99 - "Coding Standards"
Cohesion: 0.67
Nodes (3): Coding Standards, Python, TypeScript

### Community 104 - "Appendix"
Cohesion: 0.50
Nodes (4): A. FFmpeg Commands, Appendix, B. Docker Compose Services, C. Environment Variables

### Community 105 - "Video"
Cohesion: 0.14
Nodes (11): Video entity representing a YouTube video for learning., Video, Get video by YouTube URL., UUID, Process video through full pipeline with checkpoint-resume. Pipeline steps: 1.…, Retry processing from last checkpoint. Args: video_id: UUID of video to retry…, Update video status and optionally set error_message., Create chunks with Hybrid Dynamic sentence-snap. (+3 more)

### Community 122 - "vite.config.ts"
Cohesion: 0.40
Nodes (3): ref_node_url, vite, @vitejs/plugin-vue

### Community 143 - "env.py"
Cohesion: 0.18
Nodes (12): do_run_migrations(), Alembic environment configuration., Run migrations in 'offline' mode., Run actual migrations., Run migrations in async mode., Run migrations in 'online' mode., run_async_migrations(), run_migrations_offline() (+4 more)

### Community 144 - "AI Tutor Chat Streaming Spec"
Cohesion: 0.18
Nodes (10): 1. Problem, 2. Current Architecture, 3. Root Cause, 4. Target Behavior, 5. Fix, 6. Non-Goals, 7. Verification, AI Tutor Chat Streaming Spec (+2 more)

### Community 150 - "streamChat"
Cohesion: 0.40
Nodes (5): Chat Streaming Fix Implementation Plan, Global Constraints, Self-Review, Task 1: Mutate the assistant message through the reactive proxy, streamChat()

## Knowledge Gaps
- **604 isolated node(s):** `Config`, `english-learning-backend`, `build_img.sh script`, `name`, `private` (+599 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1150 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Core Requirements` connect `Core Requirements` to `3. Video Courses`, `6. LLM Processing (Immediate, Async)`, `English Speaking Learning App - Technical Specification`, `7. API Endpoints`, `1. Video Management`, `4. Learning Modes`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Why does `6.2 LLM Operations` connect `6. LLM Processing (Immediate, Async)` to `LLMService`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `6. LLM Processing (Immediate, Async)` connect `6. LLM Processing (Immediate, Async)` to `Core Requirements`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `VideoService` (e.g. with `Implemented Services` and `create_video_from_youtube()`) actually correct?**
  _`VideoService` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `VideoRepository` (e.g. with `Video` and `BaseRepository`) actually correct?**
  _`VideoRepository` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Base` (e.g. with `_ensure_database()` and `init_db()`) actually correct?**
  _`Base` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Video` (e.g. with `create_video_from_youtube()` and `VideoRepository`) actually correct?**
  _`Video` has 3 INFERRED edges - model-reasoned connections that need verification._