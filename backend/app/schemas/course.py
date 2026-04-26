"""Course and CourseVideo schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CourseVideoBase(BaseModel):
    """Base course video schema."""

    order_index: int


class CourseVideoCreate(CourseVideoBase):
    """Schema for creating a course video."""

    video_id: uuid.UUID


class CourseVideoUpdate(BaseModel):
    """Schema for updating a course video."""

    order_index: int | None = None


class CourseVideo(CourseVideoBase):
    """Course video response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    video_id: uuid.UUID
    study_plan: dict | None = None
    created_at: datetime
    updated_at: datetime


class CourseBase(BaseModel):
    """Base course schema."""

    title: str = Field(..., max_length=500)
    description: str | None = None


class CourseCreate(CourseBase):
    """Schema for creating a course."""

    video_ids: list[uuid.UUID] = []


class CourseUpdate(BaseModel):
    """Schema for updating a course."""

    title: str | None = Field(None, max_length=500)
    description: str | None = None
    status: str | None = None
    current_video_index: int | None = None


class Course(CourseBase):
    """Course response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    current_video_index: int
    course_videos: list[CourseVideo] = []
    created_at: datetime
    updated_at: datetime


class ReorderVideosRequest(BaseModel):
    """Schema for reordering videos in a course."""

    video_orders: dict[uuid.UUID, int]
