"""Transcript schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TranscriptSegment(BaseModel):
    """A single transcript segment."""

    start: float
    end: float
    text: str
    speaker: str | None = None


class TranscriptCreate(BaseModel):
    """Schema for creating a transcript (user-uploaded)."""

    source: str = "user"
    language: str = "en"
    segments: list[dict]


class TranscriptResponse(BaseModel):
    """Transcript response schema."""

    model_config = ConfigDict(from_attributes=True)

    video_id: UUID
    source: str
    language: str | None
    segments: list[dict] | None
    full_text: str | None = None


class TranscriptUpload(BaseModel):
    """Schema for user-uploaded subtitle content."""

    language: str = "en"
    segments: list[dict] = []
