"""LLM Service using llama-cpp-python for Qwen3.5-2B study plan generation."""

import asyncio
import json
import time
from pathlib import Path
from typing import Any

from app.core.config import settings, LLM_MODEL_PATH
from app.core.logging import get_logger
from app.services.exceptions import StudyPlanError
from app.utils.gpu_utils import get_llama_config

logger = get_logger(__name__)


SYSTEM_PROMPT = """You are an expert English language teacher. Your role is to analyze video transcripts and create personalized study plans for English learners.

For each video, you will generate:
1. Learning objectives - what the learner should achieve
2. Vocabulary items - important words and phrases with definitions
3. Grammar points - key grammatical structures used in the video
4. Chunk study guides - detailed study material for each video segment
5. Estimated study time

Only output the JSON response, no explanatory text."""


class LLMService:
    """Service for LLM inference using llama-cpp-python."""

    def __init__(self, model_path: Path | None = None):
        """Initialize LLM service.

        Args:
            model_path: Path to GGUF model file. Defaults to configured model.
        """
        self.model_path = model_path or (LLM_MODEL_PATH / settings.DEFAULT_MODEL)
        self._model = None
        self._initialized = False

    def _ensure_model(self) -> None:
        """Lazy load the llama-cpp-python model."""
        if self._initialized:
            return

        if not self.model_path.exists():
            raise StudyPlanError(
                f"LLM model not found at {self.model_path}. "
                f"Please download Qwen3.5-2B-Q4_K_M.gguf to {self.model_path}"
            )

        import os

        env_gpu_layers = os.getenv("LLM_GPU_LAYERS", settings.LLM_GPU_LAYERS)
        config = get_llama_config(str(self.model_path), env_gpu_layers, model_size="2B")

        from llama_cpp import Llama

        logger.info(f"Loading LLM model from {self.model_path}")
        logger.info(
            f"LLM Config: n_gpu_layers={config['n_gpu_layers']}, backend={config['backend']}"
        )

        n_ctx = getattr(settings, "LLM_CONTEXT_SIZE", 4096)
        n_threads = getattr(settings, "LLM_THREADS", 4)

        self._model = Llama(
            model_path=str(self.model_path),
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_gpu_layers=config["n_gpu_layers"],
            verbose=config["verbose"],
        )
        self._initialized = True
        logger.info("LLM model loaded successfully")

    async def generate_study_plan(
        self,
        transcript: dict,
        video_title: str,
        video_duration: float,
    ) -> tuple[dict[str, Any], dict[str, float]]:
        """Generate a study plan from transcript using LLM.

        Args:
            transcript: Transcript dict with 'segments' list
            video_title: Title of the video
            video_duration: Duration in seconds

        Returns:
            Tuple of (study_plan dict, timing dict with llm_init_seconds and llm_inference_seconds)

        Raises:
            StudyPlanError: If LLM generation fails
        """
        timings = {"llm_init_seconds": 0.0, "llm_inference_seconds": 0.0}

        init_start = time.perf_counter()
        self._ensure_model()
        timings["llm_init_seconds"] = time.perf_counter() - init_start

        transcript_text = self._format_transcript_for_prompt(transcript)

        user_prompt = f"""Based on the following video transcript, generate a personalized English study plan.

Video Title: {video_title}
Video Duration: {int(video_duration)} seconds
Transcript (first 8000 chars): {transcript_text[:8000]}

Generate a study plan in the following JSON format:
{{
    "title": "Descriptive study plan title",
    "overall_difficulty": "beginner|intermediate|advanced",
    "estimated_time": "e.g., 45 minutes",
    "vocabulary": [
        {{
            "word": "important word or phrase",
            "definition": "clear English definition",
            "example": "example sentence using the word",
            "difficulty": "easy|medium|hard"
        }}
    ],
    "grammar": [
        {{
            "pattern": "grammatical structure",
            "explanation": "how it's used in this context",
            "examples": ["example 1", "example 2"]
        }}
    ],
    "chunks": [
        {{
            "chunk_index": 0,
            "time_range": "0:00-5:00",
            "summary": "brief summary of this segment",
            "key_points": ["point 1", "point 2"],
            "practice_suggestions": ["suggestion 1", "suggestion 2"]
        }}
    ],
    "notes": "Additional pedagogical notes for the learner"
}}

Only return the JSON, no other text."""

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        inference_start = time.perf_counter()
        try:
            response = await self._generate_response(messages)
            study_plan = self._parse_json_response(response)
            validated_plan = self._validate_study_plan(study_plan, video_title, video_duration)
            timings["llm_inference_seconds"] = time.perf_counter() - inference_start
            logger.info(
                f"[LLM Timing] init={timings['llm_init_seconds']:.2f}s, "
                f"inference={timings['llm_inference_seconds']:.2f}s"
            )
            return validated_plan, timings
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            logger.warning(f"Raw LLM response (first 500 chars): {response[:500]}")
            raise StudyPlanError(f"Failed to parse study plan from LLM: {e}")
        except Exception as e:
            logger.error(f"LLM study plan generation failed: {e}")
            raise StudyPlanError(f"Study plan generation failed: {e}")

    def _format_transcript_for_prompt(self, transcript: dict) -> str:
        """Format transcript segments into a text string."""
        if hasattr(transcript, "segments"):
            segments = transcript.segments or []
        else:
            segments = transcript.get("segments", [])
        if not segments:
            return "No transcript available."

        lines = []
        for seg in segments:
            start = seg.get("start", 0)
            text = seg.get("text", "").strip()
            if text:
                minutes = int(start // 60)
                seconds = int(start % 60)
                lines.append(f"[{minutes:02d}:{seconds:02d}] {text}")

        return "\n".join(lines)

    async def _generate_response(self, messages: list) -> str:
        """Generate LLM response using chat completion."""

        def _call_llm():
            self._model.reset()
            response = self._model.create_chat_completion(
                messages=messages,
                max_tokens=8192,
                temperature=0.3,
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["```", "```\n"],
            )
            return response["choices"][0]["message"]["content"].strip()

        return await asyncio.to_thread(_call_llm)

    def _parse_json_response(self, response: str) -> dict:
        """Extract and parse JSON from LLM response."""
        first_brace = response.find("{")
        if first_brace >= 0:
            response = response[first_brace:]
        else:
            raise StudyPlanError("No JSON found in LLM response")

        if not response or not response.strip():
            raise StudyPlanError("Empty response from LLM")

        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]

        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        if not response:
            raise StudyPlanError("Empty response after stripping markdown fences")

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            last_brace = response.rfind("}") + 1
            if last_brace > 0:
                json_str = response[:last_brace]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            logger.warning(f"Failed to parse LLM response: {e}, response length: {len(response)}")
            logger.warning(f"Raw LLM response (first 1000 chars): {response[:1000]}")
            logger.warning(f"Raw LLM response (last 500 chars): {response[-500:]}")
            raise

    def _validate_study_plan(self, plan: dict, video_title: str, video_duration: float) -> dict:
        """Validate and fill in missing fields with defaults."""
        validated = {
            "title": plan.get("title", f"Study Plan: {video_title}"),
            "overall_difficulty": plan.get("overall_difficulty", "intermediate"),
            "estimated_time": plan.get("estimated_time", "30 minutes"),
            "vocabulary": plan.get("vocabulary", []),
            "grammar": plan.get("grammar", []),
            "chunks": plan.get("chunks", []),
            "notes": plan.get("notes", ""),
        }
        return validated

    async def shutdown(self) -> None:
        """Cleanup model resources."""
        if self._model is not None:
            del self._model
            self._model = None
            self._initialized = False
            logger.info("LLM model unloaded")


llm_service = LLMService()
