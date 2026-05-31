# LLM Task Skill

## Description
LLM integration using llama-cpp-python with fixed Qwen3.5-2B-Q4_K_M model for study plan generation. Single model, no switching. All processing is immediate async (no task queue).

## When to Use
Use this skill when integrating LLMs, generating study plans, or implementing chat with teacher features.

## Language Rule

**MANDATORY: ALL Chinese text must be Traditional Chinese (繁體中文). No Simplified Chinese allowed.**

Every LLM prompt that may generate Chinese content MUST include this instruction:
```
IMPORTANT: When generating any Chinese text (definitions, explanations, notes, feedback),
you MUST use Traditional Chinese (繁體中文). Do NOT use Simplified Chinese.
```

## Guidelines

### Architecture

```
User Request → FastAPI → llama-cpp-python (in-backend) → Response
                          ↓
                    Qwen3.5-2B-Q4_K_M.gguf
                    (Fixed model, no switching)
```

### LLM Configuration

**Fixed Model**: Qwen3.5-2B-Q4_K_M.gguf (Q4_K_M quantization)

| Setting | Value |
|---------|-------|
| Model | Qwen3.5-2B-Q4_K_M.gguf |
| Context Size | 4096 |
| Quantization | Q4_K_M (GGUF format) |
| GPU Layers | -1 (auto-detect), 0 (CPU only), N (specific) |

### GPU Auto-Detection

```python
from app.utils.gpu_utils import gpu_manager

from app.core.config import LLM_MODEL_PATH

config = gpu_manager.get_llama_config(
    model_path=str(LLM_MODEL_PATH / "Qwen3.5-2B-Q4_K_M.gguf"),
    env_gpu_layers=os.getenv("LLM_GPU_LAYERS", "-1")
)
# Returns: {"n_ctx": 4096, "n_gpu_layers": auto_calculated, "verbose": False}
```

### In-Backend Integration

```python
from llama_cpp import Llama

class LLMService:
    """LLM service with fixed Qwen3.5-2B model."""

    def __init__(self, model_path: str = ""):
        if not model_path:
            from app.core.config import LLM_MODEL_PATH
            model_path = str(LLM_MODEL_PATH / "Qwen3.5-2B-Q4_K_M.gguf")
        self.model_path = model_path
        self._llm: Optional[Llama] = None

    async def _load_model(self):
        """Lazy load model with GPU configuration."""
        if self._llm is None:
            config = gpu_manager.get_llama_config(
                model_path=self.model_path,
                env_gpu_layers=os.getenv("LLM_GPU_LAYERS", "-1")
            )
            self._llm = Llama(model_path=self.model_path, **config)

    async def chat_completion(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """Generate chat completion."""
        await self._load_model()
        response = self._llm.create_chat_completion(
            messages=[m.dict() for m in messages],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response['choices'][0]['message']['content']

    async def chat_completion_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion tokens."""
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
```

### Study Plan Generation

```python
class StudyPlanService:
    """Generate study plans using LLM."""

    SYSTEM_PROMPT = """You are an expert English teacher. Given a video transcript,
    generate a structured study plan with learning objectives, key vocabulary with CEFR levels,
    grammar points, cultural notes, and estimated study time.

    IMPORTANT: All Chinese text MUST be Traditional Chinese (繁體中文). No Simplified Chinese.
    When generating vocabulary definitions, grammar explanations, or any Chinese notes,
    use Traditional Chinese characters only. Examples: 是、開發、學習、詞彙、語法

    Respond ONLY with valid JSON in this exact format:
    {
        "objectives": ["string"],
        "vocabulary": [{"word": "string", "word_zh": "string (Traditional Chinese)", "definition": "string (English)", "definition_zh": "string (Traditional Chinese)", "example": "string (English)", "example_zh": "string (Traditional Chinese)", "cefr": "A1|A2|B1|B2|C1|C2", "difficulty": "easy|medium|hard", "difficulty_zh": "簡單|中等|困難"}],
        "grammar": [{"pattern": "string", "pattern_zh": "string (Traditional Chinese)", "explanation": "string (English)", "explanation_zh": "string (Traditional Chinese)", "examples": ["sentence using the grammar pattern", "another sentence using the pattern"], "examples_zh": ["使用該語法結構的例句（繁體中文）", "另一個使用該語法結構的例句（繁體中文）"]}],
        "cultural_notes": "string (English)",
        "cultural_notes_zh": "string (Traditional Chinese)",
        "estimated_time": "string",
        "overall_difficulty": "A1|A2|B1|B2|C1|C2"
    }"""

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    async def generate_study_plan(
        self,
        video_title: str,
        transcript: List[dict],
        chunk_index: int,
        chunk_duration: float
    ) -> dict:
        """Generate study plan for a video chunk."""
        transcript_text = "\n".join([
            f"[{entry['start']}] {entry['text']}"
            for entry in transcript[:50]
        ])

        user_prompt = f"""Video Title: {video_title}
Chunk: {chunk_index + 1}
Duration: {chunk_duration // 60} minutes

Transcript:
{transcript_text}

Generate a study plan as JSON."""

        messages = [
            ChatMessage(role="system", content=self.SYSTEM_PROMPT),
            ChatMessage(role="user", content=user_prompt)
        ]

        response = await self.llm.chat_completion(
            messages=messages,
            max_tokens=4096
        )

        import json
        import re
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            raise ValueError("Failed to parse LLM response as JSON")
```

### Chat with Teacher

```python
async def chat_with_teacher(
    self,
    message: str,
    context: Optional[str] = None
) -> str:
    """Conversational response with optional video context."""
system_prompt = """You are a friendly English teacher helping users learn English through video content.
    Be encouraging, provide examples, and correct mistakes gently.

    IMPORTANT: All Chinese text MUST be in Traditional Chinese (繁體中文). No Simplified Chinese.
    When explaining vocabulary, grammar, or providing feedback in Chinese, use Traditional Chinese characters only.
    Examples: 是、開發、學習、詞彙、語法"""

    if context:
        system_prompt += f"\n\nCurrent study context:\n{context}"

    messages = [
        ChatMessage(role="system", content=system_prompt),
        ChatMessage(role="user", content=message)
    ]

    return await self.llm.chat_completion(messages=messages)
```

### Vocabulary Analysis

```python
async def analyze_vocabulary(
    self,
    transcript: List[dict],
    cefr_range: tuple = ("A1", "C2")
) -> List[dict]:
    """Extract and analyze vocabulary from transcript."""
    transcript_text = "\n".join([
        f"[{entry['start']}] {entry['text']}"
        for entry in transcript[:100]
    ])

    user_prompt = f"""Extract vocabulary words from this transcript.
Focus on words between CEFR levels {cefr_range[0]} and {cefr_range[1]}.

Transcript:
{transcript_text}

Respond with JSON array:
{{"words": [{{"word": "string", "definition": "string", "cefr": "string", "example_sentence": "string"}}]}}"""

    messages = [
        ChatMessage(role="system", content="You are a vocabulary expert."),
        ChatMessage(role="user", content=user_prompt)
    ]

    response = await self.llm.chat_completion(messages=messages, max_tokens=4096)
    # Parse and return vocabulary list
```

## API Endpoints

```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/chat")

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

@router.post("")
async def chat(request: ChatRequest) -> dict:
    """Chat with LLM teacher."""
    response = await llm_service.chat_with_teacher(
        message=request.message,
        context=request.context
    )
    return {"response": response}

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat response."""
    async def generate():
        async for token in llm_service.chat_completion_stream(messages):
            yield f"data: {token}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

## LLM Operations

| Operation | Description | When Called |
|-----------|-------------|-------------|
| `generate_study_plan` | Generate learning plan | During video creation (immediate) |
| `chat_with_teacher` | Conversational response | User chat message |
| `analyze_vocabulary` | Extract vocabulary | During video creation (immediate) |

## Dependencies

```
# llama-cpp-python with GPU support
llama-cpp-python>=0.2.0

# GPU detection
GPUtil>=1.4.0
```

## Environment Variables

The following are fixed system constants (not configurable via environment):
- `LLM_MODEL_PATH` - Fixed at `PROJECT_ROOT/data/models` (e.g., `/app/data/models` in Docker)

```bash
# LLM (Fixed model - no switching)
DEFAULT_MODEL=Qwen3.5-2B-Q4_K_M.gguf
LLM_GPU_LAYERS=-1  # -1=auto, 0=CPU only, N=specific layers
LLM_CONTEXT_SIZE=8192  # Model context window (~3-5 min video per study plan)
LLM_THREADS=4
```

## Notes

- **Single fixed model**: Qwen3.5-2B-Q4_K_M.gguf only (no model switching)
- **No task queue**: All processing is immediate async with await
- **GPU auto-detection**: Automatically calculates optimal GPU layers based on VRAM
- **Streaming supported**: Real-time token generation for chat endpoints
- **Video length limit**: ~3-5 minutes per study plan (transcript truncated to 4000 chars)