"""Video endpoints with full processing pipeline."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import DATA_DIR
from app.repositories import (
    ChunkRepository,
    StudyPlanRepository,
    TranscriptRepository,
    VideoRepository,
)
from app.schemas.video import (
    Video,
    VideoChunk,
    VideoCreate,
    VideoInfoResponse,
    VideoUpdate,
    VideoResponse,
    ProcessingTimings,
)
from app.services.video_service import VideoService
from app.services.download_service import DownloadService

router = APIRouter()


def get_video_service(db: AsyncSession) -> VideoService:
    """Dependency for VideoService."""
    return VideoService(
        video_repo=VideoRepository(db),
        chunk_repo=ChunkRepository(db),
        transcript_repo=TranscriptRepository(db),
        study_plan_repo=StudyPlanRepository(db),
        storage_dir=DATA_DIR,
    )


@router.get("", response_model=list[Video])
async def list_videos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all videos."""
    repo = VideoRepository(db)
    return await repo.get_all(skip=skip, limit=limit)


@router.get("/{video_id}", response_model=Video)
async def get_video(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a video by ID."""
    repo = VideoRepository(db)
    video = await repo.get_with_chunks(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.post("/info", response_model=VideoInfoResponse)
async def get_video_info(
    video_data: VideoCreate,
):
    """Get metadata of a video from YouTube URL without DB operations."""
    download_service = DownloadService(DATA_DIR)
    try:
        info = await download_service.get_video_info(video_data.youtube_url)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to get video info: {e}")

    return VideoInfoResponse(
        youtube_url=video_data.youtube_url,
        title=info.get("title"),
        description=info.get("description"),
        duration=info.get("duration"),
        thumbnail=info.get("thumbnail"),
        uploader=info.get("uploader"),
        upload_date=info.get("upload_date"),
        view_count=info.get("view_count"),
        like_count=info.get("like_count"),
        categories=info.get("categories"),
        tags=info.get("tags"),
        language=info.get("language"),
        subtitles=info.get("subtitles", []),
        automatic_captions=info.get("automatic_captions", []),
        available_formats=info.get("available_formats", []),
    )


@router.post("/youtube", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def create_video_from_youtube(
    video_data: VideoCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create video from YouTube URL and process through full pipeline.

    This endpoint:
    1. Downloads video from YouTube (yt-dlp)
    2. Creates chunks with Hybrid Dynamic sentence-snap (±30s)
    3. Generates transcript (YouTube subtitles first, Whisper fallback)
    4. Generates study plan (Phase 3 - LLM)

    Processing is immediate - endpoint waits for completion.
    For long videos, this may take several minutes.
    """
    video_repo = VideoRepository(db)

    existing = await video_repo.get_by_youtube_url(video_data.youtube_url)
    if existing:
        raise HTTPException(status_code=400, detail="Video from this URL already exists")

    download_service = DownloadService(DATA_DIR)
    try:
        info = await download_service.get_video_info(video_data.youtube_url)
        title = info.get("title", f"Video: {video_data.youtube_url[-20:]}")
    except Exception:
        title = f"Video: {video_data.youtube_url[-20:]}"

    from app.models.video import Video as VideoModel

    video = VideoModel(
        title=title,
        youtube_url=video_data.youtube_url,
        source_type="youtube",
        chunk_duration=video_data.chunk_duration,
        status="pending",
    )
    video = await video_repo.create(video)

    video_service = VideoService(
        video_repo=video_repo,
        chunk_repo=ChunkRepository(db),
        transcript_repo=TranscriptRepository(db),
        study_plan_repo=StudyPlanRepository(db),
        storage_dir=DATA_DIR,
    )

    try:
        video, timings = await video_service.process_video(video.id)
        return VideoResponse(
            video=video,
            chunks=video.chunks,
            timings=ProcessingTimings(**timings.to_dict()),
        )
    except Exception as e:
        video = await video_repo.get_by_id(video.id)
        raise HTTPException(
            status_code=500,
            detail=f"Video processing failed: {str(e)}. Video status: {video.status}",
        )


@router.post("/{video_id}/retry", response_model=VideoResponse)
async def retry_video_processing(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retry video processing from last checkpoint.

    Use this endpoint if a previous processing attempt failed.
    Processing resumes from the last successful state.
    """
    video_repo = VideoRepository(db)
    video = await video_repo.get_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.status == "ready":
        return VideoResponse(
            video=video,
            chunks=video.chunks,
            timings=ProcessingTimings(),
        )

    video_service = VideoService(
        video_repo=video_repo,
        chunk_repo=ChunkRepository(db),
        transcript_repo=TranscriptRepository(db),
        study_plan_repo=StudyPlanRepository(db),
        storage_dir=DATA_DIR,
    )

    try:
        video, timings = await video_service.retry_video(video_id)
        return VideoResponse(
            video=video,
            chunks=video.chunks,
            timings=ProcessingTimings(**timings.to_dict()),
        )
    except Exception as e:
        video = await video_repo.get_by_id(video.id)
        raise HTTPException(
            status_code=500,
            detail=f"Video retry failed: {str(e)}. Video status: {video.status}",
        )

    try:
        video = await video_service.retry_video(video_id)
        return video
    except Exception as e:
        video = await video_repo.get_by_id(video_id)
        raise HTTPException(
            status_code=500,
            detail=f"Video retry failed: {str(e)}. Video status: {video.status}",
        )


@router.patch("/{video_id}", response_model=Video)
async def update_video(
    video_id: UUID,
    video_data: VideoUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a video."""
    repo = VideoRepository(db)
    video = await repo.get_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    update_data = video_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(video, key, value)

    return await repo.save(video)


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a video."""
    repo = VideoRepository(db)
    success = await repo.delete(video_id)
    if not success:
        raise HTTPException(status_code=404, detail="Video not found")


@router.get("/{video_id}/chunks", response_model=list[VideoChunk])
async def get_video_chunks(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all chunks for a video."""
    chunk_repo = ChunkRepository(db)
    return await chunk_repo.get_by_video_id(video_id)
