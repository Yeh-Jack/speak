# English Speaking Learning App - Project Presentation

## 英文口說學習系統 - 專案簡報

---

## Slide 1: Cover Page (封面)

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          🎬 English Speaking Learning App                     ║
║          英文口說學習系統                                      ║
║                                                               ║
║  AI-Powered English Learning Platform                         ║
║  利用大型語言模型打造個人化英語學習體驗                         ║
║                                                               ║
║  ─────────────────────────────────────────────────────────────║
║                                                               ║
║  Project Type: Full-Stack AI Application                     ║
║  Tech Stack: FastAPI + Vue 3 + llama-cpp-python              ║
║  Target: 個人英語學習者 | Single-user application              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**Suggested Visual**: App logo, screenshot of video player with subtitles, AI chat interface

---

## Slide 2: Motivation & Problem Statement (動機與問題)

### Why This Project?
```
┌────────────────────────────────────────────────────────────────┐
│ 傳統英語學習的痛點                                               │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ❌ 昂貴的一對一家教                                             │
│  ❌ 缺乏互動性的傳統教材                                         │
│  ❌ 無法根據個人程度調整學習內容                                 │
│  ❌ 影視教材缺乏系統性學習規劃                                   │
│                                                                │
│  解決方案：                                               │
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
│     (yt-dlp)              (LLM + Whisper)            (Study  │
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

## Slide 3: Tech Stack Overview (技術堆疊)

```
┌─────────────────────────────────────────────────────────────────┐
│                        TECH STACK                               │
├───────────────┬─────────────────────────────────────────────────┤
│                                                               │
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

## Slide 4: System Architecture (系統架構)

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

## Slide 5: Processing Pipeline (處理流程)

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

## Slide 6: Key Code Snippets - LLM Service (重點程式碼 - LLM 服務)

### LLM Service Initialization
```python
# app/services/llm_service.py

class LLMService:
    """Service for LLM inference using llama-cpp-python."""
    
    def _ensure_model(self) -> None:
        """Lazy load the llama-cpp-python model."""
        if self._initialized:
            return
        
        env_gpu_layers = os.getenv("LLM_GPU_LAYERS", settings.LLM_GPU_LAYERS)
        config = get_llama_config(str(self.model_path), env_gpu_layers, model_size="2B")
        
        from llama_cpp import Llama
        
        self._model = Llama(
            model_path=str(self.model_path),
            n_ctx=n_ctx,           # 8192 tokens
            n_threads=n_threads,   # CPU threads
            n_gpu_layers=config["n_gpu_layers"],  # Auto-calculated
            verbose=False,
        )
        self._initialized = True
```

### Study Plan Generation
```python
    async def generate_study_plan(
        self,
        transcript: dict,
        video_title: str,
        video_duration: float,
    ) -> tuple[dict[str, Any], dict[str, float]]:
        """Generate a study plan from transcript using LLM."""
        
        transcript_text = self._format_transcript_for_prompt(transcript)
        
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
        return self._parse_json_response(response)
```

**Speaker Notes**: 說明我們如何使用 llama-cpp-python 的 GPU 自動檢測功能，以及 Lazy loading 模式如何節省資源。

---

## Slide 7: Key Code Snippets - Video Processing (重點程式碼 - 影片處理)

### Hybrid Dynamic Chunking with Sentence Snap
```python
# app/services/chunking_service.py

class ChunkingService:
    """Virtual time-based chunking with sentence-aware boundaries."""
    
    SENTENCE_PUNCTUATION = {'.', '!', '?'}
    SEARCH_WINDOW = 30.0  # ±30 seconds

    def _find_sentence_boundary(self, target_time: float, transcript: List[dict]) -> float:
        """Find nearest sentence boundary within ±30s of target_time."""
        min_search = target_time - self.SEARCH_WINDOW
        max_search = target_time + self.SEARCH_WINDOW
        
        candidates = []
        for entry in transcript:
            if not (min_search <= entry["start"] <= max_search):
                continue
            
            text = entry.get("text", "")
            if text and self._ends_with_sentence(text):
                distance = abs(entry["start"] - target_time)
                candidates.append((distance, entry["start"]))
        
        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1]
        
        return target_time  # No boundary found, use ideal
```

---

## Slide 8: Algorithm Deep Dive (演算法深入解析)

### 1. Sentence Boundary Detection Algorithm
```
┌────────────────────────────────────────────────────────────────┐
│  SENTENCE BOUNDARY DETECTION                                    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Input: target_time, transcript_segments, SEARCH_WINDOW=30s     │
│  Output: adjusted_time (snapped to sentence boundary)          │
│                                                                │
│  Algorithm:                                                     │
│  ───────────────────────────────────────────────────────────  │
│  1. Define sentence punctuations: {'.', '!', '?'}             │
│  2. Calculate search range: [target-30s, target+30s]           │
│  3. Scan transcript for entries within range                   │
│  4. Filter entries where text ends with sentence punctuation   │
│  5. Select entry closest to target_time                       │
│  6. If no boundary found, return original target_time          │
│                                                                │
│  Edge Cases Handled:                                            │
│  ───────────────────────────────────────────────────────────  │
│  • Empty transcript entries → skip                             │
│  • No punctuation in window → return original target           │
│  • Multiple boundaries equidistant → pick first                │
│  • Overlapping segments → prioritize natural breaks           │
└────────────────────────────────────────────────────────────────┘
```

### 2. Whisper Transcription Accuracy Comparison
```
┌────────────────────────────────────────────────────────────────┐
│  WHISPER MODEL COMPARISON (English Video Test)                  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Model       │ Size  │ Speed  │ WER*   │ VRAM    │ Best For   │
│  ────────────┼───────┼────────┼────────┼─────────┼────────────│
│  Tiny       │ 75MB  │ 10x    │ ~8%    │ ~500MB  │ Speed      │
│  Base       │ 140MB │ 6x     │ ~6%    │ ~1GB    │ Balance    │
│  Small      │ 450MB │ 2x     │ ~4%    │ ~2GB    │ Accuracy   │
│  Medium     │ 1.5GB │ 1x     │ ~3%    │ ~5GB    │ High Prec  │
│  ───────────────────────────────────────────────────────────  │
│  *WER = Word Error Rate (lower is better)                      │
│                                                                │
│  Our Choice: Tiny Model                                        │
│  ───────────────────────────────────────────────────────────  │
│  • Trade accuracy for speed (processing time matters UX)      │
│  • Acceptable ~8% WER for learning context                    │
│  • 500MB VRAM leaves room for LLM (~1.5GB)                    │
│  • Can switch to Base/Small for better accuracy if needed    │
└────────────────────────────────────────────────────────────────┘
```

### 3. Transcript Priority Selection
```
┌────────────────────────────────────────────────────────────────┐
│  TRANSCRIPT PRIORITY ORDER (Highest → Lowest)                  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Priority  │ Type            │ Source      │ Use Case          │
│  ──────────┼─────────────────┼─────────────┼───────────────────│
│  1st      │ User Uploaded   │ User        │ Custom subtitles  │
│  2nd      │ youtube_author  │ YouTube     │ Professional      │
│  3rd      │ whisper         │ faster-whisper│ Always available│
│  4th      │ youtube_auto    │ YouTube     │ Auto-generated    │
│                                                                │
│  Rationale:                                                     │
│  • User uploaded = most accurate for learning                 │
│  • youtube_author = professionally created                    │
│  • whisper = consistent, not dependent on YouTube            │
│  • youtube_auto = least reliable (ASR errors)               │
└────────────────────────────────────────────────────────────────┘
```

---

## Slide 9: Chat with Tutor - Streaming Mode (導師聊天 - 流式模式)

### Real-time Streaming Chat Interface
```
┌────────────────────────────────────────────────────────────────┐
│  CHAT WITH AI TUTOR - STREAMING MODE                            │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  System: You are a helpful English tutor...              │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  User: What does "ubiquitous" mean?                            │
│                                                                │
│  Tutor: "Ubiquitous" (無所不在的) means...                    │
│         [streamed token by token in real-time]                │
│                                                                │
│  Features:                                                     │
│  • Server-Sent Events (SSE) for streaming responses          │
│  • Real-time token display as LLM generates                   │
│  • Interrupt/cancel ongoing generation                        │
│  • Context-aware with video transcript                       │
└────────────────────────────────────────────────────────────────┘
```

### Backend Streaming Implementation
```python
# app/services/llm_service.py

async def chat_stream(
    self,
    messages: List[dict],
    video_context: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """Stream LLM response token by token via SSE."""
    
    if video_context:
        messages = self._add_video_context(messages, video_context)
    
    async for token in self._stream_response(messages):
        yield f"data: {token}\n\n"
    
    yield "data: [DONE]\n\n"

# app/api/endpoints/chat.py
@router.post("/api/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """SSE endpoint for streaming chat responses."""
    
    async def event_generator():
        async for token in llm_service.chat_stream(
            messages=request.messages,
            video_context=request.video_context,
        ):
            yield token
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
```

### Frontend Streaming Component
```typescript
// frontend/src/composables/useChatStream.ts

export function useChatStream() {
  const messages = ref<ChatMessage[]>([])
  const isStreaming = ref(false)

  async function sendMessage(content: string, videoContext?: string) {
    isStreaming.value = true
    
    const response = await fetch("/api/chat/stream", {
      method: "POST",
      body: JSON.stringify({ messages: messages.value, videoContext }),
      headers: { "Content-Type": "application/json" },
    })

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    
    while (reader) {
      const { done, value } = await reader.read()
      if (done) break
      
      const chunk = decoder.decode(value)
      // Parse SSE data and append tokens in real-time
      for (const line of chunk.split("\n")) {
        if (line.startsWith("data: ")) {
          const token = line.slice(6)
          if (token !== "[DONE]") {
            appendToken(token) // Real-time UI update
          }
        }
      }
    }
    
    isStreaming.value = false
  }

  return { messages, isStreaming, sendMessage }
}
```

### Key Benefits of Streaming
```
┌────────────────────────────────────────────────────────────────┐
│  ✅ Better UX - See responses as they're generated             │
│  ✅ Lower perceived latency - First token appears immediately   │
│  ✅ Engagement - More interactive learning experience          │
│  ✅ Cancellation - Stop generation mid-response                │
└────────────────────────────────────────────────────────────────┘
```

---

## Slide 9: Problems Encountered & Solutions (問題與解決方案)

### Problem 1: CUDA Support & Python Version (CUDA 支援與 Python 版本)

```
┌────────────────────────────────────────────────────────────────┐
│  🔴 PROBLEM                                                     │
│  ────────────────────────────────────────────────────────────  │
│  llama-cpp-python with CUDA support requires specific Python   │
│  versions. Python 3.13+ is NOT supported.                      │
│                                                                │
│  Error: "Python 3.13 compatibility issues with CUDA backend"    │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  ✅ SOLUTION                                                    │
│  ────────────────────────────────────────────────────────────  │
│  1. Use Python 3.12 as the required version                    │
│  2. Set LLM_GPU_LAYERS=0 for CPU-only mode on Python 3.13+    │
│  3. Add runtime detection and graceful fallback                │
│                                                                │
│  Code:                                                         │
│  if sys.version_info >= (3, 13):                              │
│      os.environ["LLM_GPU_LAYERS"] = "0"  # Force CPU mode     │
│  else:                                                         │
│      # Use GPU if available                                    │
└────────────────────────────────────────────────────────────────┘
```

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

### Problem 3: GPU Memory Calculation (GPU 記憶體計算)

```
┌────────────────────────────────────────────────────────────────┐
│  🔴 PROBLEM                                                     │
│  ────────────────────────────────────────────────────────────  │
│  Need to calculate optimal GPU layers based on available VRAM  │
│  for the Q4_K_M quantized model.                                │
│                                                                │
│  • Model: Qwen3.5-2B-Q4_K_M (~1.5GB total)                    │
│  • Each layer: ~50MB                                            │
│  • Total layers: 28                                            │
│  • Need to reserve VRAM for other operations                  │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  ✅ SOLUTION - GPUtil + VRAM Calculation                       │
│  ────────────────────────────────────────────────────────────  │
│  1. Use GPUtil to detect NVIDIA GPUs and VRAM                  │
│  2. Subtract 1GB safety buffer                                 │
│  3. Calculate: available_vram / layer_size                   │
│  4. Cap at total model layers                                  │
│                                                                │
│  Config via environment:                                       │
│  • LLM_GPU_LAYERS=-1 (default): Auto-detect                    │
│  • LLM_GPU_LAYERS=N: Use N specific layers                    │
│  • LLM_GPU_LAYERS=0: Force CPU-only mode                       │
└────────────────────────────────────────────────────────────────┘
```

### Problem 4: Traditional Chinese Support (繁體中文支援)

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
│  1. Add explicit instruction in system prompt:                 │
│                                                                │
│  IMPORTANT: All Chinese translations MUST be in                │
│  TRADITIONAL Chinese (繁體中文) ONLY.                          │
│  Examples: 學習 not 学习, 詞匯 not 词汇                         │
│                                                                │
│  2. Add _zh suffix fields in all JSON schemas                 │
│  3. Validate in service layer                                  │
└────────────────────────────────────────────────────────────────┘
```

---

## Slide 10: Future Enhancements (未來改進)

```
┌────────────────────────────────────────────────────────────────┐
│                    FUTURE ENHANCEMENTS                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  🔮 PHASE 1: Enhanced AI Features                              │
│  ───────────────────────────────────────────────────────────  │
│  □ Model upgrades (larger LLM for better study plans)          │
│  □ Multi-language support beyond Chinese/English               │
│  □ Improved pronunciation feedback with advanced ASR           │
│  □ Personalized learning paths based on history               │
│                                                                │
│  🔮 PHASE 2: User Experience                                   │
│  ───────────────────────────────────────────────────────────  │
│  □ Progress tracking dashboard with visualizations            │
│  □ Spaced repetition for vocabulary review                    │
│  □ Mobile app (React Native or PWA)                            │
│  □ Collaborative features (share courses)                      │
│                                                                │
│  🔮 PHASE 3: Content Expansion                                 │
│  ───────────────────────────────────────────────────────────  │
│  □ Support for local video files                               │
│  □ Podcast and audio-only content                              │
│  □ Integration with other video platforms                      │
│  □ Custom subtitle upload for any video                       │
│                                                                │
│  🔮 PHASE 4: Infrastructure                                    │
│  ───────────────────────────────────────────────────────────  │
│  □ Docker Compose for easy deployment                         │
│  □ Cloud storage for videos                                    │
│  □ Multi-user support with authentication                     │
│  □ API rate limiting and monitoring                           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Slide 11: Demo / Live Preview (展示環節)

```
┌────────────────────────────────────────────────────────────────┐
│                      LIVE DEMO                                 │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  1. Submit a YouTube URL                                       │
│     → https://www.youtube.com/watch?v=example                 │
│                                                                │
│  2. Watch processing pipeline                                  │
│     Download → Transcribe → Chunk → Study Plan               │
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
│  7. Resources                                      │
│     □ GitHub: https://github.com/Yeh-Jack/speak.git        │
│     □ https://unshaven-travesty-luckless.ngrok-free.dev │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Slide 12: Project Summary (專案總結)

```
┌────────────────────────────────────────────────────────────────┐
│                    PROJECT SUMMARY                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ✅ Successfully built AI-powered English learning platform    │
│                                                                │
│  Key Achievements:                                            │
│  ───────────────────────────────────────────────────────────  │
│  • Embedded LLM with llama-cpp-python (no API costs)         │
│  • NVIDIA GPU acceleration with auto-detection                 │
│  • Hybrid Dynamic chunking with sentence-aware boundaries     │
│  • Checkpoint-resume for reliable processing                  │
│  • Traditional Chinese support throughout                     │
│  • Async/await for non-blocking operations                    │
│                                                                │
│  Architecture Highlights:                                      │
│  ───────────────────────────────────────────────────────────  │
│  • FastAPI + Vue 3 (modern, async Python + reactive JS)       │
│  • Repository + Service pattern (clean separation)           │
│  • Pydantic v2 for validation                                  │
│  • SQLAlchemy 2.0 async ORM                                    │
│                                                                │
│  Challenges Solved:                                            │
│  ───────────────────────────────────────────────────────────  │
│  • CUDA + Python 3.12 compatibility                            │
│  • HTTPS requirement for browser audio recording              │
│  • GPU VRAM calculation for optimal layer offloading         │
│  • Consistent Traditional Chinese in AI-generated content     │
│                                                                │
│  Results:                                                      │
│  ───────────────────────────────────────────────────────────  │
│  • Personal AI tutor available 24/7                           │
│  • Personalized study plans from any YouTube video            │
│  • Interactive learning with speaking practice                │
│  • Open-source and self-hostable                              │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Slide 13: Q&A (問答時間)

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                          Q & A                                ║
║                       問答時間                                 ║
║                                                               ║
║  ───────────────────────────────────────────────────────────  ║
║                                                               ║
║   歡迎提問！                                                   ║
║   Questions & Discussion                                      ║
║                                                               ║
║  Topics for discussion:                                       ║
║   • LLM integration and optimization                          ║
║   • Video processing pipeline                                  ║
║   • GPU configuration and CUDA support                        ║
║   • Async Python patterns                                      ║
║   • Future enhancements                                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Slide 14: Additional Suggested Pages (建議投影片)

Based on the project, here are additional slides you may consider:

```
┌────────────────────────────────────────────────────────────────┐
│               ADDITIONAL SLIDES TO CONSIDER                     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  📊 Performance Metrics                                        │
│  ───────────────────────────────────────────────────────────  │
│  • Processing time per stage (download, transcription, etc.)  │
│  • LLM inference speed with/without GPU                        │
│  • Memory usage comparison (CPU vs GPU mode)                   │
│                                                                │
│  📈 Cost Analysis                                              │
│  ───────────────────────────────────────────────────────────  │
│  • API cost comparison (OpenAI vs local LLM)                   │
│  • Hardware requirements and costs                            │
│  • Scalability considerations                                 │
│                                                                │
│  🔧 Technical Deep Dives                                       │
│  ───────────────────────────────────────────────────────────  │
│  • Whisper transcription accuracy comparison                   │
│  • Sentence boundary detection algorithm                       │
│  • Chunk size optimization analysis                            │
│                                                                │
│  📚 Learning Outcomes                                          │
│  ───────────────────────────────────────────────────────────  │
│  • How this helps English learners                             │
│  • Comparison with traditional methods                         │
│  • User feedback and improvement areas                         │
│                                                                │
│  🏗️ Deployment Guide                                          │
│  ───────────────────────────────────────────────────────────  │
│  • Docker setup walkthrough                                    │
│  • Environment configuration                                    │
│  • Troubleshooting common issues                              │
│                                                                │
│  🤝 Contributing Guidelines                                    │
│  ───────────────────────────────────────────────────────────  │
│  • Code style and conventions                                  │
│  • Testing requirements                                       │
│  • Pull request process                                        │
│                                                                │
└────────────────────────────────────────────────────────────────┘
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
║  Project Repository: github.com/yourusername/english-learning ║
║  Documentation: /docs                                         ║
║  Demo: localhost:8080                                         ║
║                                                               ║
║  Built with:                                                  ║
║   FastAPI + Vue 3 + llama-cpp-python + faster-whisper        ║
║                                                               ║
║  ───────────────────────────────────────────────────────────  ║
║                                                               ║
║  Questions? Feel free to reach out!                            ║
║  有任何問題，歡迎聯繫！                                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Appendix: Key File Structure (附錄：專案結構)

```
english-learning-app/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # API endpoints
│   │   ├── core/                 # Config, logging
│   │   ├── db/                   # Database session
│   │   ├── models/               # SQLAlchemy models
│   │   ├── repositories/         # Data access layer
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/             # Business logic
│   │   └── utils/               # GPU utilities
│   └── alembic/                  # Database migrations
│
├── frontend/
│   ├── src/
│   │   ├── components/           # Vue components
│   │   ├── views/                # Page views
│   │   ├── composables/          # Vue composables
│   │   ├── services/            # API client
│   │   └── stores/              # Pinia stores
│   └── tests/
│
├── data/
│   ├── db/learning.db           # SQLite database
│   ├── videos/                   # Downloaded videos
│   ├── subtitles/               # YouTube subtitles
│   ├── transcripts/             # JSON transcripts
│   ├── audios/                  # Extracted audio
│   └── models/                  # LLM model files
│
├── design-specs.md              # Architecture & design
├── requirements.md               # Technical specification
└── README.md                    # Project documentation
```

---

## Appendix: Environment Variables (附錄：環境變數)

```bash
# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8080
FRONTEND_DIST=/path/to/frontend/dist
CORS_ALLOW_ORIGINS=http://localhost:3000

# LLM Configuration (llama-cpp-python)
DEFAULT_MODEL=Qwen3.5-2B-Q4_K_M.gguf
LLM_GPU_LAYERS=-1           # -1=auto, 0=CPU only, N=specific layers
LLM_CONTEXT_SIZE=8192      # Context window size
LLM_THREADS=4              # CPU threads

# Video Processing
YOUTUBE_DOWNLOAD_QUALITY=720
YOUTUBE_AUDIO_QUALITY=128k
CHUNK_DURATION=300         # 5 minutes

# Storage
PROJECT_ROOT=/app          # Docker: /app, Local: auto-detected
```

---

**End of Presentation Outline**

Total: 15 slides (+ 2 appendix slides for additional content)

This outline covers all requested topics and provides comprehensive detail for each slide. Adjust content as needed based on presentation time and audience.
