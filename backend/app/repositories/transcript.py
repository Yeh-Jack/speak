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
        """Get transcript for a video."""
        result = await self.session.execute(
            select(Transcript).where(Transcript.video_id == video_id)
        )
        return result.scalar_one_or_none()

    async def get_by_video_and_source(self, video_id: UUID, source: str) -> Transcript | None:
        """Get transcript by video ID and source."""
        result = await self.session.execute(
            select(Transcript).where(Transcript.video_id == video_id, Transcript.source == source)
        )
        return result.scalar_one_or_none()
