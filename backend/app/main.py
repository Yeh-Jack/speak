"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.api.v1.router import api_router
from app.core.config import DATA_DIR, DATABASE_URL, FRONTEND_DIST, settings
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
cors_origins = [o.strip() for o in settings.CORS_ALLOW_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Serve frontend index.html or return API info."""
    if FRONTEND_DIST.exists():
        from fastapi.responses import FileResponse
        index_path = FRONTEND_DIST / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
    return {
        "message": "Welcome to English Learning API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.get("/config.js")
async def frontend_config(request: Request):
    """Return runtime config for frontend."""
    # Detect protocol from request, fallback to BACKEND_URL setting
    protocol = "https" if request.url.scheme == "https" else "http"
    host = request.headers.get("host", settings.BACKEND_URL.split("://")[-1] if "://" in settings.BACKEND_URL else f"{settings.BACKEND_HOST}:8080")
    api_url = f"{protocol}://{host}"
    content = f"window.__API_URL__ = '{api_url}';"
    return Response(content=content, media_type="application/javascript")


# Mount frontend static files (if dist exists)
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
