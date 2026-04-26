"""Study plan repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.study_plan import StudyPlan
from app.repositories.base import BaseRepository


class StudyPlanRepository(BaseRepository[StudyPlan]):
    """Repository for StudyPlan model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, StudyPlan)

    async def get_by_video_id(self, video_id: UUID) -> StudyPlan | None:
        """Get study plan for a video (overall plan, chunk_index is null)."""
        result = await self.session.execute(
            select(StudyPlan).where(StudyPlan.video_id == video_id, StudyPlan.chunk_index.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_video_and_chunk(self, video_id: UUID, chunk_index: int) -> StudyPlan | None:
        """Get study plan for a specific chunk."""
        result = await self.session.execute(
            select(StudyPlan).where(
                StudyPlan.video_id == video_id, StudyPlan.chunk_index == chunk_index
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_video_id(self, video_id: UUID) -> list[StudyPlan]:
        """Get all study plans for a video (including chunk-specific)."""
        result = await self.session.execute(
            select(StudyPlan).where(StudyPlan.video_id == video_id).order_by(StudyPlan.chunk_index)
        )
        return list(result.scalars().all())
