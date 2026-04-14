"""Exam schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class ExamQuestionBase(BaseModel):
    """Base exam question schema."""

    question_type: str = Field(..., max_length=50)
    question_text: str
    correct_answer: str
    order_index: int


class ExamQuestionCreate(ExamQuestionBase):
    """Schema for creating an exam question."""

    exam_id: uuid.UUID
    options: list[str] | None = None
    explanation: str | None = None


class ExamQuestion(ExamQuestionBase):
    """Exam question response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    exam_id: uuid.UUID
    options: list[str] | None
    explanation: str | None
    created_at: datetime
    updated_at: datetime


class ExamBase(BaseModel):
    """Base exam schema."""

    title: str = Field(..., max_length=500)


class ExamCreate(ExamBase):
    """Schema for creating an exam."""

    video_id: uuid.UUID
    chunk_index: int | None = None
    total_questions: int = Field(default=10, ge=5, le=50)


class Exam(ExamBase):
    """Exam response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    video_id: uuid.UUID
    chunk_index: int | None
    status: str
    total_questions: int
    questions: list[ExamQuestion] = []
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class ExamResultBase(BaseModel):
    """Base exam result schema."""

    score: float = Field(..., ge=0, le=100)
    correct_count: int
    total_count: int


class ExamResultCreate(ExamResultBase):
    """Schema for creating an exam result."""

    exam_id: uuid.UUID
    answers: list[dict] = []
    feedback: str | None = None


class ExamResult(ExamResultBase):
    """Exam result response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    exam_id: uuid.UUID
    answers: list[dict]
    feedback: str | None
    created_at: datetime
    updated_at: datetime


class ExamSubmission(BaseModel):
    """Schema for submitting exam answers."""

    answers: dict[uuid.UUID, str]  # question_id -> answer


class ExamHistoryResponse(BaseModel):
    """Paginated exam history response."""

    items: list[ExamResult]
    total: int
    page: int
    limit: int
