"""Video and VideoChunk schemas."""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VideoProcessState(str, Enum):
    """Video processing state machine states."""

    PENDING = "pending"
    DOWNLOADING = "downloading"
    DOWNLOADING_COMPLETE = "downloading_complete"
    CHUNKING = "chunking"
    CHUNKING_COMPLETE = "chunking_complete"
    TRANSCRIBING = "transcribing"
    TRANSCRIBING_COMPLETE = "transcribing_complete"
    STUDYING = "studying"
    READY = "ready"
    FAILED = "failed"


class VideoChunkBase(BaseModel):
    """Base video chunk schema."""

    chunk_index: int
    start_time: float
    end_time: float
    duration: float


class VideoChunkCreate(VideoChunkBase):
    """Schema for creating a video chunk."""

    pass


class VideoChunkUpdate(BaseModel):
    """Schema for updating a video chunk."""

    transcript: list[dict] | None = None
    status: str | None = None


class VideoChunk(VideoChunkBase):
    """Video chunk response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    video_id: uuid.UUID
    transcript: list[dict] | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class VideoBase(BaseModel):
    """Base video schema."""

    title: str = Field(..., max_length=500)
    description: str | None = None
    youtube_url: str
    chunk_duration: float = Field(default=300.0, ge=30, le=600)


class VideoCreate(BaseModel):
    """Schema for creating a video from YouTube URL."""

    youtube_url: str = Field(..., min_length=10)
    chunk_duration: float = Field(default=300.0, ge=30, le=600)

    @field_validator("youtube_url")
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        if "youtube.com" not in v and "youtu.be" not in v:
            raise ValueError("Invalid YouTube URL")
        return v


class VideoUpdate(BaseModel):
    """Schema for updating a video."""

    title: str | None = Field(None, max_length=500)
    description: str | None = None
    status: str | None = None


class Video(VideoBase):
    """Video response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_type: str
    file_path: str | None
    duration: float
    status: str
    chunks: list[VideoChunk] = []
    created_at: datetime
    updated_at: datetime


class VideoResponse(BaseModel):
    """Complete video response with all data."""

    video: Video
    chunks: list[VideoChunk]
    transcript: dict | None = None
    study_plan: dict | None = None


class VideoFormatInfo(BaseModel):
    """Video format information."""

    format_id: str | None = None
    ext: str | None = None
    resolution: str | None = None
    filesize: int | None = None
    fps: float | None = None
    vcodec: str | None = None
    acodec: str | None = None


class VideoInfoResponse(BaseModel):
    """Video metadata response without DB operations."""

    youtube_url: str
    title: str | None = None
    description: str | None = None
    duration: float | None = None
    thumbnail: str | None = None
    uploader: str | None = None
    upload_date: str | None = None
    view_count: int | None = None
    like_count: int | None = None
    categories: list[str] | None = None
    tags: list[str] | None = None
    language: str | None = None
    subtitles: list[str] = []
    automatic_captions: list[str] = []
    available_formats: list[VideoFormatInfo] = []
