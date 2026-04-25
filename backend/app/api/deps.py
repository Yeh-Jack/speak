"""Dependencies for API endpoints."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Get database session for dependency injection."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
