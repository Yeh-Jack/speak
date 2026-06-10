"""Vocabulary schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class VocabularyBase(BaseModel):
    """Base vocabulary schema."""

    word: str = Field(..., max_length=200)
    definition: str | None = None
    context: str | None = None
    cefr_level: str | None = Field(None, max_length=10)


class VocabularyUpdate(BaseModel):
    """Schema for updating vocabulary."""

    definition: str | None = None
    context: str | None = None
    cefr_level: str | None = Field(None, max_length=10)


class Vocabulary(VocabularyBase):
    """Vocabulary response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    review_count: int
    next_review: date | None
    interval: int
    ease_factor: float
    repetition_number: int
    created_at: datetime
    updated_at: datetime


class VocabularyReview(BaseModel):
    """Schema for reviewing vocabulary with SM-2 algorithm."""

    quality: int = Field(..., ge=0, le=5)  # 0-5 quality rating


class VocabularyListResponse(BaseModel):
    """Paginated vocabulary list response."""

    items: list[Vocabulary]
    total: int
    page: int
    limit: int
