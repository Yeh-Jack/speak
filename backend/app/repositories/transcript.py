"""Transcript repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transcript import Transcript
from app.repositories.base import BaseRepository


class TranscriptRepository(BaseRepository[Transcript]):
    """Repository for Transcript model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Transcript)

    async def get_by_video_id(self, video_id: UUID) -> Transcript | None:
        """Get a single transcript for a video (first one found)."""
        if isinstance(video_id, UUID):
            video_id = str(video_id)
        result = await self.session.execute(
            select(Transcript).where(Transcript.video_id == video_id)
        )
        return result.scalars().first()

    async def get_all_by_video_id(self, video_id: UUID) -> list[Transcript]:
        """Get all transcripts for a video."""
        if isinstance(video_id, UUID):
            video_id = str(video_id)
        result = await self.session.execute(
            select(Transcript).where(Transcript.video_id == video_id)
        )
        return list(result.scalars().all())

    async def get_by_video_and_source(self, video_id: UUID, source: str) -> Transcript | None:
        """Get transcript by video ID and source."""
        if isinstance(video_id, UUID):
            video_id = str(video_id)
        result = await self.session.execute(
            select(Transcript).where(Transcript.video_id == video_id, Transcript.source == source)
        )
        return result.scalars().first()

    async def create(self, video_id: UUID, transcript_data: dict) -> Transcript:
        """Create a transcript for a video."""
        transcript = Transcript(
            video_id=str(video_id),
            source=transcript_data.get("source", "youtube"),
            segments=transcript_data.get("segments", []),
            full_text=transcript_data.get("full_text"),
            language=transcript_data.get("language"),
        )
        self.session.add(transcript)
        await self.session.flush()
        await self.session.refresh(transcript)
        return transcript
