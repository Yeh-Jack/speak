"""Database session management."""

from sqlalchemy import text, event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import DATABASE_URL, settings
from app.core.logging import get_logger, is_verbose

logger = get_logger(__name__)

_engine_options = {"future": True}
if is_verbose():
    _engine_options["echo"] = True

engine = create_async_engine(DATABASE_URL, **_engine_options)


async def init_sqlite_pragmas():
    """Initialize SQLite pragmas for better performance and foreign key support."""
    async with engine.connect() as conn:
        await conn.execute(text("PRAGMA foreign_keys = ON"))
        await conn.execute(text("PRAGMA journal_mode = WAL"))


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


@event.listens_for(engine.sync_engine, "before_cursor_execute")
def log_query(conn, cursor, statement, parameters, context, executemany):
    """Log SQL queries at debug level before execution."""
    logger.debug(f"SQL: {statement}")
    if parameters:
        logger.debug(f"Params: {parameters}")
