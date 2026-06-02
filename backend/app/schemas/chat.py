"""Chat schemas for AI tutor interface."""

from pydantic import BaseModel, Field
from uuid import UUID


class ChatMessage(BaseModel):
    """A single chat message."""

    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class StreamChatRequest(BaseModel):
    """Request for streaming chat."""

    video_id: UUID | None = Field(None, description="Video ID for context (optional)")
    messages: list[ChatMessage] = Field(..., description="Chat history")
    system_prompt: str | None = Field(
        None,
        description="Optional system prompt override",
    )