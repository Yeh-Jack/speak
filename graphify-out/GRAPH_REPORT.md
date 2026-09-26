# Graph Report - speak  (2026-09-26)

## Corpus Check
- 150 files · ~79,398 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .example 2, .toml 1)

## Summary
- 1906 nodes · 2918 edges · 132 communities (104 shown, 28 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 107 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ca2ec288`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Base
- test_video_service.py
- DownloadService
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
- gpu_utils.py
- compilerOptions
- TranscriptionError
- Video Processing Skill
- DashboardView.vue
- schemas/video.py
- English Speaking Learning App - Project Presentation
- English Speaking Learning App - Project Presentation
- AGENTS.md
- schemas/__init__.py
- Backend Documentation
- VideoService
- .generate_study_plan
- get_log_level
- API Endpoints
- endpoints/chat.py
- is_verbose
- video.service.ts
- LLM Task Skill
- endpoints/vocabulary.py
- useI18n.ts
- ProgressRepository
- MarkdownText.vue
- asyncio
- asyncio
- Study Statistics Implementation Plan
- Exam System Skill
- main.py
- UUID
- SpeakingService
- StudyProgress
- TestModuleLevelConstants
- TestSettings
- StudyPlanDisplay.vue
- devDependencies
- dependencies
- endpoints/speaking.py
- .get_with_chunks
- _get_handlers
- .delete_by_video_id
- SQLite3 Migration Implementation Plan
- TranscriptRepository
- TestCalculateSimilarity
- design-specs.md
- Transcription Skill
- Phase 2: Video Processing Pipeline Implementation Plan
- English Speaking Learning App
- setup_logging
- package.json
- VocabularyCard.vue
- Guidelines
- asyncio
- sqlalchemy
- test_speaking_service.py
- schemas/transcript.py
- TestGenerateFeedback
- English Learning Frontend
- compilerOptions
- English Speaking Learning App - Technical Specification
- session.py
- ChatService
- English Speaking Learning App - Agent Instructions
- TestCreateChunksEdgeCases
- logging.py
- TestSettingsEnvOverride
- Implementation Phases
- ChunkingConfig
- api.ts
- Core Requirements
- TestGetLogger
- TestLogLevel
- scripts
- pull_request_template.md
- BaseButton.vue
- ChunkingService
- VideoChunk
- TestVideoChunk
- 7. API Endpoints
- 1. Video Management
- 4. Learning Modes
- Technical Constraints
- Settings
- 3. Video Courses
- 6. LLM Processing (Immediate, Async)
- Coding Standards
- .__init__
- .__init__
- .__init__
- .__init__
- Appendix
- .get_by_youtube_url
- build_img.sh
- db/__init__.py
- app/__init__.py
- vite.config.ts
- tests/unit/__init__.py
- english-learning-backend
- env.py
- AI Tutor Chat Streaming Spec
- frontend_config
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
- `Implemented Services` --references--> `ChunkingService`  [INFERRED]
  ARCHITECTURE.md → backend/app/services/chunking_service.py
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

## Communities (132 total, 28 thin omitted)

### Community 0 - "Base"
Cohesion: 0.14
Nodes (25): AsyncAttrs, Base, SQLAlchemy base class for all models., Base class for all SQLAlchemy models., Mixin to add created_at and updated_at timestamps., TimestampMixin, Chunk of a video with sentence-snapped boundaries., VideoChunk (+17 more)

### Community 1 - "test_video_service.py"
Cohesion: 0.09
Nodes (21): ProcessingTimings, Elapsed time metrics for each processing stage., MockVideo, asyncio, Tests for VideoService., process_video should raise VideoProcessingError if video not found., Mock Video model for testing., process_video should set error_message on failure. (+13 more)

### Community 2 - "DownloadService"
Cohesion: 0.11
Nodes (14): Implemented Services, DownloadService, Path, Get video metadata without downloading. Args: youtube_url: Full YouTube URL…, Synchronous info extraction using yt-dlp. Note on YouTube subtitles: -…, Service for downloading YouTube videos using yt-dlp., Download video and subtitles from YouTube URL. Args: youtube_url: Full YouTube…, Synchronous download using yt-dlp. Downloads video and both author-uploaded and… (+6 more)

### Community 3 - "test_chunking_service.py"
Cohesion: 0.18
Nodes (11): chunking_service(), fixture, ChunkingService should have default search window of 30s., _ends_with_sentence should detect sentence endings., Should find sentence boundary within ±30s window., Should return target time if no boundary in window., sample_transcript(), test_chunking_service_initialization() (+3 more)

### Community 4 - "Design Specifications & Coding Guidelines"
Cohesion: 0.04
Nodes (45): 1. Input Validation, 1. Repository Pattern (Backend), 1. Strict Type Safety, 1. Type Hints (Mandatory), 2. Async/Await (ALL I/O Operations), 2. Service Layer Pattern (Async), 2. Vue 3.5 Best Practices, 3. CORS Configuration (+37 more)

### Community 5 - "video_service.py"
Cohesion: 0.07
Nodes (41): asyncio, get_logger(), Get a logger instance with the standard format. Args: name: Logger name…, Chat service for AI tutor functionality., Hybrid Dynamic chunking service with ±30s sentence boundary snap., YouTube video download service using yt-dlp., ChunkingError, DownloadError (+33 more)

### Community 6 - "English Speaking Learning App - System Architecture"
Cohesion: 0.05
Nodes (40): 1. Download Service, 1. Repository Pattern, 2. Chunking Service (Hybrid Dynamic), 2. Service Layer Pattern, 3. State Machine Pattern, 3. Transcription Service, 4. Video Service (Orchestrator), API Reference (+32 more)

### Community 7 - "videos.py"
Cohesion: 0.09
Nodes (47): delete_video(), get_chunk_audio(), get_progress(), get_study_plan_by_chunk(), get_video(), get_video_chunks(), get_video_study_plans(), get_video_transcript() (+39 more)

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

### Community 13 - "gpu_utils.py"
Cohesion: 0.11
Nodes (21): calculate_gpu_layers(), detect_all_gpus(), get_best_gpu(), get_gpu_summary(), GPUBackend, GPUInfo, GPUManager, GPUVendor (+13 more)

### Community 14 - "compilerOptions"
Cohesion: 0.09
Nodes (21): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleResolution (+13 more)

### Community 15 - "TranscriptionError"
Cohesion: 0.06
Nodes (38): Raised when transcription fails., TranscriptionError, Path, Transcription service: Dual transcript system with YouTube subtitles + Whisper., Extract speaker label if present (e.g., 'John: Hello')., Service for transcribing audio using faster-whisper., Initialize Whisper model. Model sizes: tiny, base, small, medium, large-v3 CPU-…, Lazy load the Whisper model. (+30 more)

### Community 16 - "Video Processing Skill"
Cohesion: 0.07
Nodes (26): API Endpoints, Character-Based Chunking, Character Chunking Service, Chunking configuration, Chunking Modes, Chunking settings, Database Schema, Description (+18 more)

### Community 17 - "DashboardView.vue"
Cohesion: 0.08
Nodes (27): startRecording(), useAuth(), t(), videoService, chunkDuration, chunkDurationOptions, closeAddModal(), createVideoFromYouTube() (+19 more)

### Community 18 - "schemas/video.py"
Cohesion: 0.08
Nodes (33): create_video_from_youtube(), get_video_info(), post, Get metadata of a video from YouTube URL without DB operations., Create video from YouTube URL and process through full pipeline. This endpoint:…, ProcessingTimings, BaseModel, Enum (+25 more)

### Community 19 - "English Speaking Learning App - Project Presentation"
Cohesion: 0.08
Nodes (25): English Speaking Learning App - Project Presentation, 問題 1：CUDA 支援與 Python 版本, 問題 2：瀏覽器音訊錄製, 問題 3：繁體中文支援, 如何建構 AI 賦能的 Python 應用程式, 投影片 10：問題與解決方案, 投影片 11：問題與解決方案, 投影片 12：問題與解決方案 (+17 more)

### Community 20 - "English Speaking Learning App - Project Presentation"
Cohesion: 0.08
Nodes (25): 1: CUDA Support & Python Version (CUDA 支援與 Python 版本), Checkpoint-Resume State Machine, English Speaking Learning App - Project Presentation, How to Build an AI-Enabled Python Application, Key Design Decisions, Problem 2: Audio Recording from Browser (瀏覽器音頻錄製), Problem 3: Traditional Chinese Support (繁體中文支援), Slide 10: Problems Encountered & Solutions (問題與解決方案) (+17 more)

### Community 21 - "AGENTS.md"
Cohesion: 0.08
Nodes (24): Add a dev dependency, Add a new dependency, API waits for full processing before returning, Apply migrations, Create migration, Create virtual environment and install dependencies, Downgrade, Generate study plan with highest priority transcript (user > whisper > youtube) (+16 more)

### Community 22 - "schemas/__init__.py"
Cohesion: 0.12
Nodes (22): Pydantic schemas for the English Learning application., BaseModel, Study Progress schemas., Base study progress schema., Schema for creating study progress., Schema for updating study progress., Study progress response schema., Resume information for a video. (+14 more)

### Community 23 - "Backend Documentation"
Cohesion: 0.08
Nodes (24): API Endpoints, Backend Documentation, Configuration, Database Models, Dependencies, Directory Structure, Environment Variables, Fixed (not configurable) (+16 more)

### Community 24 - "VideoService"
Cohesion: 0.11
Nodes (16): UUID, Process video through full pipeline with checkpoint-resume. Pipeline steps: 1.…, Retry processing from last checkpoint. Args: video_id: UUID of video to retry…, Update video status and optionally set error_message., Create chunks with Hybrid Dynamic sentence-snap., Transcribe video using triple transcript system. Always runs Whisper. Tries to…, Extract audio for each chunk in mp3 format. Args: video: Video model with…, Extract a specific audio chunk from video. Args: video_path: Path to video file… (+8 more)

### Community 25 - ".generate_study_plan"
Cohesion: 0.13
Nodes (8): LLM Operations, Any, Format transcript segments into a text string., Generate LLM response using chat completion., Extract and parse JSON from LLM response., Attempt to fix JSON truncated mid-string. When LLM output is cut off mid-string…, Validate and fill in missing fields with defaults., Generate a study plan from transcript using LLM. Args: transcript: Transcript…

### Community 27 - "get_log_level"
Cohesion: 0.13
Nodes (13): get_log_level(), Get log level from environment variable or provided value. Args: env_value: Log…, Tests for get_log_level function., Should return logging.DEBUG for 'DEBUG' input., Should return logging.INFO for 'INFO' input., Should return logging.WARNING for 'WARNING' input., Should return logging.ERROR for 'ERROR' input., Should return logging.CRITICAL for 'CRITICAL' input. (+5 more)

### Community 28 - "API Endpoints"
Cohesion: 0.09
Nodes (21): API Documentation, API Endpoints, Chat (`/api/v1/chat`), Chunks & Audio, Data Storage, Development, Docker, English Learning Backend (+13 more)

### Community 29 - "endpoints/chat.py"
Cohesion: 0.08
Nodes (26): get_db(), AsyncSession, Dependencies for API endpoints., Get database session for dependency injection. Commits on success. Endpoints…, Chat endpoints for AI tutor functionality., get_gpu_status(), get_llm_health(), get (+18 more)

### Community 30 - "is_verbose"
Cohesion: 0.17
Nodes (10): is_verbose(), Check if verbose mode is enabled via environment variable., Tests for is_verbose function., Should return True for 'true'., Should return True for '1'., Should return True for 'yes'., Should return False for 'false'., Should return False for 'no'. (+2 more)

### Community 31 - "video.service.ts"
Cohesion: 0.15
Nodes (16): ChatMessage, StreamChatOptions, StudyPlanResponse, TranscriptResponse, VideoResponse, useVideoStore, GrammarItem, StudyObjective (+8 more)

### Community 32 - "LLM Task Skill"
Cohesion: 0.12
Nodes (16): API Endpoints, Architecture, Chat with Teacher, Dependencies, Description, Environment Variables, GPU Auto-Detection, Guidelines (+8 more)

### Community 33 - "endpoints/vocabulary.py"
Cohesion: 0.06
Nodes (44): migrate_vocabulary(), AsyncSession, post, Migrate vocabulary items from study_plans.vocabulary JSON to vocabularies…, FavoriteListResponse, FavoriteWord, get_favorite_vocabulary(), get_reviewed_vocabulary() (+36 more)

### Community 34 - "useI18n.ts"
Cohesion: 0.11
Nodes (18): { t }, videoStore, languageStore, isLearningPage, languageStore, route, { t }, useI18n() (+10 more)

### Community 35 - "ProgressRepository"
Cohesion: 0.22
Nodes (7): ProgressRepository, AsyncSession, UUID, Repository for StudyProgress model., Get progress for a specific video chunk., Get all progress for a video., Get list of completed chunk indices for a video.

### Community 36 - "MarkdownText.vue"
Cohesion: 0.31
Nodes (6): props, rendered, renderMarkdown(), dompurify, marked, vitest

### Community 37 - "asyncio"
Cohesion: 0.18
Nodes (9): asyncio, create_chunks should use ideal chunks when transcript is empty., _create_ideal_chunks should create correct chunk count., Should create chunks with Hybrid Dynamic sentence-snap., Chunk duration should be user-adjustable., Should snap to sentence when it's within ±30s but not at ideal boundary., test_create_chunks_hybrid_dynamic(), test_create_chunks_respects_chunk_duration() (+1 more)

### Community 38 - "asyncio"
Cohesion: 0.13
Nodes (12): asyncio, Tests for save_recording method., save_recording should create file with audio data., save_recording should create parent directories if needed., Tests for extract_audio_segment method., extract_audio_segment should raise ValueError on FFmpeg failure., extract_audio_segment should use custom output path if provided., Tests for compare_recordings method. (+4 more)

### Community 39 - "Study Statistics Implementation Plan"
Cohesion: 0.12
Nodes (16): Chart Types:, File Structure Overview, Key Interactive Features Implemented:, Study Statistics Implementation Plan, Summary of Implementation, Task 10: Create Statistics Chart Component, Task 11: Final Integration and Testing, Task 1: Add pyecharts Dependency (+8 more)

### Community 40 - "Exam System Skill"
Cohesion: 0.12
Nodes (15): API Endpoints, Dependencies, Description, Environment Variables, Exam Generation with LLM, Exam Submission and Scoring, Exam System Skill, Guidelines (+7 more)

### Community 41 - "main.py"
Cohesion: 0.22
Nodes (10): _ensure_data_directories(), _ensure_database(), lifespan(), FastAPI application entry point., Ensure all data storage directories exist., Ensure database exists and has tables created via SQLAlchemy., Application lifespan context manager for startup/shutdown events., contextlib (+2 more)

### Community 42 - "UUID"
Cohesion: 0.18
Nodes (6): UUID, Get study plan for a video (overall plan, chunk_index is null)., Get study plan for a specific chunk., Get all study plans for a video (including chunk-specific)., Create a study plan for a video and save vocabulary items to database., Save vocabulary items to the vocabulary table.

### Community 43 - "SpeakingService"
Cohesion: 0.18
Nodes (9): Path, Calculate simple text similarity between two strings. Uses word overlap ratio…, Compare user's recording with original using Whisper. Args:…, Service for speaking practice with audio comparison., Generate feedback based on comparison. Args: original_text: Original transcript…, Save user's recording to disk. Args: audio_data: Raw audio bytes (WebM/Opus)…, Extract audio segment from video for a specific time range. Args: video_path:…, Transcribe audio file using Whisper. Args: audio_path: Path to audio file… (+1 more)

### Community 44 - "StudyProgress"
Cohesion: 0.12
Nodes (12): Progress tracking for video chunks., StudyProgress, AsyncSession, Statistics service for calculating user learning metrics., Count completed study chunks (proxy for sentences practiced)., Calculate total minutes studied today., Service for calculating dashboard statistics., Calculate dashboard statistics from study progress. Args: daily_goal_minutes:… (+4 more)

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

### Community 50 - "endpoints/speaking.py"
Cohesion: 0.21
Nodes (14): compare_recording(), get_audio_segment(), get_speaking_service(), get_video_segments(), AsyncSession, get, post, UUID (+6 more)

### Community 51 - ".get_with_chunks"
Cohesion: 0.40
Nodes (3): UUID, Get video with its chunks., Update video status and optionally error_message.

### Community 52 - "_get_handlers"
Cohesion: 0.25
Nodes (7): _get_handlers(), Get logging handlers based on environment. Args: level: The logging level…, Tests for _get_handlers function., Should always include StreamHandler for stdout., Should add file handler when LOG_DIR is set., TestGetHandlers, Handler

### Community 53 - ".delete_by_video_id"
Cohesion: 0.29
Nodes (4): UUID, Get all chunks for a video., Get a specific chunk by video ID and index., Delete all chunks for a video and return count.

### Community 54 - "SQLite3 Migration Implementation Plan"
Cohesion: 0.13
Nodes (14): File Structure Overview, Spec Coverage Check, SQLite3 Migration Implementation Plan, Task 10: Update Environment Example File, Task 11: Test Database Setup, Task 1: Update Configuration for SQLite3, Task 2: Update Database Session for SQLite3, Task 3: Update Base Model for SQLite UUID Compatibility (+6 more)

### Community 56 - "TranscriptRepository"
Cohesion: 0.13
Nodes (12): chat(), AsyncSession, post, Streaming chat endpoint for AI tutor (SSE). Streams tokens as they are…, AsyncSession, UUID, Repository for Transcript model., Get a single transcript for a video (first one found). (+4 more)

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

### Community 62 - "setup_logging"
Cohesion: 0.21
Nodes (8): Configure application-wide logging. Args: log_level: Log level string (default:…, setup_logging(), Should use DEBUG_FORMAT when verbose is True., Should use DEFAULT_FORMAT when verbose is False., Should use explicit log_level over env var., Should set httpx and urllib3 to WARNING., Tests for setup_logging function., TestSetupLogging

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
Cohesion: 0.16
Nodes (10): asyncio, get_video_info should return video metadata without downloading., get_video_info should return defaults if extraction fails., Tests for download_video method., download_video should return video info dict on success., download_video should raise DownloadError if file doesn't exist after download., download_video should raise DownloadError when sync download fails., Tests for get_video_info method. (+2 more)

### Community 67 - "sqlalchemy"
Cohesion: 0.12
Nodes (19): ABC, Migration endpoint to populate vocabularies table from existing study plans., BaseRepository, Any, AsyncSession, Base repository with common CRUD operations., Base repository with CRUD operations., Get all entities with pagination. (+11 more)

### Community 68 - "test_speaking_service.py"
Cohesion: 0.17
Nodes (9): Speaking practice service for character impersonation mode., fixture, Tests for SpeakingService., Create SpeakingService with temp directory., Tests for SpeakingService initialization., SpeakingService should create recordings directory., speaking_service(), TestSpeakingServiceInitialization (+1 more)

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

### Community 74 - "session.py"
Cohesion: 0.15
Nodes (11): get_db(), init_sqlite_pragmas(), log_query(), Database session management., Initialize SQLite pragmas for better performance and foreign key support., Get database session for dependency injection., Log SQL queries at debug level before execution., init_db() (+3 more)

### Community 75 - "ChatService"
Cohesion: 0.20
Nodes (5): ChatService, Cleanup model resources., Service for chat-based LLM interactions (AI tutor)., Lazy load the llama-cpp-python model., Generate a streaming chat response. Args: messages: List of message dicts with…

### Community 76 - "English Speaking Learning App - Agent Instructions"
Cohesion: 0.14
Nodes (14): Agent Skills Available, Architecture, Backend, Directory Structure, English Speaking Learning App - Agent Instructions, Frontend, Key Design Patterns, LLM Configuration (+6 more)

### Community 77 - "TestCreateChunksEdgeCases"
Cohesion: 0.17
Nodes (7): Tests for edge cases in create_chunks., create_chunks should raise ChunkingError for invalid duration., create_chunks should raise ChunkingError for zero duration., Last chunk should be shorter if video doesn't divide evenly., _find_sentence_boundary should find boundary for last chunk., _find_sentence_boundary should not search before chunk_start., TestCreateChunksEdgeCases

### Community 78 - "logging.py"
Cohesion: 0.08
Nodes (26): Application configuration using Pydantic settings., Core module for the English Learning application., LogLevel, Enum, str, Centralized logging configuration for the application., Log level enumeration matching standard logging levels., Tests for config module. (+18 more)

### Community 79 - "TestSettingsEnvOverride"
Cohesion: 0.25
Nodes (5): Tests for Settings environment variable override., LLM_GPU_LAYERS should be overridable via env var., CHUNK_DURATION should be overridable via env var., ENVIRONMENT should be overridable via env var., TestSettingsEnvOverride

### Community 80 - "Implementation Phases"
Cohesion: 0.25
Nodes (8): Implementation Phases, Phase 1: Foundation (1 week), Phase 2: Video Pipeline (1 week), Phase 3: Transcription (1 week), Phase 4: LLM Integration (1 week), Phase 5: Learning Features (1 week), Phase 6: Speaking Practice (1 week), Phase 7: Statistics & Polish (1 week)

### Community 81 - "ChunkingConfig"
Cohesion: 0.28
Nodes (6): ChunkingConfig, Configuration for Hybrid Dynamic chunking., Tests for ChunkingConfig dataclass., ChunkingConfig should have correct default values., ChunkingConfig should accept custom values., TestChunkingConfig

### Community 82 - "api.ts"
Cohesion: 0.29
Nodes (5): api, Window, DashboardStats, statsService, axios

### Community 83 - "Core Requirements"
Cohesion: 0.29
Nodes (7): 2.1 Subtitle/Transcript Strategy, 2. Subtitle/Transcript Processing, 5.1 LLM-Generated Study Plan, 5.2 Study Plan Structure, 5.3 Vocabulary Extraction, 5. Study Plan Generation, Core Requirements

### Community 84 - "TestGetLogger"
Cohesion: 0.33
Nodes (4): Tests for get_logger function., Should return a logger instance., Should set the logger name correctly., TestGetLogger

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
Cohesion: 0.29
Nodes (5): ChunkingService, Hybrid Dynamic chunking with sentence-aware boundaries. Algorithm: 1. Calculate…, Check if text ends with sentence-ending punctuation., Find nearest sentence boundary within ±30s of target_time. Args: target_time:…, create_chunks should use custom ChunkingConfig.

### Community 90 - "VideoChunk"
Cohesion: 0.40
Nodes (4): Create ideal chunks without sentence snap (fallback when no transcript)., A virtual video chunk with sentence-snapped timestamps., Create chunks with Hybrid Dynamic sentence-snap. Args: video_duration: Total…, VideoChunk

### Community 91 - "TestVideoChunk"
Cohesion: 0.33
Nodes (4): Tests for VideoChunk dataclass., VideoChunk should store chunk data correctly., VideoChunk duration should be end - start., TestVideoChunk

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

### Community 122 - "vite.config.ts"
Cohesion: 0.40
Nodes (3): ref_node_url, vite, @vitejs/plugin-vue

### Community 143 - "env.py"
Cohesion: 0.18
Nodes (12): do_run_migrations(), Alembic environment configuration., Run migrations in 'offline' mode., Run actual migrations., Run migrations in async mode., Run migrations in 'online' mode., run_async_migrations(), run_migrations_offline() (+4 more)

### Community 144 - "AI Tutor Chat Streaming Spec"
Cohesion: 0.18
Nodes (10): 1. Problem, 2. Current Architecture, 3. Root Cause, 4. Target Behavior, 5. Fix, 6. Non-Goals, 7. Verification, AI Tutor Chat Streaming Spec (+2 more)

### Community 147 - "frontend_config"
Cohesion: 0.29
Nodes (8): frontend_config(), health_check(), get, Return runtime config for frontend., Serve frontend index.html for SPA routes, or static files if they exist., Health check endpoint., serve_spa_or_static(), Request

### Community 150 - "streamChat"
Cohesion: 0.40
Nodes (5): Chat Streaming Fix Implementation Plan, Global Constraints, Self-Review, Task 1: Mutate the assistant message through the reactive proxy, streamChat()

## Knowledge Gaps
- **604 isolated node(s):** `Config`, `english-learning-backend`, `build_img.sh script`, `name`, `private` (+599 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1152 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Core Requirements` connect `Core Requirements` to `3. Video Courses`, `6. LLM Processing (Immediate, Async)`, `English Speaking Learning App - Technical Specification`, `7. API Endpoints`, `1. Video Management`, `4. Learning Modes`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Why does `6.2 LLM Operations` connect `6. LLM Processing (Immediate, Async)` to `.generate_study_plan`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Why does `6. LLM Processing (Immediate, Async)` connect `6. LLM Processing (Immediate, Async)` to `Core Requirements`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `VideoService` (e.g. with `Implemented Services` and `create_video_from_youtube()`) actually correct?**
  _`VideoService` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `VideoRepository` (e.g. with `Video` and `BaseRepository`) actually correct?**
  _`VideoRepository` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Base` (e.g. with `_ensure_database()` and `init_db()`) actually correct?**
  _`Base` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Video` (e.g. with `create_video_from_youtube()` and `VideoRepository`) actually correct?**
  _`Video` has 3 INFERRED edges - model-reasoned connections that need verification._