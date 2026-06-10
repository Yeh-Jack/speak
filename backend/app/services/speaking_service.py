"""Speaking practice service for character impersonation mode."""

import asyncio
import subprocess
from pathlib import Path
from typing import Optional

from app.core.config import DATA_DIR
from app.core.logging import get_logger

logger = get_logger(__name__)


class SpeakingService:
    """Service for speaking practice with audio comparison."""

    def __init__(self, storage_dir: Path = DATA_DIR):
        self.storage_dir = storage_dir
        self.recordings_dir = storage_dir / "recordings"
        self.recordings_dir.mkdir(parents=True, exist_ok=True)

    async def extract_audio_segment(
        self,
        video_path: Path,
        start_time: float,
        end_time: float,
        output_path: Path | None = None,
    ) -> Path:
        """Extract audio segment from video for a specific time range.

        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            end_time: End time in seconds
            output_path: Optional output path (generated if not provided)

        Returns:
            Path to extracted audio file (WAV, 16kHz mono)
        """
        if output_path is None:
            output_path = self.recordings_dir / f"segment_{start_time}_{end_time}.wav"

        duration = end_time - start_time

        cmd = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-ss",
            str(start_time),
            "-t",
            str(duration),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-y",
            str(output_path),
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            logger.error(f"FFmpeg audio extraction failed: {stderr.decode()}")
            raise ValueError(f"FFmpeg audio extraction failed: {stderr.decode()}")

        return output_path

    async def transcribe_audio(self, audio_path: Path, language: str = "en") -> str:
        """Transcribe audio file using Whisper.

        Args:
            audio_path: Path to audio file
            language: Language code (default: en)

        Returns:
            Transcribed text
        """
        try:
            from faster_whisper import WhisperModel

            model = WhisperModel(
                "base",
                device="cpu",
                compute_type="int8",
                cpu_threads=4,
            )

            segments, info = await asyncio.to_thread(
                lambda: model.transcribe(
                    str(audio_path),
                    language=language,
                    word_timestamps=False,
                ),
            )

            text = " ".join(segment.text.strip() for segment in segments)
            return text.strip()
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            raise ValueError(f"Transcription failed: {e}")

    def calculate_similarity(self, original_text: str, user_text: str) -> float:
        """Calculate simple text similarity between two strings.

        Uses word overlap ratio as a simple similarity metric.

        Args:
            original_text: Original transcript text
            user_text: User's transcript text

        Returns:
            Similarity score between 0.0 and 1.0
        """
        original_words = set(original_text.lower().split())
        user_words = set(user_text.lower().split())

        if not original_words or not user_words:
            return 0.0

        intersection = original_words & user_words
        union = original_words | user_words

        return len(intersection) / len(union)

    async def compare_recordings(
        self,
        original_audio_path: Path,
        user_audio_path: Path,
        language: str = "en",
    ) -> dict:
        """Compare user's recording with original using Whisper.

        Args:
            original_audio_path: Path to original audio
            user_audio_path: Path to user's recording
            language: Whisper language code (always 'en' for English videos)

        Returns:
            Dict with similarity_score, feedback_en, feedback_zh
        """
        original_text = await self.transcribe_audio(original_audio_path, language)
        user_text = await self.transcribe_audio(user_audio_path, language)

        similarity = self.calculate_similarity(original_text, user_text)

        feedback = self._generate_feedback(original_text, user_text, similarity)

        return {
            "original_text": original_text,
            "user_text": user_text,
            "similarity_score": round(similarity, 2),
            **feedback,
        }

    def _generate_feedback(
        self, original_text: str, user_text: str, similarity: float
    ) -> dict:
        """Generate feedback based on comparison.

        Args:
            original_text: Original transcript
            user_text: User's transcript
            similarity: Similarity score

        Returns:
            Dict with feedback_en and feedback_zh
        """
        if similarity >= 0.8:
            return {
                "feedback_en": "Excellent! Your pronunciation is very close to the original. Keep practicing!",
                "feedback_zh": "太棒了！您的發音非常接近原文。繼續保持！"
            }
        elif similarity >= 0.6:
            return {
                "feedback_en": "Good effort! Try to match the rhythm and emphasis of the original more closely.",
                "feedback_zh": "很好！請嘗試更貼近原文的節奏和語調。"
            }
        elif similarity >= 0.4:
            return {
                "feedback_en": "Nice try! Focus on the key words and try to say them more clearly.",
                "feedback_zh": "不錯！請專注於關鍵單詞並嘗試說得更清晰。"
            }
        else:
            return {
                "feedback_en": "Keep practicing! Listen to the original again and try to repeat each phrase carefully.",
                "feedback_zh": "繼續加油！請再次聆聽原文並仔細重複每個句子。"
            }

    async def save_recording(
        self, audio_data: bytes, video_id: str, segment_start: float
    ) -> Path:
        """Save user's recording to disk.

        Args:
            audio_data: Raw audio bytes (WebM/Opus)
            video_id: Video ID
            segment_start: Start time of segment

        Returns:
            Path to saved recording
        """
        output_path = self.recordings_dir / f"{video_id}_{segment_start}.webm"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(audio_data)

        return output_path