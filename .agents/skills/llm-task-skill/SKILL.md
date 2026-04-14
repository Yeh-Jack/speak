# LLM Task Skill

## Description
LLM integration with llama.cpp, task queuing with Celery, and OpenAI-compatible API for study plan generation.

## When to Use
Use this skill when integrating LLMs, generating study plans, creating exam questions, or implementing async task processing.

## Guidelines

### Architecture

```
User Request → FastAPI → Redis Queue → Celery Worker → llama.cpp → Store Result → Notify User
```

### LLM Models (User-Selectable)

| Model | Parameters | Use Case |
|-------|------------|----------|
| **Qwen2.5** | 7B | Primary model - best multilingual, excellent reasoning |
| **Gemma 4 E4B-it** | 8B | Alternative - Google's newest |
| **Llama 3.2** | 3B | Low resource mode - lightweight |
| **Gemma 4 E2B-it** | 5B | Fallback - ultra-lightweight |

**Note**: All models use **Q4_K_M** quantization. No A/V processing from Gemma (unified text only).

### Docker Compose Service

```yaml
services:
  llama-cpp:
    image: ghcr.io/ggerganov/llama.cpp:server-cuda
    volumes:
      - ./models:/models:ro
    environment:
      - LLAMA_ARG_PORT=8080
    command: >
      --model /models/qwen2.5-7b-q4_k_m.gguf
      --ctx-size 32768
      --n-gpu-layers 35
      --host 0.0.0.0
      --port 8080
    ports:
      - "8080:8080"
```

### OpenAI-Compatible API Client

```python
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass
import httpx
import json

@dataclass
class ChatMessage:
    role: str  # "system", "user", "assistant"
    content: str

class LlamaCppProvider:
    """llama.cpp OpenAI-compatible API provider."""
    
    def __init__(self, base_url: str = "http://llama-cpp:8080"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=None)  # No timeout for chunk processing
    
    async def chat_completion(
        self,
        messages: List[ChatMessage],
        model: str = "qwen2.5:7b",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> str:
        """Send chat completion request to llama.cpp."""
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        response = await self.client.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload
        )
        response.raise_for_status()
        
        if stream:
            return self._handle_stream(response)
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    async def _handle_stream(self, response) -> AsyncGenerator[str, None]:
        """Handle streaming response."""
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = json.loads(line[6:])
                if "choices" in data:
                    delta = data["choices"][0].get("delta", {})
                    if "content" in delta:
                        yield delta["content"]
```

### Model Factory

```python
class LLMService:
    """LLM service with provider switching."""
    
    AVAILABLE_MODELS = {
        "qwen2.5:7b": {
            "name": "Qwen2.5",
            "description": "Best multilingual, excellent reasoning",
            "max_tokens": 32768,
            "default_max_tokens": 2048,
            "temperature": 0.7
        },
        "gemma-4-e4b-it:8b": {
            "name": "Gemma 4 E4B-it",
            "description": "Google's newest, good quality",
            "max_tokens": 8192,
            "default_max_tokens": 2048,
            "temperature": 0.7
        },
        "llama-3.2:3b": {
            "name": "Llama 3.2",
            "description": "Lightweight, Meta quality",
            "max_tokens": 4096,
            "default_max_tokens": 2048,
            "temperature": 0.7
        },
        "gemma-4-e2b-it:5b": {
            "name": "Gemma 4 E2B-it",
            "description": "Ultra-lightweight fallback",
            "max_tokens": 4096,
            "default_max_tokens": 2048,
            "temperature": 0.7
        }
    }
    
    def __init__(self, base_url: str = "http://llama-cpp:8080"):
        self.provider = LlamaCppProvider(base_url)
        self.current_model = "qwen2.5:7b"
    
    def set_model(self, model_id: str):
        """Switch active model."""
        if model_id not in self.AVAILABLE_MODELS:
            raise ValueError(f"Unknown model: {model_id}")
        self.current_model = model_id
    
    def list_models(self) -> List[dict]:
        """List available models."""
        return [
            {"id": k, **v}
            for k, v in self.AVAILABLE_MODELS.items()
        ]
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion with current model."""
        model_config = self.AVAILABLE_MODELS[self.current_model]
        
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt)
        ]
        
        return await self.provider.chat_completion(
            messages=messages,
            model=self.current_model,
            max_tokens=max_tokens or model_config["default_max_tokens"],
            temperature=model_config["temperature"]
        )
```

### Study Plan Generation

```python
class StudyPlanService:
    """Generate study plans using LLM."""
    
    SYSTEM_PROMPT = """You are an expert English teacher. Given a video transcript, 
generate a structured study plan with learning objectives, key vocabulary with CEFR levels,
grammar points, cultural notes, practice exercises, and estimated study time.

Respond ONLY with valid JSON in this exact format:
{
    "objectives": ["string"],
    "vocabulary": [{"word": "string", "definition": "string", "cefr": "A1|A2|B1|B2|C1|C2", "context": "string"}],
    "grammar": ["string"],
    "cultural_notes": "string",
    "exercises": [{"type": "multiple_choice|fill_blank|speaking", "question": "string", "answer": "string"}],
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
        
        # Build context from transcript (first 50 entries)
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
        
        response = await self.llm.generate(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=4096
        )
        
        # Parse JSON response
        import json
        import re
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            raise ValueError("Failed to parse LLM response as JSON")
```

### Celery Task Queue

```python
from celery import Celery
from celery.signals import task_postrun
import asyncio

# Initialize Celery
celery = Celery('english_learning')
celery.conf.update(
    broker_url='redis://redis:6379/0',
    result_backend='redis://redis:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    # No time limits for chunk processing
    task_time_limit=None,
    task_soft_time_limit=None,
    worker_prefetch_multiplier=1,
)

# Task priority routes
celery.conf.task_routes = {
    'tasks.transcribe_video': {'queue': 'high'},
    'tasks.process_youtube': {'queue': 'high'},
    'tasks.generate_study_plan': {'queue': 'medium'},
    'tasks.generate_exam_questions': {'queue': 'medium'},
    'tasks.analyze_vocabulary': {'queue': 'medium'},
    'tasks.chat_with_teacher': {'queue': 'low'},
}

@celery.task(bind=True, max_retries=3)
def generate_study_plan_task(self, video_id: str, chunk_index: int):
    """Background task for study plan generation."""
    try:
        # Get video and transcript from DB
        # Call StudyPlanService
        # Store result
        return {"status": "completed", "video_id": video_id}
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@celery.task(bind=True, max_retries=3)
def transcribe_video_task(self, video_id: str):
    """Background task for transcription."""
    pass

@celery.task(bind=True, max_retries=3)
def generate_exam_questions_task(self, video_id: str):
    """Background task for exam question generation."""
    pass

@celery.task(bind=True)
def chat_with_teacher_task(self, user_id: str, message: str):
    """Low priority chat task."""
    pass

# Task completion signal
@task_postrun.connect
def task_postrun_handler(task_id, task, retval, state, **kwargs):
    """Notify user when task completes."""
    if state == 'SUCCESS':
        # Send notification via WebSocket or push notification
        pass
```

### Task Priority Configuration

```python
TASK_PRIORITIES = {
    'transcribe_video': 10,        # High - blocks other tasks
    'process_youtube': 10,           # High - blocks other tasks
    'generate_study_plan': 5,        # Medium
    'generate_exam_questions': 5,    # Medium
    'analyze_vocabulary': 5,         # Medium
    'chat_with_teacher': 1,          # Low - user-facing
}
```

### API Endpoints

```python
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel

router = APIRouter(prefix="/api/tasks")

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

@router.post("/study-plan/{video_id}")
async def queue_study_plan(
    video_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> TaskResponse:
    """Queue study plan generation."""
    task = generate_study_plan_task.delay(video_id, chunk_index=0)
    return TaskResponse(
        task_id=task.id,
        status="pending",
        message="Study plan generation queued"
    )

@router.get("/{task_id}")
async def get_task_status(task_id: str) -> dict:
    """Check task status."""
    result = celery.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }
```

## Task Types

| Task | Priority | Description |
|------|----------|-------------|
| `transcribe_video` | High | Whisper transcription |
| `process_youtube` | High | YouTube download and processing |
| `generate_study_plan` | Medium | LLM study plan generation |
| `generate_exam_questions` | Medium | LLM exam question generation |
| `analyze_vocabulary` | Medium | Extract and analyze vocabulary |
| `chat_with_teacher` | Low | LLM conversational response |

## Dependencies

```
# HTTP client
httpx>=0.25.0

# Task queue
celery[redis]>=5.3.0
redis>=4.6.0

# Retry logic
tenacity>=8.2.0
```

## Environment Variables

```bash
# LLM Configuration
LLAMA_CPP_URL=http://llama-cpp:8080
DEFAULT_MODEL=qwen2.5:7b

# Task Queue
REDIS_URL=redis://redis:6379/0

# Available models (comma-separated)
AVAILABLE_MODELS=qwen2.5:7b,gemma-4-e4b-it:8b,llama-3.2:3b,gemma-4-e2b-it:5b
```

## Notes

- All models use Q4_K_M quantization for optimal performance
- Process in chunks to avoid timeout (5-10 min video segments)
- No timeout limits for LLM tasks (use Celery without task_time_limit)
- Implement retry logic with exponential backoff
- Cache results in Redis for duplicate requests
- Use streaming responses for chat endpoints
