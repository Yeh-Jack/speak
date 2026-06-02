"""Study Progress schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StudyProgressBase(BaseModel):
    """Base study progress schema."""

    video_id: uuid.UUID
    chunk_index: int
    current_timestamp: float
    sentence_index: int | None = None
    completed: bool = False


class StudyProgressCreate(StudyProgressBase):
    """Schema for creating study progress."""

    pass


class StudyProgressUpdate(BaseModel):
    """Schema for updating study progress."""

    current_timestamp: float | None = None
    sentence_index: int | None = None
    completed: bool | None = None


class StudyProgress(StudyProgressBase):
    """Study progress response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    updated_at: datetime


class ResumeInfo(BaseModel):
    """Resume information for a video."""

    video_id: uuid.UUID
    chunk_index: int
    timestamp: float
    sentence_index: int | None
