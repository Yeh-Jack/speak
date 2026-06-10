"""Study Plan schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StudyPlanBase(BaseModel):
    """Base study plan schema."""

    title: str = Field(..., max_length=500)
    duration: str = Field(..., max_length=50)


class StudyPlanCreate(StudyPlanBase):
    """Schema for creating a study plan."""

    video_id: uuid.UUID
    overall_difficulty: str | None = Field(None, max_length=10)
    estimated_time: str | None = Field(None, max_length=100)
    chunks: list[dict] = []
    vocabulary: list[dict] = []
    grammar: list[str] = []
    notes: str | None = None
    notes_zh: str | None = None


class StudyPlanUpdate(BaseModel):
    """Schema for updating a study plan."""

    title: str | None = Field(None, max_length=500)
    duration: str | None = Field(None, max_length=50)
    overall_difficulty: str | None = Field(None, max_length=10)
    estimated_time: str | None = Field(None, max_length=100)
    chunks: list[dict] | None = None
    vocabulary: list[dict] | None = None
    grammar: list[str] | None = None
    notes: str | None = None
    notes_zh: str | None = None


class StudyPlan(StudyPlanBase):
    """Study plan response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    video_id: uuid.UUID
    overall_difficulty: str | None
    estimated_time: str | None
    chunks: list[dict]
    vocabulary: list[dict]
    grammar: list[str]
    notes: str | None
    notes_zh: str | None
    created_at: datetime
