# Graph Report - speak  (2026-08-05)

## Corpus Check
- 149 files · ~79,307 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1949 nodes · 2797 edges · 141 communities (122 shown, 19 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 116 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5b84e543`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Base
- VideoService
- DownloadService
- ChunkingService
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
- TranscriptionService
- Video Processing Skill
- DashboardView.vue
- schemas/video.py
- English Speaking Learning App - Project Presentation
- English Speaking Learning App - Project Presentation
- AGENTS.md
- schemas/__init__.py
- Backend Documentation
- What You Must Do When Invoked
- LLMService
- get_log_level
- API Endpoints
- endpoints/stats.py
- patch
- video.service.ts
- LLM Task Skill
- endpoints/vocabulary.py
- useI18n.ts
- repositories/__init__.py
- MarkdownText.vue
- asyncio
- asyncio
- Study Statistics Implementation Plan
- Exam System Skill
- main.py
- StudyPlanRepository
- SpeakingService
- StatsService
- TestModuleLevelConstants
- TestSettings
- StudyPlanDisplay.vue
- devDependencies
- dependencies
- endpoints/speaking.py
- .get_with_chunks
- logging.py
- ChunkRepository
- SQLite3 Migration Implementation Plan
- TranscriptRepository
- TestCalculateSimilarity
- design-specs.md
- Transcription Skill
- Phase 2: Video Processing Pipeline Implementation Plan
- English Speaking Learning App
- setup_logging
- asyncio
- VocabularyCard.vue
- Guidelines
- endpoints/chat.py
- BaseRepository
- test_speaking_service.py
- schemas/transcript.py
- TestGenerateFeedback
- English Learning Frontend
- compilerOptions
- English Speaking Learning App - Technical Specification
- session.py
- ChatService
- SpeakingPracticeRecord
- graphify reference: extra exports and benchmark
- conftest.py
- TestSettingsEnvOverride
- Implementation Phases
- main.ts
- api.ts
- Core Requirements
- TestGetLogger
- TestLogLevel
- package.json
- pull_request_template.md
- graphify reference: query, path, explain
- Success Criteria
- get_gpu_status
- get_dashboard_stats
- @types/node
- @typescript-eslint/eslint-plugin
- Technical Constraints
- Settings
- test_config.py
- opencode.json
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- Appendix
- stats.store.ts
- graphify.js
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- db/__init__.py
- app/__init__.py
- create_video_from_youtube
- .test_settings_has_default_model
- .test_settings_chunk_duration
- .test_settings_environment
- eslint
- @typescript-eslint/parser
- extraction-spec.md
- tests/unit/__init__.py
- english-learning-backend
- env.py
- AI Tutor Chat Streaming Spec
- frontend_config
- Chat Streaming Fix Implementation Plan
- Vocabulary
- init_db.py
- TestSpeakingServiceInitialization
- .dict

## God Nodes (most connected - your core abstractions)
1. `VideoService` - 40 edges
2. `VideoRepository` - 28 edges
3. `ProcessingTimings` - 25 edges
4. `Base` - 23 edges
5. `DownloadService` - 22 edges
6. `VideoProcessingError` - 22 edges
7. `TranscriptRepository` - 20 edges
8. `SpeakingService` - 20 edges
9. `StudyPlanRepository` - 19 edges
10. `ChunkingService` - 19 edges

## Surprising Connections (you probably didn't know these)
- `TestGetLogger` --uses--> `LogLevel`  [INFERRED]
  backend/tests/unit/test_logging.py → backend/app/core/logging.py
- `TestGetLogLevel` --uses--> `LogLevel`  [INFERRED]
  backend/tests/unit/test_logging.py → backend/app/core/logging.py
- `TestIsVerbose` --uses--> `LogLevel`  [INFERRED]
  backend/tests/unit/test_logging.py → backend/app/core/logging.py
- `TestLogLevel` --uses--> `LogLevel`  [INFERRED]
  backend/tests/unit/test_logging.py → backend/app/core/logging.py
- `TestSetupLogging` --uses--> `LogLevel`  [INFERRED]
  backend/tests/unit/test_logging.py → backend/app/core/logging.py

## Import Cycles
- None detected.

## Communities (141 total, 19 thin omitted)

### Community 0 - "Base"
Cohesion: 0.16
Nodes (18): AsyncAttrs, Base, SQLAlchemy base class for all models., Base class for all SQLAlchemy models., Mixin to add created_at and updated_at timestamps., TimestampMixin, Chunk of a video with sentence-snapped boundaries., VideoChunk (+10 more)

### Community 1 - "VideoService"
Cohesion: 0.06
Nodes (45): Base exception for video processing errors with checkpoint info., VideoProcessingError, ProcessingTimings, Path, UUID, Video, VideoChunk, Process video through full pipeline with checkpoint-resume. Pipeline steps: 1.… (+37 more)

### Community 2 - "DownloadService"
Cohesion: 0.07
Nodes (24): DownloadService, Path, Get video metadata without downloading. Args: youtube_url: Full YouTube URL…, Synchronous info extraction using yt-dlp. Note on YouTube subtitles: -…, Service for downloading YouTube videos using yt-dlp., Download video and subtitles from YouTube URL. Args: youtube_url: Full YouTube…, Synchronous download using yt-dlp. Downloads video and both author-uploaded and…, download_service() (+16 more)

### Community 3 - "ChunkingService"
Cohesion: 0.06
Nodes (39): ChunkingConfig, ChunkingService, Hybrid Dynamic chunking service with ±30s sentence boundary snap., Configuration for Hybrid Dynamic chunking., Create ideal chunks without sentence snap (fallback when no transcript)., A virtual video chunk with sentence-snapped timestamps., Hybrid Dynamic chunking with sentence-aware boundaries. Algorithm: 1. Calculate…, Check if text ends with sentence-ending punctuation. (+31 more)

### Community 4 - "Design Specifications & Coding Guidelines"
Cohesion: 0.04
Nodes (45): 1. Input Validation, 1. Repository Pattern (Backend), 1. Strict Type Safety, 1. Type Hints (Mandatory), 2. Async/Await (ALL I/O Operations), 2. Service Layer Pattern (Async), 2. Vue 3.5 Best Practices, 3. CORS Configuration (+37 more)

### Community 5 - "video_service.py"
Cohesion: 0.09
Nodes (33): Application configuration using Pydantic settings., get_logger(), Get a logger instance with the standard format. Args: name: Logger name…, YouTube video download service using yt-dlp., DownloadError, Custom exceptions for video processing pipeline., Raised when video download fails., Raised when transcription fails. (+25 more)

### Community 6 - "English Speaking Learning App - System Architecture"
Cohesion: 0.05
Nodes (41): 1. Download Service, 1. Repository Pattern, 2. Chunking Service (Hybrid Dynamic), 2. Service Layer Pattern, 3. State Machine Pattern, 3. Transcription Service, 4. Video Service (Orchestrator), API Reference (+33 more)

### Community 7 - "videos.py"
Cohesion: 0.12
Nodes (32): delete_video(), get_chunk_audio(), get_progress(), get_video(), get_video_chunks(), get_video_transcript(), list_videos(), AsyncSession (+24 more)

### Community 8 - "ShadowingMode.vue"
Cohesion: 0.06
Nodes (37): allCompleted, audioLevel, beginRecording(), calculateSimilarity(), currentSentence, currentSentenceIndex, emit, fallbackToTTS() (+29 more)

### Community 9 - "VideoPlayerView.vue"
Cohesion: 0.06
Nodes (30): streamChat(), chatError, chatInput, chatMessages, chatMessagesContainer, currentTime, currentTranscriptSegments, error (+22 more)

### Community 10 - "VideoPlayer.vue"
Cohesion: 0.07
Nodes (31): buffered, containerRef, currentSubtitle, currentTime, duration, emit, formattedCurrentTime, formattedDuration (+23 more)

### Community 11 - "Study Progress Statistics Design Document"
Cohesion: 0.06
Nodes (35): API Caching, API Endpoints, Architecture, Backend, Chart 1: Study Timeline (Line/Area with DataZoom), Chart 2: Activity Heatmap (Calendar View), Chart 3: Weekly Comparison (Grouped Bar with Timeline), Chart 4: Video Progress (Horizontal Bar) (+27 more)

### Community 12 - "Frontend Documentation"
Cohesion: 0.06
Nodes (31): api (Axios instance), Components, Composables, DashboardView (`/`), Directory Structure, Environment Variables, Frontend Documentation, languageStore (+23 more)

### Community 13 - "gpu_utils.py"
Cohesion: 0.11
Nodes (21): calculate_gpu_layers(), detect_all_gpus(), get_best_gpu(), get_gpu_summary(), GPUBackend, GPUInfo, GPUManager, GPUVendor (+13 more)

### Community 14 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleResolution (+20 more)

### Community 15 - "TranscriptionService"
Cohesion: 0.10
Nodes (19): Path, Extract speaker label if present (e.g., 'John: Hello')., Service for transcribing audio using faster-whisper., Initialize Whisper model. Model sizes: tiny, base, small, medium, large-v3 CPU-…, Lazy load the Whisper model., Transcribe audio file with word-level timestamps. Args: audio_path: Path to…, Orchestrates dual transcription. 1. Always runs Whisper transcription 2. Also…, Parse subtitle file and return list of entries. Args: subtitle_path: Path to… (+11 more)

### Community 16 - "Video Processing Skill"
Cohesion: 0.07
Nodes (26): API Endpoints, Character-Based Chunking, Character Chunking Service, Chunking configuration, Chunking Modes, Chunking settings, Database Schema, Description (+18 more)

### Community 17 - "DashboardView.vue"
Cohesion: 0.09
Nodes (22): useAuth(), chunkDuration, chunkDurationOptions, closeAddModal(), createVideoFromYouTube(), dashboardStats, error, fetchDashboardStats() (+14 more)

### Community 18 - "schemas/video.py"
Cohesion: 0.12
Nodes (23): ProcessingTimings, BaseModel, Enum, str, Video and VideoChunk schemas., Elapsed time metrics for video processing stages., Video processing state machine states., Complete video response with all data. (+15 more)

### Community 19 - "English Speaking Learning App - Project Presentation"
Cohesion: 0.08
Nodes (25): English Speaking Learning App - Project Presentation, 問題 1：CUDA 支援與 Python 版本, 問題 2：瀏覽器音訊錄製, 問題 3：繁體中文支援, 如何建構 AI 賦能的 Python 應用程式, 投影片 10：問題與解決方案, 投影片 11：問題與解決方案, 投影片 12：問題與解決方案 (+17 more)

### Community 20 - "English Speaking Learning App - Project Presentation"
Cohesion: 0.08
Nodes (25): 1: CUDA Support & Python Version (CUDA 支援與 Python 版本), Checkpoint-Resume State Machine, English Speaking Learning App - Project Presentation, How to Build an AI-Enabled Python Application, Key Design Decisions, Problem 2: Audio Recording from Browser (瀏覽器音頻錄製), Problem 3: Traditional Chinese Support (繁體中文支援), Slide 10: Problems Encountered & Solutions (問題與解決方案) (+17 more)

### Community 21 - "AGENTS.md"
Cohesion: 0.05
Nodes (41): Add a dev dependency, Add a new dependency, Agent Skills Available, API waits for full processing before returning, Apply migrations, Architecture, Backend, Coding Standards (+33 more)

### Community 22 - "schemas/__init__.py"
Cohesion: 0.12
Nodes (22): Pydantic schemas for the English Learning application., BaseModel, Study Progress schemas., Base study progress schema., Schema for creating study progress., Schema for updating study progress., Study progress response schema., Resume information for a video. (+14 more)

### Community 23 - "Backend Documentation"
Cohesion: 0.08
Nodes (24): API Endpoints, Backend Documentation, Configuration, Database Models, Dependencies, Directory Structure, Environment Variables, Fixed (not configurable) (+16 more)

### Community 24 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 25 - "LLMService"
Cohesion: 0.09
Nodes (17): Chat service for AI tutor functionality., LLMService, Any, Path, Format transcript segments into a text string., Generate LLM response using chat completion., Stream LLM response token by token. Args: messages: List of message dicts with…, Extract and parse JSON from LLM response. (+9 more)

### Community 27 - "get_log_level"
Cohesion: 0.13
Nodes (13): get_log_level(), Get log level from environment variable or provided value. Args: env_value: Log…, Tests for get_log_level function., Should return logging.DEBUG for 'DEBUG' input., Should return logging.INFO for 'INFO' input., Should return logging.WARNING for 'WARNING' input., Should return logging.ERROR for 'ERROR' input., Should return logging.CRITICAL for 'CRITICAL' input. (+5 more)

### Community 28 - "API Endpoints"
Cohesion: 0.09
Nodes (21): API Documentation, API Endpoints, Chat (`/api/v1/chat`), Chunks & Audio, Data Storage, Development, Docker, English Learning Backend (+13 more)

### Community 29 - "endpoints/stats.py"
Cohesion: 0.24
Nodes (7): get_db(), AsyncSession, Dependencies for API endpoints., Get database session for dependency injection. Commits on success. Endpoints…, Statistics endpoints., DashboardStats, BaseModel

### Community 30 - "patch"
Cohesion: 0.16
Nodes (12): is_verbose(), Check if verbose mode is enabled via environment variable., Should add file handler when LOG_DIR is set., Tests for is_verbose function., Should return True for 'true'., Should return True for '1'., Should return True for 'yes'., Should return False for 'false'. (+4 more)

### Community 31 - "video.service.ts"
Cohesion: 0.15
Nodes (16): ChatMessage, StreamChatOptions, StudyPlanResponse, TranscriptResponse, VideoResponse, videoService, GrammarItem, StudyObjective (+8 more)

### Community 32 - "LLM Task Skill"
Cohesion: 0.11
Nodes (17): API Endpoints, Architecture, Chat with Teacher, Dependencies, Description, Environment Variables, GPU Auto-Detection, Guidelines (+9 more)

### Community 33 - "endpoints/vocabulary.py"
Cohesion: 0.06
Nodes (39): FavoriteListResponse, FavoriteWord, get_favorite_vocabulary(), get_reviewed_vocabulary(), get_vocabulary(), AsyncSession, BaseModel, get (+31 more)

### Community 34 - "useI18n.ts"
Cohesion: 0.18
Nodes (11): { t }, videoStore, languageStore, isLearningPage, languageStore, route, { t }, useI18n() (+3 more)

### Community 35 - "repositories/__init__.py"
Cohesion: 0.18
Nodes (9): Repository layer for database operations., ProgressRepository, AsyncSession, UUID, Repository for StudyProgress model., Get progress for a specific video chunk., Get all progress for a video., Get list of completed chunk indices for a video. (+1 more)

### Community 36 - "MarkdownText.vue"
Cohesion: 0.32
Nodes (5): dompurify, dompurify, props, rendered, renderMarkdown()

### Community 37 - "asyncio"
Cohesion: 0.12
Nodes (12): asyncio, create_chunks should raise ChunkingError for invalid duration., create_chunks should raise ChunkingError for zero duration., create_chunks should use ideal chunks when transcript is empty., _create_ideal_chunks should create correct chunk count., Last chunk should be shorter if video doesn't divide evenly., Should create chunks with Hybrid Dynamic sentence-snap., Chunk duration should be user-adjustable. (+4 more)

### Community 38 - "asyncio"
Cohesion: 0.18
Nodes (9): asyncio, Tests for save_recording method., save_recording should create file with audio data., save_recording should create parent directories if needed., Tests for extract_audio_segment method., extract_audio_segment should raise ValueError on FFmpeg failure., extract_audio_segment should use custom output path if provided., TestExtractAudioSegment (+1 more)

### Community 39 - "Study Statistics Implementation Plan"
Cohesion: 0.12
Nodes (16): Chart Types:, File Structure Overview, Key Interactive Features Implemented:, Study Statistics Implementation Plan, Summary of Implementation, Task 10: Create Statistics Chart Component, Task 11: Final Integration and Testing, Task 1: Add pyecharts Dependency (+8 more)

### Community 40 - "Exam System Skill"
Cohesion: 0.12
Nodes (15): API Endpoints, Dependencies, Description, Environment Variables, Exam Generation with LLM, Exam Submission and Scoring, Exam System Skill, Guidelines (+7 more)

### Community 41 - "main.py"
Cohesion: 0.22
Nodes (9): LLM status and health endpoints., _ensure_data_directories(), _ensure_database(), lifespan(), FastAPI application entry point., Ensure all data storage directories exist., Ensure database exists and has tables created via SQLAlchemy., Application lifespan context manager for startup/shutdown events. (+1 more)

### Community 42 - "StudyPlanRepository"
Cohesion: 0.18
Nodes (10): AsyncSession, UUID, Repository for StudyPlan model., Get study plan for a video (overall plan, chunk_index is null)., Get study plan for a specific chunk., Get all study plans for a video (including chunk-specific)., Create a study plan for a video and save vocabulary items to database., Save vocabulary items to the vocabulary table. (+2 more)

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
Cohesion: 0.12
Nodes (9): Tests for Settings class., Settings should have LLM_GPU_LAYERS., Settings should have LLM_CONTEXT_SIZE., Settings should have LLM_THREADS as positive int., Settings should have YOUTUBE_DOWNLOAD_QUALITY., Settings should have YOUTUBE_AUDIO_QUALITY., Settings should have DEBUG defaulting to True., Settings should have LOG_LEVEL defaulting to INFO. (+1 more)

### Community 47 - "StudyPlanDisplay.vue"
Cohesion: 0.08
Nodes (18): Props, sizeClasses, variantClasses, emit, onInput(), Props, activeTab, completedVocabulary (+10 more)

### Community 48 - "devDependencies"
Cohesion: 0.10
Nodes (21): autoprefixer, eslint-plugin-vue, devDependencies, autoprefixer, eslint-plugin-vue, jsdom, postcss, typescript (+13 more)

### Community 49 - "dependencies"
Cohesion: 0.12
Nodes (17): axios, clsx, dependencies, axios, clsx, marked, pinia, tailwindcss (+9 more)

### Community 50 - "endpoints/speaking.py"
Cohesion: 0.21
Nodes (14): compare_recording(), get_audio_segment(), get_speaking_service(), get_video_segments(), AsyncSession, get, post, UUID (+6 more)

### Community 51 - ".get_with_chunks"
Cohesion: 0.29
Nodes (5): UUID, Video, Get video with its chunks., Get video by YouTube URL., Update video status and optionally error_message.

### Community 52 - "logging.py"
Cohesion: 0.18
Nodes (12): _get_handlers(), LogLevel, Enum, str, Centralized logging configuration for the application., Log level enumeration matching standard logging levels., Get logging handlers based on environment. Args: level: The logging level…, Tests for logging module. (+4 more)

### Community 53 - "ChunkRepository"
Cohesion: 0.17
Nodes (9): ChunkRepository, AsyncSession, UUID, VideoChunk, Repository for VideoChunk model., Get all chunks for a video., Get a specific chunk by video ID and index., Delete all chunks for a video and return count. (+1 more)

### Community 54 - "SQLite3 Migration Implementation Plan"
Cohesion: 0.13
Nodes (14): File Structure Overview, Spec Coverage Check, SQLite3 Migration Implementation Plan, Task 10: Update Environment Example File, Task 11: Test Database Setup, Task 1: Update Configuration for SQLite3, Task 2: Update Database Session for SQLite3, Task 3: Update Base Model for SQLite UUID Compatibility (+6 more)

### Community 56 - "TranscriptRepository"
Cohesion: 0.21
Nodes (9): AsyncSession, UUID, Repository for Transcript model., Get a single transcript for a video (first one found)., Get all transcripts for a video., Get transcript by video ID and source., Create a transcript for a video., TranscriptRepository (+1 more)

### Community 57 - "TestCalculateSimilarity"
Cohesion: 0.14
Nodes (8): Tests for calculate_similarity method., Full word match should return 1.0., Partial word match should return proportion., No common words should return 0.0., Empty original text should return 0.0., Empty user text should return 0.0., Comparison should be case insensitive., TestCalculateSimilarity

### Community 58 - "design-specs.md"
Cohesion: 0.17
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

### Community 63 - "asyncio"
Cohesion: 0.40
Nodes (5): asyncio, TranscriptionService should try YouTube subtitles first., TranscriptionService should fallback to Whisper if YouTube fails., test_transcription_service_fallback_to_whisper(), test_transcription_service_youtube_strategy_first()

### Community 64 - "VocabularyCard.vue"
Cohesion: 0.20
Nodes (9): cardBorderClass, cefrColor, emit, isFlipped, isPlaying, playAudio(), Props, saveWord() (+1 more)

### Community 65 - "Guidelines"
Cohesion: 0.18
Nodes (10): Coding Patterns, Dependencies, Description, Example: Dependency Injection, Example: Service Layer, FastAPI Skill, Guidelines, Project Structure (+2 more)

### Community 66 - "endpoints/chat.py"
Cohesion: 0.19
Nodes (11): chat(), AsyncSession, post, Chat endpoints for AI tutor functionality., Streaming chat endpoint for AI tutor (SSE). Streams tokens as they are…, ChatMessage, BaseModel, Chat schemas for AI tutor interface. (+3 more)

### Community 67 - "BaseRepository"
Cohesion: 0.11
Nodes (15): ABC, Migration endpoint to populate vocabularies table from existing study plans., BaseRepository, Any, AsyncSession, Base repository with common CRUD operations., Base repository with CRUD operations., Get all entities with pagination. (+7 more)

### Community 68 - "test_speaking_service.py"
Cohesion: 0.22
Nodes (7): fixture, Tests for SpeakingService., Create SpeakingService with temp directory., Tests for compare_recordings method., compare_recordings should calculate similarity between transcriptions., speaking_service(), TestCompareRecordings

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
Cohesion: 0.20
Nodes (9): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, strict, include (+1 more)

### Community 73 - "English Speaking Learning App - Technical Specification"
Cohesion: 0.22
Nodes (7): Document History, English Speaking Learning App - Technical Specification, Language Requirements, LLM Configuration, Mandatory Traditional Chinese (繁體中文), Project Overview, Tech Stack

### Community 74 - "session.py"
Cohesion: 0.22
Nodes (8): get_db(), init_sqlite_pragmas(), log_query(), Database session management., Initialize SQLite pragmas for better performance and foreign key support., Get database session for dependency injection., Log SQL queries at debug level before execution., listens_for

### Community 75 - "ChatService"
Cohesion: 0.25
Nodes (5): ChatService, Cleanup model resources., Service for chat-based LLM interactions (AI tutor)., Lazy load the llama-cpp-python model., Generate a streaming chat response. Args: messages: List of message dicts with…

### Community 77 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 78 - "conftest.py"
Cohesion: 0.28
Nodes (8): event_loop(), fixture, Pytest configuration for unit tests., Create event loop for async tests., Create temporary path for tests., Sample transcript for testing chunking service., sample_transcript(), tmp_path()

### Community 79 - "TestSettingsEnvOverride"
Cohesion: 0.25
Nodes (5): Tests for Settings environment variable override., LLM_GPU_LAYERS should be overridable via env var., CHUNK_DURATION should be overridable via env var., ENVIRONMENT should be overridable via env var., TestSettingsEnvOverride

### Community 80 - "Implementation Phases"
Cohesion: 0.25
Nodes (8): Implementation Phases, Phase 1: Foundation (1 week), Phase 2: Video Pipeline (1 week), Phase 3: Transcription (1 week), Phase 4: LLM Integration (1 week), Phase 5: Learning Features (1 week), Phase 6: Speaking Practice (1 week), Phase 7: Statistics & Polish (1 week)

### Community 81 - "main.ts"
Cohesion: 0.38
Nodes (3): app, router, routes

### Community 82 - "api.ts"
Cohesion: 0.33
Nodes (4): api, Window, DashboardStats, statsService

### Community 83 - "Core Requirements"
Cohesion: 0.06
Nodes (31): 1.1 Video Source, 1.2 Video Processing Flow (Immediate, Async), 1.3 Video Chunking with Sentence Snap, 1.4 Storage Structure, 1. Video Management, 2.1 Subtitle/Transcript Strategy, 2. Subtitle/Transcript Processing, 3.1 Course Creation (+23 more)

### Community 84 - "TestGetLogger"
Cohesion: 0.33
Nodes (4): Tests for get_logger function., Should return a logger instance., Should set the logger name correctly., TestGetLogger

### Community 85 - "TestLogLevel"
Cohesion: 0.33
Nodes (4): Tests for LogLevel enum., LogLevel should have correct string values., LogLevel should be usable as string., TestLogLevel

### Community 86 - "package.json"
Cohesion: 0.18
Nodes (10): name, private, scripts, build, dev, lint, preview, test (+2 more)

### Community 87 - "pull_request_template.md"
Cohesion: 0.33
Nodes (5): Checklist:, Description, How Has This Been Tested?, Related issue: #, Type of change

### Community 88 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 89 - "Success Criteria"
Cohesion: 0.67
Nodes (3): Functional Requirements, Non-Functional Requirements, Success Criteria

### Community 90 - "get_gpu_status"
Cohesion: 0.40
Nodes (5): get_gpu_status(), get_llm_health(), get, Get GPU detection and configuration status for LLM inference. Returns…, Check LLM service health and GPU utilization. Forces LLM model initialization…

### Community 91 - "get_dashboard_stats"
Cohesion: 0.40
Nodes (5): get_dashboard_stats(), AsyncSession, get, Get dashboard statistics. Returns aggregated statistics about user learning…, DashboardStats

### Community 95 - "Technical Constraints"
Cohesion: 0.40
Nodes (5): LLM Constraints, Performance Constraints, Storage Constraints, Technical Constraints, Video Constraints

### Community 96 - "Settings"
Cohesion: 0.50
Nodes (4): Config, Application settings loaded from environment variables., Settings, BaseSettings

### Community 98 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 99 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 100 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 101 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 104 - "Appendix"
Cohesion: 0.50
Nodes (4): A. FFmpeg Commands, Appendix, B. Docker Compose Services, C. Environment Variables

### Community 112 - "create_video_from_youtube"
Cohesion: 0.13
Nodes (19): create_video_from_youtube(), get_study_plan_by_chunk(), get_video_info(), get_video_study_plans(), get, post, Get metadata of a video from YouTube URL without DB operations., Create video from YouTube URL and process through full pipeline. This endpoint:… (+11 more)

### Community 143 - "env.py"
Cohesion: 0.22
Nodes (10): do_run_migrations(), Alembic environment configuration., Run migrations in 'offline' mode., Run actual migrations., Run migrations in async mode., Run migrations in 'online' mode., run_async_migrations(), run_migrations_offline() (+2 more)

### Community 144 - "AI Tutor Chat Streaming Spec"
Cohesion: 0.18
Nodes (10): 1. Problem, 2. Current Architecture, 3. Root Cause, 4. Target Behavior, 5. Fix, 6. Non-Goals, 7. Verification, AI Tutor Chat Streaming Spec (+2 more)

### Community 147 - "frontend_config"
Cohesion: 0.29
Nodes (8): frontend_config(), health_check(), get, Return runtime config for frontend., Serve frontend index.html for SPA routes, or static files if they exist., Health check endpoint., serve_spa_or_static(), Request

### Community 150 - "Chat Streaming Fix Implementation Plan"
Cohesion: 0.40
Nodes (4): Chat Streaming Fix Implementation Plan, Global Constraints, Self-Review, Task 1: Mutate the assistant message through the reactive proxy

### Community 151 - "Vocabulary"
Cohesion: 0.17
Nodes (9): migrate_vocabulary(), AsyncSession, post, Migrate vocabulary items from study_plans.vocabulary JSON to vocabularies…, Progress tracking for video chunks., StudyProgress, Vocabulary item for spaced repetition learning., Vocabulary (+1 more)

### Community 152 - "init_db.py"
Cohesion: 0.50
Nodes (3): init_db(), Database initialization script for creating tables., Initialize database with all tables.

### Community 153 - "TestSpeakingServiceInitialization"
Cohesion: 0.50
Nodes (3): Tests for SpeakingService initialization., SpeakingService should create recordings directory., TestSpeakingServiceInitialization

## Knowledge Gaps
- **647 isolated node(s):** `Config`, `english-learning-backend`, `name`, `private`, `version` (+642 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `VideoService` connect `VideoService` to `Base`, `DownloadService`, `ChunkingService`, `video_service.py`, `videos.py`, `TranscriptionService`, `create_video_from_youtube`, `ChunkRepository`, `LLMService`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `SpeakingService` connect `SpeakingService` to `TestSpeakingServiceInitialization`, `test_speaking_service.py`, `video_service.py`, `asyncio`, `TestGenerateFeedback`, `endpoints/speaking.py`, `TestCalculateSimilarity`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `TestSettings` connect `TestSettings` to `test_config.py`, `.test_settings_chunk_duration`, `.test_settings_environment`, `.test_settings_has_default_model`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `VideoService` (e.g. with `VideoChunk` and `Video`) actually correct?**
  _`VideoService` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `ProcessingTimings` (e.g. with `VideoChunk` and `Video`) actually correct?**
  _`ProcessingTimings` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `Base` (e.g. with `VideoChunk` and `StudyProgress`) actually correct?**
  _`Base` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `DownloadService` (e.g. with `DownloadError` and `ProcessingTimings`) actually correct?**
  _`DownloadService` has 6 INFERRED edges - model-reasoned connections that need verification._