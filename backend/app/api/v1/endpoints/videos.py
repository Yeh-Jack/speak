"""Video endpoints with full processing pipeline."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
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
from app.schemas.transcript import TranscriptUpload
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
    3. Generates dual transcripts (YouTube subtitles + Whisper)
    4. Extracts audio per chunk (mp3 format)
    5. Generates study plan using Whisper transcript (LLM)

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
        await db.commit()
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
        await db.commit()
        video = await video_repo.get_by_id(video.id)
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
    """Delete a video and all associated files."""
    repo = VideoRepository(db)
    video = await repo.get_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video_id_str = str(video_id)

    for ext in ["webm", "mp4"]:
        video_file = DATA_DIR / "videos" / f"{video_id_str}.{ext}"
        if video_file.exists():
            video_file.unlink()

    for lang in ["en", "zh", "ja", "es", "fr", "de"]:
        for ext in ["json3", "vtt", "srt", "ass", "lrc"]:
            subtitle_file = DATA_DIR / "subtitles" / f"{video_id_str}.{lang}.{ext}"
            if subtitle_file.exists():
                subtitle_file.unlink()

    transcript_file = DATA_DIR / "transcripts" / f"{video_id_str}.json"
    if transcript_file.exists():
        transcript_file.unlink()

    for audio_ext in ["mp3", "wav", "m4a", "ogg"]:
        audio_file = DATA_DIR / "audios" / f"{video_id_str}.{audio_ext}"
        if audio_file.exists():
            audio_file.unlink()

    await repo.delete(video_id)


@router.get("/{video_id}/chunks", response_model=list[VideoChunk])
async def get_video_chunks(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all chunks for a video."""
    chunk_repo = ChunkRepository(db)
    return await chunk_repo.get_by_video_id(video_id)


@router.get("/{video_id}/chunks/{chunk_index}/audio")
async def get_chunk_audio(
    video_id: UUID,
    chunk_index: int,
    db: AsyncSession = Depends(get_db),
):
    """Get audio file for a specific chunk as MP3.

    Args:
        video_id: Video UUID
        chunk_index: Index of the chunk

    Returns:
        MP3 audio file for the chunk
    """
    video_repo = VideoRepository(db)
    video = await video_repo.get_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    audio_path = DATA_DIR / "audios" / str(video_id) / f"chunk_{chunk_index}.mp3"
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail=f"Audio for chunk {chunk_index} not found")

    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename=f"chunk_{chunk_index}.mp3",
    )


@router.get("/{video_id}/transcripts/{transcript_type}")
async def get_video_transcript(
    video_id: UUID,
    transcript_type: str,
    db: AsyncSession = Depends(get_db),
):
    """Get transcript for a video.

    Args:
        video_id: Video UUID
        transcript_type: 'user', 'youtube_author', 'youtube_auto', or 'whisper'

    Returns:
        Transcript JSON
    """
    if transcript_type not in ("user", "youtube_author", "youtube_auto", "whisper"):
        raise HTTPException(
            status_code=400,
            detail="transcript_type must be 'user', 'youtube_author', 'youtube_auto', or 'whisper'",
        )

    transcript_repo = TranscriptRepository(db)
    transcript = await transcript_repo.get_by_video_and_source(video_id, transcript_type)
    if not transcript:
        raise HTTPException(status_code=404, detail=f"{transcript_type} transcript not found")

    return {
        "video_id": str(video_id),
        "source": transcript.source,
        "language": transcript.language,
        "segments": transcript.segments,
    }


@router.post("/{video_id}/transcripts/user")
async def upload_user_transcript(
    video_id: UUID,
    transcript_data: TranscriptUpload,
    db: AsyncSession = Depends(get_db),
):
    """Upload user-provided subtitles for a video.

    User-uploaded subtitles have the highest priority and will be used
    for study plan generation over Whisper or YouTube subtitles.

    Args:
        video_id: Video UUID
        transcript_data: User subtitle content with segments

    Returns:
        Created transcript info
    """
    video_repo = VideoRepository(db)
    video = await video_repo.get_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    transcript_repo = TranscriptRepository(db)

    existing = await transcript_repo.get_by_video_and_source(video_id, "user")
    if existing:
        existing.segments = transcript_data.segments
        existing.language = transcript_data.language
        await transcript_repo.save(existing)
        transcript = existing
    else:
        transcript = await transcript_repo.create(
            video_id,
            {
                "source": "user",
                "segments": transcript_data.segments,
                "language": transcript_data.language,
            },
        )

    return {
        "video_id": str(video_id),
        "source": transcript.source,
        "language": transcript.language,
        "segments_count": len(transcript.segments) if transcript.segments else 0,
        "message": "User transcript uploaded successfully. It will be used for study plan generation.",
    }
