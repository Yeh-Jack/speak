"""Progress repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import StudyProgress
from app.repositories.base import BaseRepository


class ProgressRepository(BaseRepository[StudyProgress]):
    """Repository for StudyProgress model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, StudyProgress)

    async def get_by_video_and_chunk(
        self, video_id: UUID, chunk_index: int
    ) -> StudyProgress | None:
        """Get progress for a specific video chunk."""
        result = await self.session.execute(
            select(StudyProgress).where(
                StudyProgress.video_id == video_id, StudyProgress.chunk_index == chunk_index
            )
        )
        return result.scalar_one_or_none()

    async def get_by_video_id(self, video_id: UUID) -> list[StudyProgress]:
        """Get all progress for a video."""
        result = await self.session.execute(
            select(StudyProgress)
            .where(StudyProgress.video_id == video_id)
            .order_by(StudyProgress.chunk_index)
        )
        return list(result.scalars().all())

    async def get_completed_chunks(self, video_id: UUID) -> list[int]:
        """Get list of completed chunk indices for a video."""
        result = await self.session.execute(
            select(StudyProgress.chunk_index).where(
                StudyProgress.video_id == video_id, StudyProgress.completed.is_(True)
            )
        )
        return list(result.scalars().all())
