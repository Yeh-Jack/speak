"""Video endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories import ChunkRepository, VideoRepository
from app.schemas.video import Video, VideoChunk, VideoCreate, VideoUpdate

router = APIRouter()


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


@router.post("", response_model=Video, status_code=status.HTTP_201_CREATED)
async def create_video(
    video_data: VideoCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new video from YouTube URL.

    Note: This is a placeholder endpoint. Full implementation will:
    1. Download video from YouTube
    2. Create chunks with sentence snap
    3. Generate transcript
    4. Generate study plan via LLM
    """
    repo = VideoRepository(db)
    existing = await repo.get_by_youtube_url(video_data.youtube_url)
    if existing:
        raise HTTPException(status_code=400, detail="Video already exists")

    from app.models.video import Video as VideoModel

    video = VideoModel(
        title="Pending: " + video_data.youtube_url[-20:],
        youtube_url=video_data.youtube_url,
        source_type="youtube",
        chunk_duration=video_data.chunk_duration,
        status="pending",
    )
    return await repo.create(video)


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
