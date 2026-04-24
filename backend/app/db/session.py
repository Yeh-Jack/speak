"""Database session management."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

# Create async engine with SQLite-specific settings
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)


async def init_sqlite_pragmas():
    """Initialize SQLite pragmas for better performance and foreign key support."""
    async with engine.connect() as conn:
        # Enable foreign key constraints (SQLite disables them by default)
        await conn.execute(text("PRAGMA foreign_keys = ON"))
        # Use WAL mode for better concurrent access
        await conn.execute(text("PRAGMA journal_mode = WAL"))


# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db():
    """Get database session for dependency injection."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
