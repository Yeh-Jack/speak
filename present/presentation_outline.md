# English Speaking Learning App - Project Presentation

## 英文口說學習系統 - 專案簡報

---

## Slide 1: Cover Page (封面)

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║  AI-Powered English Learning Platform                         ║
║  利用大型語言模型打造個人化英語學習體驗                         ║
║                                                               ║
║  ─────────────────────────────────────────────────────────────║
║                                                               ║
║  Project Type: Full-Stack AI Application                     ║
║  Target: 個人英語學習者             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**Suggested Visual**: App logo, screenshot of video player with subtitles, AI chat interface

---

## Slide 2: Motivation & Problem Statement (動機與問題)

### Why This Project?
```
┌────────────────────────────────────────────────────────────────┐
│  製作動機                                             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ✅ 嘗試製作一個具有AI功能的應用程式                                 │
│  ✅ 利用 AI 作為個人化的英語老師                                  │
│  ✅ 從 YouTube 影片中學習（電影、TED、影集）                     │
│  ✅ AI 自動生成個人化學習計劃和詞彙表                             │
│  ✅ 口說練習功能                                             │
└────────────────────────────────────────────────────────────────┘
```

### How to Build an AI-Enabled Python Application
```
                     ┌─────────────────┐
                     │   User Submit   │
                     │  YouTube URL    │
                     └────────┬────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    AI Application Architecture                │
│                                                              │
│  1. Video Ingestion  ──►  2. AI Processing  ──►  3. Output │
│     (yt-dlp)              (Whisper + LLM)            (Study  │
│                                                        Plan) │
│                                                              │
│  Key Technologies:                                           │
│  • llama-cpp-python - Embedded LLM (no API costs)            │
│  • faster-whisper - Speech-to-text transcription             │
│  • async/await - Non-blocking processing                     │
└──────────────────────────────────────────────────────────────┘
```

**Speaker Notes**: 說明如何用 Python 建構 AI 應用程式，重點在於 llama-cpp-python 的使用讓我們不需要支付 API 費用，可以在本地端運行 LLM。

---

## Slide 3: Demo / Live Preview (展示環節)

```
┌────────────────────────────────────────────────────────────────┐
│                      LIVE DEMO                                 │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  1. Submit a YouTube URL                                       │
│     → https://www.youtube.com/watch?v=3OSkg0JudmU                 │
│                                                                │
│  2. i18n            │
│                                                                │
│  3. View generated content                                     │
│     □ Study plan with vocabulary                               │
│     □ Grammar points                                           │
│     □ Chunk summaries                                          │
│                                                                │
│  4. Interactive learning                                       │
│     □ Video player with synced subtitles                      │
│     □ Vocabulary highlighting                                   │
│     □ Listening mode (audio only)                              │
│                                                                │
│  5. Speaking practice                                         │
│     □ Record pronunciation                                      │
│     □ Compare with original                                    │
│     □ AI feedback                                              │
│                                                                │
│  6. Chat with AI teacher                                      │
│     □ Ask questions about vocabulary                           │
│     □ Get explanations in Traditional Chinese                  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Slide 4: Tech Stack Overview (技術堆疊)

```
┌─────────────────────────────────────────────────────────────────┐
│                        TECH STACK                               │
├───────────────┬─────────────────────────────────────────────────┤
│   FRONTEND          │  Vue 3.5 + TypeScript + Vite + pnpm      │
│                     │  Pinia (State Management)                 │
│                     │  Tailwind CSS                              │
├─────────────────────┼─────────────────────────────────────────┤
│   BACKEND           │  FastAPI (Python 3.12)                   │
│                     │  SQLAlchemy 2.0 (Async)                   │
│                     │  Pydantic v2                              │
├─────────────────────┼─────────────────────────────────────────┤
│   DATABASE          │  SQLite3 (WAL mode)                      │
│                     │  learning.db                              │
├─────────────────────┼─────────────────────────────────────────┤
│   AI/ML             │  llama-cpp-python                        │
│                     │  Qwen3.5-2B-Q4_K_M.gguf                    │
│                     │  faster-whisper (Whisper Tiny)            │
├─────────────────────┼─────────────────────────────────────────┤
│   VIDEO             │  FFmpeg + yt-dlp                         │
│                     │  WebM/MP4 (720p)                          │
├─────────────────────┼─────────────────────────────────────────┤
│   INFRASTRUCTURE    │  uv (Package Manager)                    │
│                     │  GPUtil (NVIDIA GPU detection)            │
└─────────────────────┴─────────────────────────────────────────┘
```

### Why These Choices?
```
┌────────────────────────────────────────────────────────────────┐
│  選擇 FastAPI 的原因                                            │
│  • 原生支援 async/await                                         │
│  • 自動 OpenAPI 文件                                           │
│  • Pydantic 整合                                                │
│                                                                │
│  選擇 llama-cpp-python 的原因                                   │
│  • 本地運行，無 API 費用                                        │
│  • 支援 NVIDIA CUDA 加速                                       │
│  • Q4_K_M 量化，2B 模型只需 ~1.5GB RAM                          │
└────────────────────────────────────────────────────────────────┘
```

---

## Slide 5: System Architecture (系統架構)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SYSTEM ARCHITECTURE                              │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                        Frontend (Vue 3.5)                          │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────────┐ │  │
│  │  │  Home   │  │  Video  │  │ Speaking│  │   Chat with AI      │ │  │
│  │  │  Page   │  │  Player │  │ Practice│  │     Teacher         │ │  │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └──────────┬──────────┘ │  │
│  └───────┼────────────┼────────────┼────────────────────┼─────────────┘  │
│          │            │            │                    │               │
│          └────────────┴────────────┴────────────────────┘               │
│                               │                                          │
│                          REST API │                                      │
│                               │                                          │
│  ┌────────────────────────────┴──────────────────────────────────────┐  │
│  │                    Backend (FastAPI) - Async I/O                    │  │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌─────────────────┐  │  │
│  │  │   Video   │  │    LLM    │  │ Transcript│  │     Study      │  │  │
│  │  │  Service  │  │  Service  │  │  Service  │  │    Service      │  │  │
│  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └────────┬────────┘  │  │
│  └────────┼──────────────┼──────────────┼─────────────────┼───────────┘  │
│           │              │              │                  │             │
│           ▼              ▼              ▼                  ▼             │
│  ┌────────────────┐         ┌────────────────────────────┐             │
│  │    SQLite3      │         │  llama-cpp-python + GPUtil  │             │
│  │  learning.db    │         │    (Qwen3.5-2B-Q4_K_M)      │             │
│  └────────────────┘         └────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions
```
┌────────────────────────────────────────────────────────────────┐
│  📌 No Authentication - Single-user application                │
│  📌 No Background Queue - All operations are async/await        │
│  📌 Single Fixed LLM Model - Qwen3.5-2B-Q4_K_M.gguf            │
│  📌 YouTube Only - No local file uploads                        │
└────────────────────────────────────────────────────────────────┘
```

---

## Slide 6: Processing Pipeline (處理流程)

```
POST /api/videos/youtube
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Download (yt-dlp)                                    │
│ ──────────────────────────────────────────────────────────── │
│ • Download video (MP4/WebM, 720p)                            │
│ • Download YouTube subtitles simultaneously                  │
│ • Extract video metadata (title, uploader, thumbnail)       │
│                                                             │
│ Checkpoint: pending → downloading → downloading_complete    │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Transcription (Whisper - Always Runs)               │
│ ──────────────────────────────────────────────────────────── │
│ • Extract audio using FFmpeg                                 │
│ • Run faster-whisper (Tiny model for speed)                 │
│ • Store: youtube_author, youtube_auto, whisper transcripts  │
│                                                             │
│ Checkpoint: downloading_complete → transcribing → complete  │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Chunking (Hybrid Dynamic + Sentence Snap)           │
│ ──────────────────────────────────────────────────────────── │
│ • Calculate ~5-min segments                                 │
│ • Search ±30s for nearest sentence boundary (., !, ?)       │
│ • Snap to full sentence boundaries                          │
│ • Virtual chunks - use original video with timestamps       │
│                                                             │
│ Checkpoint: transcribing_complete → chunking → complete     │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Audio Extraction (FFmpeg)                            │
│ ──────────────────────────────────────────────────────────── │
│ • Extract MP3 audio per chunk                               │
│ • 128kbps, for listening-only mode                         │
│ • Stored at data/audios/{video_id}/chunk_{n}.mp3           │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Study Plan Generation (LLM)                         │
│ ──────────────────────────────────────────────────────────── │
│ • Select highest priority transcript:                       │
│   user > youtube_author > whisper > youtube_auto            │
│ • Generate: vocabulary, grammar, study objectives           │
│ • All Chinese in Traditional Chinese (繁體中文)             │
│                                                             │
│ Checkpoint: audio_extracted → studying → ready             │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Return Complete Video Object              │
│  • Video metadata        • Chunks with timestamps          │
│  • Transcripts           • Study plan with vocabulary       │
└─────────────────────────────────────────────────────────────┘
```

### Checkpoint-Resume State Machine
```
┌──────────────────────────────────────────────────────────────┐
│  pending ──► downloading ──► downloading_complete            │
│       │                                                │     │
│       │           ┌─────────────────────────────────┘     │
│       │           │                                       │
│       ▼           ▼                                       │
│  transcribing ──► transcribing_complete                   │
│       │                                                │     │
│       │           ┌─────────────────────────────────┘     │
│       │           │                                       │
│       ▼           ▼                                       │
│   chunking ──► chunking_complete ──► audio_extracted       │
│                                                │            │
│                                                ▼            │
│                                    studying ──► ready       │
│                                                │            │
│                                                ▼            │
│                                             failed ◄──┬──┘
│                                                       │
│                              POST /api/videos/{id}/retry
└──────────────────────────────────────────────────────────────┘
```

---

## Slide 7: Key Code Snippets - Whisper Transcription Service
```python
# app/services/transcription_service.py

class WhisperTranscriptionService:
    """Service for transcribing audio using faster-whisper."""
    def _load_model(self):
        from faster_whisper import WhisperModel
        self._model = WhisperModel(
            self.model_size, # Model sizes: tiny, base, small, medium, large-v3
            device="cpu",
            compute_type="int8",
            cpu_threads=4,
        )

    async def transcribe(...) -> List[dict]:
        self._load_model()
        segments, info = await asyncio.to_thread(
            lambda: self._model.transcribe(
                str(audio_path),
                language=language, # 'en' here.
                word_timestamps=word_timestamps,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
            ),
        )
```

## Slide 8: Key Code Snippets - LLM Service Initialization
```python
# app/services/llm_service.py

class LLMService:
    """Service for LLM inference using llama-cpp-python."""
    def _ensure_model(self) -> None:
        from llama_cpp import Llama
        self._model = Llama(
            model_path=str(self.model_path),
            n_ctx=n_ctx,           # 8192 tokens
            n_threads=n_threads,   # CPU threads
            n_gpu_layers=config["n_gpu_layers"],  # Auto-calculated
            verbose=False,
        )
```

## Slide 9: Key Code Snippets - Study Plan Generation
```python
    SYSTEM_PROMPT = """You are an expert English language teacher. Your role is to analyze video transcripts and create personalized study plans for English learners.

    """Generate a study plan from transcript using LLM."""
    async def generate_study_plan(...) -> tuple[dict[str, Any], dict[str, float]]:
        user_prompt = f"""Based on the following video transcript...
        Transcript (first 4000 chars): {transcript_text[:4000]}

        Generate a study plan with vocabulary, grammar, and chunk summaries.
        IMPORTANT: All Chinese translations in TRADITIONAL Chinese (繁體中文) ONLY.
        """
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        response = await self._generate_response(messages)
```

**Speaker Notes**: 說明我們如何使用 llama-cpp-python 的 GPU 自動檢測功能，以及 Lazy loading 模式如何節省資源。

---

## Slide 10: Problems Encountered & Solutions (問題與解決方案)
### 1: CUDA Support & Python Version (CUDA 支援與 Python 版本)

```
┌────────────────────────────────────────────────────────────────┐
│  🔴 PROBLEM                                                     │
│  ────────────────────────────────────────────────────────────  │
│  llama-cpp-python with CUDA support requires specific Python   │
│  versions 3.10 ~ 3.12. Python 3.13+ is NOT supported.          │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  ✅ SOLUTION                                                    │
│  ────────────────────────────────────────────────────────────  │
│  1. Use Python 3.12 as the required version                    │
│  2. Set LLM_GPU_LAYERS=0 for CPU-only mode on Python 3.13+    │
│  3. Add runtime detection and graceful fallback                │
└────────────────────────────────────────────────────────────────┘
```

## Slide 11: Problems Encountered & Solutions (問題與解決方案)
### Problem 2: Audio Recording from Browser (瀏覽器音頻錄製)

```
┌────────────────────────────────────────────────────────────────┐
│  🔴 PROBLEM                                                     │
│  ────────────────────────────────────────────────────────────  │
│  Browsers require HTTPS for microphone access via MediaRecorder│
│  API. Development servers using HTTP will fail silently.       │
│                                                                │
│  Error: "getUserMedia() not available on insecure origins"     │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  ✅ SOLUTION                                                    │
│  ────────────────────────────────────────────────────────────  │
│  1. Generate self-signed SSL certificate for development       │
│  2. Configure uvicorn with SSL                                 │
│  3. Update CORS settings for HTTPS                             │
│  4. OR use ngrok.                             │
│                                                                │
│  Commands:                                                     │
│  openssl req -x509 -newkey rsa:2048 \                          │
│      -keyout key.pem -out cert.pem \                          │
│      -days 365 -nodes -subj "/CN=YOUR_HOST"                    │
│                                                                │
│  uvicorn app.main:app --ssl-keyfile key.pem \                 │
│                  --ssl-certfile cert.pem                      │
│                                                                │
│  Note: For production, use proper SSL certificates             │
└────────────────────────────────────────────────────────────────┘
```

## Slide 12: Problems Encountered & Solutions (問題與解決方案)
### Problem 3: Traditional Chinese Support (繁體中文支援)

```
┌────────────────────────────────────────────────────────────────┐
│  🔴 PROBLEM                                                     │
│  ────────────────────────────────────────────────────────────  │
│  LLM may generate Simplified Chinese instead of Traditional   │
│  Chinese. Need consistent Traditional Chinese throughout.     │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  ✅ SOLUTION                                                    │
│  ────────────────────────────────────────────────────────────  │
│  Add explicit instruction in system prompt:                 │
│                                                                │
│  IMPORTANT: All Chinese translations MUST be in                │
│  TRADITIONAL Chinese (繁體中文) ONLY.                          │
│  Examples: 學習 not 学习, 詞匯 not 词汇                         │
└────────────────────────────────────────────────────────────────┘
```

---

## Slide 13: Future Enhancements (未來改進)

```
┌────────────────────────────────────────────────────────────────┐
│                    FUTURE ENHANCEMENTS                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  □ Model upgrades (larger LLM for better inference quality)    │
│  □ Multi-language support beyond Chinese/English               │
│  □ Improved pronunciation feedback with advanced ASR           │
│  □ Docker Compose for easy deployment                         │
│  □ Multi-user support with authentication                     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Slide 14: Q&A (問答時間)

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                          Q & A                                ║
║                       問答時間                                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Slide 15: Thank You (感謝聆聽)

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                    Thank You!                                 ║
║                    感謝聆聽！                                   ║
║                                                               ║
║  ───────────────────────────────────────────────────────────  ║
║                                                               ║
│     □ GitHub: https://github.com/Yeh-Jack/speak.git        │
│     □ Demo: https://unshaven-travesty-luckless.ngrok-free.dev │
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```
