"""Video repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.video import Video
from app.repositories.base import BaseRepository


class VideoRepository(BaseRepository[Video]):
    """Repository for Video model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Video)

    async def get_with_chunks(self, id: UUID) -> Video | None:
        """Get video with its chunks."""
        result = await self.session.execute(
            select(Video).where(Video.id == id).options(selectinload(Video.chunks))
        )
        return result.scalar_one_or_none()

    async def get_with_relations(self, id: UUID) -> Video | None:
        """Get video with all relations."""
        result = await self.session.execute(
            select(Video)
            .where(Video.id == id)
            .options(
                selectinload(Video.chunks),
                selectinload(Video.transcripts),
                selectinload(Video.study_plans),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_youtube_url(self, youtube_url: str) -> Video | None:
        """Get video by YouTube URL."""
        result = await self.session.execute(select(Video).where(Video.youtube_url == youtube_url))
        return result.scalar_one_or_none()

    async def get_pending(self) -> list[Video]:
        """Get all pending videos."""
        result = await self.session.execute(select(Video).where(Video.status == "pending"))
        return list(result.scalars().all())

    async def get_by_status(self, status: str) -> list[Video]:
        """Get videos by status."""
        result = await self.session.execute(select(Video).where(Video.status == status))
        return list(result.scalars().all())

    async def update_status(
        self, video_id: UUID, status: str, error_message: str | None = None
    ) -> Video | None:
        """Update video status and optionally error_message."""
        video = await self.get_by_id(video_id)
        if not video:
            return None
        video.status = status
        if error_message is not None:
            video.error_message = error_message
        return await self.save(video)
