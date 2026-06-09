"""Speaking practice endpoints for character impersonation."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import DATA_DIR
from app.models.video import Video
from app.repositories import VideoRepository, TranscriptRepository
from app.services.speaking_service import SpeakingService

router = APIRouter()


def get_speaking_service() -> SpeakingService:
    """Dependency for SpeakingService."""
    return SpeakingService(storage_dir=DATA_DIR)


@router.get("/videos/{video_id}/segments")
async def get_video_segments(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
    source: str = "whisper",
) -> dict:
    """Get transcript segments for a video suitable for speaking practice.

    Returns segments with start/end times and text that can be practiced.

    Args:
        video_id: Video UUID
        source: Transcript source - 'whisper', 'youtube_author', 'youtube_auto', or 'user'

    Returns:
        Dict with segments array
    """
    video_repo = VideoRepository(db)
    video = await video_repo.get_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    transcript_repo = TranscriptRepository(db)
    transcript = await transcript_repo.get_by_video_and_source(video_id, source)
    if not transcript or not transcript.segments:
        raise HTTPException(
            status_code=404,
            detail=f"No {source} transcript found for this video",
        )

    segments = [
        {
            "start": seg.get("start", 0),
            "end": seg.get("end", 0),
            "text": seg.get("text", ""),
            "speaker": seg.get("speaker"),
        }
        for seg in transcript.segments
        if seg.get("text")
    ]

    return {"segments": segments, "source": source}


@router.get("/videos/{video_id}/audio-segment")
async def get_audio_segment(
    video_id: UUID,
    start: float,
    end: float,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Extract audio segment from video for playback.

    Args:
        video_id: Video UUID
        start: Start time in seconds
        end: End time in seconds

    Returns:
        Audio file path info
    """
    video_repo = VideoRepository(db)
    video = await video_repo.get_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video_path = DATA_DIR / "videos" / f"{video_id}.webm"
    if not video_path.exists():
        video_path = DATA_DIR / "videos" / f"{video_id}.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    speaking_service = get_speaking_service()
    try:
        audio_path = await speaking_service.extract_audio_segment(
            video_path, start, end
        )
        return {
            "audio_path": str(audio_path),
            "start": start,
            "end": end,
        }
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/videos/{video_id}/compare")
async def compare_recording(
    video_id: UUID,
    start: float,
    end: float,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Compare user's recording with original audio.

    Args:
        video_id: Video UUID
        start: Segment start time
        end: Segment end time
        file: User's audio recording (WebM format)

    Returns:
        Comparison result with similarity score and feedback
    """
    video_repo = VideoRepository(db)
    video = await video_repo.get_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video_path = DATA_DIR / "videos" / f"{video_id}.webm"
    if not video_path.exists():
        video_path = DATA_DIR / "videos" / f"{video_id}.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    speaking_service = get_speaking_service()

    original_audio_path = await speaking_service.extract_audio_segment(
        video_path, start, end
    )

    user_audio_data = await file.read()
    user_audio_path = await speaking_service.save_recording(
        user_audio_data, str(video_id), start
    )

    try:
        result = await speaking_service.compare_recordings(
            original_audio_path, user_audio_path
        )
        return {
            "video_id": str(video_id),
            "segment_start": start,
            "segment_end": end,
            **result,
        }
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if original_audio_path.exists():
            original_audio_path.unlink()
        if user_audio_path.exists():
            user_audio_path.unlink()