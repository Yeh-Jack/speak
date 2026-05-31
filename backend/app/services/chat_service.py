"""Chat service for AI tutor functionality."""

import asyncio
import json
from typing import AsyncGenerator

from app.core.config import settings, LLM_MODEL_PATH
from app.core.logging import get_logger
from app.utils.gpu_utils import get_llama_config

logger = get_logger(__name__)

DEFAULT_TUTOR_PROMPT = """You are an expert English language tutor helping a student learn English from video content.
You can:
- Answer questions about vocabulary, grammar, and expressions in the video
- Explain cultural context and idioms
- Provide examples and practice suggestions
- Help the student understand difficult passages

Always be helpful, patient, and encouraging. Use simple language appropriate for the student's level when explaining concepts.
If you don't know something, admit it honestly rather than making up information."""


class ChatService:
    """Service for chat-based LLM interactions (AI tutor)."""

    def __init__(self):
        self._model = None
        self._initialized = False

    def _ensure_model(self) -> None:
        """Lazy load the llama-cpp-python model."""
        if self._initialized:
            return

        model_path = LLM_MODEL_PATH / settings.DEFAULT_MODEL
        if not model_path.exists():
            raise RuntimeError(
                f"LLM model not found at {model_path}. "
                f"Please download Qwen3.5-2B-Q4_K_M.gguf to {model_path}"
            )

        import os

        env_gpu_layers = os.getenv("LLM_GPU_LAYERS", settings.LLM_GPU_LAYERS)
        config = get_llama_config(str(model_path), env_gpu_layers, model_size="2B")

        from llama_cpp import Llama

        logger.info(f"Loading LLM model for chat from {model_path}")
        logger.info(
            f"Chat LLM Config: n_gpu_layers={config['n_gpu_layers']}, backend={config['backend']}"
        )

        n_ctx = getattr(settings, "LLM_CONTEXT_SIZE", 4096)
        n_threads = getattr(settings, "LLM_THREADS", 4)

        self._model = Llama(
            model_path=str(model_path),
            chat_template_kwargs={
                "enable_thinking": False
            },
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_gpu_layers=config["n_gpu_layers"],
            verbose=config["verbose"],
        )
        self._initialized = True
        logger.info("Chat LLM model loaded successfully")

    async def stream_chat(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming chat response.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt override

        Yields:
            Response tokens one at a time
        """
        self._ensure_model()

        system = system_prompt or DEFAULT_TUTOR_PROMPT
        full_messages = [{"role": "system", "content": system}] + messages

        def _stream_tokens():
            self._model.reset()
            response = self._model.create_chat_completion(
                messages=full_messages,
                max_tokens=4096,
                temperature=0.7,
                top_p=0.9,
                repeat_penalty=1.1,
                stream=True,
            )
            for chunk in response:
                delta = chunk["choices"][0]["delta"]
                if "content" in delta:
                    yield delta["content"]

        for token in await asyncio.to_thread(_stream_tokens):
            yield token

    async def shutdown(self) -> None:
        """Cleanup model resources."""
        if self._model is not None:
            del self._model
            self._model = None
            self._initialized = False
            logger.info("Chat LLM model unloaded")


chat_service = ChatService()