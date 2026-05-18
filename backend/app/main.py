"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.api.v1.router import api_router
from app.core.config import DATA_DIR, DATABASE_URL, settings
from app.core.logging import setup_logging, get_logger, is_verbose

setup_logging(
    log_level=settings.LOG_LEVEL,
    verbose=is_verbose(),
)
logger = get_logger(__name__)


def _ensure_data_directories() -> None:
    """Ensure all data storage directories exist."""
    subdirs = ["db", "videos", "subtitles", "transcripts", "audios", "models"]
    for subdir in subdirs:
        dir_path = DATA_DIR / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Data directory ensured: {dir_path}")


async def _ensure_database() -> None:
    """Ensure database exists and has tables created via SQLAlchemy."""
    from app.db.base import Base
    import app.models  # noqa: F401 - Import to register models with Base.metadata

    engine = create_async_engine(DATABASE_URL, echo=False, future=True)

    async with engine.connect() as conn:
        await conn.execute(text("PRAGMA foreign_keys = ON"))
        await conn.execute(text("PRAGMA journal_mode = WAL"))

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    logger.info(f"Database ensured: {DATA_DIR}/db/learning.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info("Starting up English Learning API")

    # Ensure data directories exist
    _ensure_data_directories()

    # Ensure database exists with tables
    await _ensure_database()

    try:
        yield
    except Exception as e:
        logger.error(f"Application error during lifespan: {e}", exc_info=True)
        raise
    finally:
        # Shutdown - always executes even if an exception occurred
        logger.info("Shutting down English Learning API")


# Create FastAPI app
app = FastAPI(
    title="English Learning API",
    description="AI-powered English education platform API",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers (courses and videos)
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to English Learning API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
