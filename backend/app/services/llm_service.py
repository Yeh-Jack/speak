"""LLM Service using llama-cpp-python for Qwen3.5-2B study plan generation."""

import asyncio
import json
import time
from pathlib import Path
from typing import Any, AsyncGenerator

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

IMPORTANT: All Chinese translations MUST be in TRADITIONAL Chinese (繁體中文) ONLY.
- Do NOT use Simplified Chinese (簡體中文)
- Do NOT mix in simplified characters
- Use 繁體中文 characters only (如：學習、詞匯、影片，而不是 学习、词汇、电影)

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
            chat_template_kwargs={
                "enable_thinking": False
            },  # Disable thinking mode for Qwen models.
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
Transcript (first 4000 chars): {transcript_text[:4000]}

Generate a study plan in the following JSON format:
{{
    "title": "Descriptive study plan title",
    "title_zh": "描述性學習計劃標題（繁體中文）",
    "overall_difficulty": "beginner|intermediate|advanced",
    "overall_difficulty_zh": "初級|中級|高級",
    "estimated_time": "e.g., 45 minutes",
    "estimated_time_zh": "例如：45分鐘",
    "vocabulary": [
        {{
            "word": "important word or phrase",
            "word_zh": "重要單詞或片語（繁體中文）",
            "definition": "clear English definition",
            "definition_zh": "清晰的中文定義",
            "example": "example sentence using the word (from the video transcript when possible)",
            "example_zh": "使用該詞的例句（繁體中文）",
            "context": "the sentence from the video transcript where this word appears, showing real usage",
            "context_zh": "該單詞在影片字幕中出現的句子，展示真實用法（繁體中文）",
            "difficulty": "easy|medium|hard",
            "difficulty_zh": "簡單|中等|困難"
        }}
    ],
    "grammar": [
        {{
            "pattern": "grammatical structure",
            "pattern_zh": "語法結構（繁體中文）",
            "explanation": "how it's used in this context (English)",
            "explanation_zh": "在此語境中的用法（繁體中文）",
            "examples": ["sentence using the pattern", "another sentence using the pattern"],
            "examples_zh": ["使用該語法結構的例句（繁體中文）", "另一個使用該語法結構的例句（繁體中文）"]
        }}
    ],
    "chunks": [
        {{
            "chunk_index": 0,
            "time_range": "0:00-5:00",
            "summary": "brief summary of this segment",
            "summary_zh": "此片段的簡要摘要（繁體中文）",
            "key_points": ["point 1", "point 2"],
            "key_points_zh": ["要點1（繁體中文）", "要點2（繁體中文）"],
            "practice_suggestions": ["suggestion 1", "suggestion 2"],
            "practice_suggestions_zh": ["練習建議1（繁體中文）", "練習建議2（繁體中文）"]
        }}
    ],
    "notes": "Additional pedagogical notes for the learner",
    "notes_zh": "給學習者的額外教學筆記（繁體中文）"
}}

IMPORTANT: Keep the output concise to avoid truncation.
- vocabulary: Include ONLY 3 items maximum (choose the most important ones)
- grammar: Include ONLY 2 items maximum
- chunks: Include ONLY 1 chunk maximum (the first/most important one)

CRITICAL REQUIREMENTS:
1. Every text/string field in the JSON output MUST have a corresponding Chinese translation field with "_zh" suffix. This applies to ALL nested objects including vocabulary items, grammar items, and chunk objects. Do NOT omit any translation fields.
2. ALL Chinese translations MUST be in TRADITIONAL Chinese (繁體中文) ONLY. Do NOT use Simplified Chinese (簡體中文). Examples: use 學習 not 学习, 詞匯 not 词汇, 影片 not 电影.

Only return the JSON, no other text. Ensure the JSON is complete and valid. The JSON must be properly closed with all strings terminated."""

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

    async def stream_response(
        self,
        messages: list[dict],
    ) -> AsyncGenerator[str, None]:
        """Stream LLM response token by token.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Yields:
            Response tokens one at a time
        """
        self._ensure_model()

        def _stream_tokens():
            self._model.reset()
            response = self._model.create_chat_completion(
                messages=messages,
                max_tokens=8192,
                temperature=0.3,
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["```", "```\n"],
                stream=True,
            )
            for chunk in response:
                delta = chunk["choices"][0]["delta"]
                if "content" in delta:
                    yield delta["content"]

        for token in await asyncio.to_thread(_stream_tokens):
            yield token

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
            truncated_json = self._fix_truncated_json(response)
            if truncated_json:
                return truncated_json
            logger.warning(f"Failed to parse LLM response: {e}, response length: {len(response)}")
            logger.warning(f"Raw LLM response (first 1000 chars): {response[:1000]}")
            logger.warning(f"Raw LLM response (last 500 chars): {response[-500:]}")
            raise

    def _fix_truncated_json(self, response: str) -> dict | None:
        """Attempt to fix JSON truncated mid-string.

        When LLM output is cut off mid-string (e.g., "difficulty": "medium
        without closing quote), finds the last valid JSON boundary and truncates there.
        """
        msg = str(response)

        # Case 1: Odd number of quotes suggests an unclosed string
        quote_count = msg.count('"')
        if quote_count % 2 != 0:
            # Find the last unclosed quote
            last_quote = msg.rfind('"')
            if last_quote > len(msg) // 2:
                # Truncate at the unclosed quote
                truncated = msg[:last_quote]
                # Try to find a valid JSON end
                last_brace = truncated.rfind("}") + 1
                if last_brace > 0:
                    truncated = truncated[:last_brace]
                    try:
                        result = json.loads(truncated)
                        logger.info(f"Fixed truncated JSON by truncating at unclosed string (char {last_quote})")
                        return result
                    except json.JSONDecodeError:
                        pass

        # Case 2: Try to find the last complete object (look for },])
        last_valid_end = msg.rfind("}")
        if last_valid_end > 0:
            truncated = msg[:last_valid_end + 1]
            try:
                result = json.loads(truncated)
                logger.info(f"Fixed truncated JSON by truncating at last complete object (char {last_valid_end})")
                return result
            except json.JSONDecodeError:
                pass

        # Case 3: Look for last complete entry in arrays
        for search_str in [']}}', ']}', '"]', '}]']:
            last_idx = msg.rfind(search_str)
            if last_idx > len(msg) // 2:
                truncated = msg[:last_idx + len(search_str)]
                try:
                    result = json.loads(truncated)
                    logger.info(f"Fixed truncated JSON by truncating at '{search_str}' (char {last_idx})")
                    return result
                except json.JSONDecodeError:
                    pass

        return None

    def _validate_study_plan(self, plan: dict, video_title: str, video_duration: float) -> dict:
        """Validate and fill in missing fields with defaults."""
        vocabulary = []
        for item in plan.get("vocabulary", []):
            validated_item = {
                "word": item.get("word", ""),
                "word_zh": item.get("word_zh", ""),
                "definition": item.get("definition", ""),
                "definition_zh": item.get("definition_zh", ""),
                "example": item.get("example", ""),
                "example_zh": item.get("example_zh", ""),
                "context": item.get("context", ""),
                "context_zh": item.get("context_zh", ""),
                "difficulty": item.get("difficulty", "medium"),
                "difficulty_zh": item.get("difficulty_zh", "中等"),
            }
            vocabulary.append(validated_item)

        grammar = []
        for item in plan.get("grammar", []):
            validated_item = {
                "pattern": item.get("pattern", ""),
                "pattern_zh": item.get("pattern_zh", ""),
                "explanation": item.get("explanation", ""),
                "explanation_zh": item.get("explanation_zh", ""),
                "examples": item.get("examples", []),
                "examples_zh": item.get("examples_zh", []),
            }
            grammar.append(validated_item)

        chunks = []
        for item in plan.get("chunks", []):
            validated_item = {
                "chunk_index": item.get("chunk_index", 0),
                "time_range": item.get("time_range", ""),
                "summary": item.get("summary", ""),
                "summary_zh": item.get("summary_zh", ""),
                "key_points": item.get("key_points", []),
                "key_points_zh": item.get("key_points_zh", []),
                "practice_suggestions": item.get("practice_suggestions", []),
                "practice_suggestions_zh": item.get("practice_suggestions_zh", []),
            }
            chunks.append(validated_item)

        validated = {
            "title": plan.get("title", f"Study Plan: {video_title}"),
            "title_zh": plan.get("title_zh", ""),
            "overall_difficulty": plan.get("overall_difficulty", "intermediate"),
            "overall_difficulty_zh": plan.get("overall_difficulty_zh", "中級"),
            "estimated_time": plan.get("estimated_time", "30 minutes"),
            "estimated_time_zh": plan.get("estimated_time_zh", "30分鐘"),
            "vocabulary": vocabulary,
            "grammar": grammar,
            "chunks": chunks,
            "notes": plan.get("notes", ""),
            "notes_zh": plan.get("notes_zh", ""),
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
