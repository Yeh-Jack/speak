"""Video chunk repository."""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import VideoChunk
from app.repositories.base import BaseRepository


class ChunkRepository(BaseRepository[VideoChunk]):
    """Repository for VideoChunk model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, VideoChunk)

    async def get_by_video_id(self, video_id: UUID) -> list[VideoChunk]:
        """Get all chunks for a video."""
        result = await self.session.execute(
            select(VideoChunk)
            .where(VideoChunk.video_id == video_id)
            .order_by(VideoChunk.chunk_index)
        )
        return list(result.scalars().all())

    async def get_by_video_and_index(self, video_id: UUID, chunk_index: int) -> VideoChunk | None:
        """Get a specific chunk by video ID and index."""
        result = await self.session.execute(
            select(VideoChunk).where(
                VideoChunk.video_id == video_id, VideoChunk.chunk_index == chunk_index
            )
        )
        return result.scalar_one_or_none()

    async def delete_by_video_id(self, video_id: UUID) -> int:
        """Delete all chunks for a video and return count."""
        result = await self.session.execute(
            delete(VideoChunk).where(VideoChunk.video_id == video_id)
        )
        await self.session.flush()
        return result.rowcount

    async def create_many(self, chunks: list[VideoChunk]) -> list[VideoChunk]:
        """Create multiple chunks."""
        self.session.add_all(chunks)
        await self.session.flush()
        return chunks
