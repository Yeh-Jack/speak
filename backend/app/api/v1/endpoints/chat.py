"""Chat endpoints for AI tutor functionality."""

import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories import VideoRepository, TranscriptRepository
from app.schemas.chat import StreamChatRequest
from app.services.chat_service import chat_service

router = APIRouter()


@router.post("")
async def chat(
    request: StreamChatRequest,
    db: AsyncSession,
):
    """Streaming chat endpoint for AI tutor (SSE).

    Streams tokens as they are generated for real-time UI updates.
    Optionally contextualized by a video's transcript.
    """
    video_context = ""
    video_title = "the video"
    if request.video_id:
        video_repo = VideoRepository(db)
        video = await video_repo.get_by_id(request.video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        video_title = video.title

        transcript_repo = TranscriptRepository(db)
        transcript = await transcript_repo.get_by_video_and_source(
            request.video_id, "whisper"
        )
        if transcript and transcript.segments:
            segments_text = "\n".join(
                f"[{seg.get('start', 0):.1f}s] {seg.get('text', '')}"
                for seg in transcript.segments[:100]
            )
            video_context = f"\n\nVideo transcript context (first 100 segments):\n{segments_text}"

    messages = []
    for msg in request.messages:
        content = msg.content
        if msg.role == "user" and video_context:
            content = f"{msg.content}\n\nNote: This conversation is about a video titled '{video_title}'.{video_context}"
        messages.append({"role": msg.role, "content": content})

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            async for token in chat_service.stream_chat(
                messages=messages,
                system_prompt=request.system_prompt,
            ):
                yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"
            yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )