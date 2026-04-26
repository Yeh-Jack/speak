"""Hybrid Dynamic chunking service with ±30s sentence boundary snap."""

import logging
from dataclasses import dataclass
from typing import List
from app.services.exceptions import ChunkingError

logger = logging.getLogger(__name__)


@dataclass
class ChunkingConfig:
    """Configuration for Hybrid Dynamic chunking."""

    default_duration: int = 300
    min_duration: int = 60
    max_duration: int = 600
    search_window: float = 30.0


@dataclass
class VideoChunk:
    """A virtual video chunk with sentence-snapped timestamps."""

    index: int
    start_time: float
    end_time: float
    duration: float


class ChunkingService:
    """Hybrid Dynamic chunking with sentence-aware boundaries.

    Algorithm:
    1. Calculate ideal 5-min positions: (0:00-5:00), (5:00-10:00), etc.
    2. For each ideal boundary, search ±30s for nearest sentence-ending punctuation
    3. Snap chunk end to the sentence boundary if found within window
    """

    SENTENCE_PUNCTUATION = {".", "!", "?"}
    SEARCH_WINDOW = 30.0

    def __init__(self, config: ChunkingConfig | None = None):
        self.config = config or ChunkingConfig()

    def _ends_with_sentence(self, text: str) -> bool:
        """Check if text ends with sentence-ending punctuation."""
        if not text:
            return False
        return text.strip()[-1] in ChunkingService.SENTENCE_PUNCTUATION

    def _find_sentence_boundary(
        self,
        target_time: float,
        transcript: List[dict],
        chunk_start: float,
        video_duration: float,
    ) -> float:
        """Find nearest sentence boundary within ±30s of target_time.

        Args:
            target_time: Ideal boundary time in seconds
            transcript: List of transcript entries with start, end, text
            chunk_start: Start of current chunk to limit backward search
            video_duration: Total video duration to detect last chunk

        Returns:
            Adjusted boundary time snapped to nearest sentence, or target_time if not found
        """
        is_last_chunk = target_time >= video_duration
        min_search = max(chunk_start, target_time - ChunkingService.SEARCH_WINDOW)
        max_search = target_time + ChunkingService.SEARCH_WINDOW

        candidates = []
        for entry in transcript:
            entry_start = entry.get("start", 0.0)
            if entry_start < min_search:
                continue
            if entry_start > max_search:
                break
            text = entry.get("text", "")
            if text and self._ends_with_sentence(text):
                distance = abs(entry_start - target_time)
                candidates.append((distance, entry_start))

        if candidates:
            candidates.sort(key=lambda x: (x[0], x[1]))
            return candidates[0][1]

        logger.debug(f"No sentence boundary found near {target_time}, using ideal position")
        return target_time

    async def create_chunks(
        self, video_duration: float, transcript: List[dict], chunk_duration: int | None = None
    ) -> List[VideoChunk]:
        """Create chunks with Hybrid Dynamic sentence-snap.

        Args:
            video_duration: Total video duration in seconds
            transcript: List of transcript entries with start, end, text
            chunk_duration: Target chunk duration in seconds (default 300s = 5min)

        Returns:
            List of VideoChunk with snapped timestamps
        """
        if chunk_duration is None:
            chunk_duration = self.config.default_duration

        if video_duration <= 0:
            raise ChunkingError(f"Invalid video duration: {video_duration}")

        if not transcript:
            logger.warning("No transcript provided, using ideal chunk boundaries")
            return self._create_ideal_chunks(video_duration, chunk_duration)

        chunks = []
        current_time = 0.0
        chunk_index = 0

        while current_time < video_duration:
            ideal_end = min(current_time + chunk_duration, video_duration)

            actual_end = self._find_sentence_boundary(
                ideal_end, transcript, current_time, video_duration
            )

            if actual_end <= current_time:
                actual_end = ideal_end

            chunks.append(
                VideoChunk(
                    index=chunk_index,
                    start_time=current_time,
                    end_time=actual_end,
                    duration=actual_end - current_time,
                )
            )

            current_time = actual_end
            chunk_index += 1

            if chunk_index > 1000:
                logger.warning("Chunk limit reached, truncating video")
                break

        logger.info(f"Created {len(chunks)} chunks for video duration {video_duration}")
        return chunks

    def _create_ideal_chunks(self, video_duration: float, chunk_duration: int) -> List[VideoChunk]:
        """Create ideal chunks without sentence snap (fallback when no transcript)."""
        chunks = []
        current_time = 0.0
        chunk_index = 0

        while current_time < video_duration:
            end_time = min(current_time + chunk_duration, video_duration)
            chunks.append(
                VideoChunk(
                    index=chunk_index,
                    start_time=current_time,
                    end_time=end_time,
                    duration=end_time - current_time,
                )
            )
            current_time = end_time
            chunk_index += 1

        return chunks
