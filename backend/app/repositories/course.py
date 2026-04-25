"""Course repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import Course, CourseVideo
from app.repositories.base import BaseRepository


class CourseRepository(BaseRepository[Course]):
    """Repository for Course model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Course)

    async def get_with_videos(self, id: UUID) -> Course | None:
        """Get course with its videos."""
        result = await self.session.execute(
            select(Course)
            .where(Course.id == id)
            .options(selectinload(Course.course_videos).selectinload(CourseVideo.video))
        )
        return result.scalar_one_or_none()

    async def get_by_status(self, status: str) -> list[Course]:
        """Get courses by status."""
        result = await self.session.execute(select(Course).where(Course.status == status))
        return list(result.scalars().all())


class CourseVideoRepository(BaseRepository[CourseVideo]):
    """Repository for CourseVideo model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, CourseVideo)

    async def get_by_course_id(self, course_id: UUID) -> list[CourseVideo]:
        """Get all course videos for a course."""
        result = await self.session.execute(
            select(CourseVideo)
            .where(CourseVideo.course_id == course_id)
            .order_by(CourseVideo.order_index)
        )
        return list(result.scalars().all())

    async def get_by_course_and_video(self, course_id: UUID, video_id: UUID) -> CourseVideo | None:
        """Get a specific course video."""
        result = await self.session.execute(
            select(CourseVideo).where(
                CourseVideo.course_id == course_id, CourseVideo.video_id == video_id
            )
        )
        return result.scalar_one_or_none()

    async def delete_by_course_id(self, course_id: UUID) -> int:
        """Delete all course videos for a course."""
        from sqlalchemy import delete

        result = await self.session.execute(
            delete(CourseVideo).where(CourseVideo.course_id == course_id)
        )
        await self.session.flush()
        return result.rowcount
