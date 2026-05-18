"""Study progress model."""

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class StudyProgress(Base, TimestampMixin):
    """Progress tracking for video chunks."""

    __tablename__ = "study_progress"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    current_timestamp: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.0")
    sentence_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    next_review: Mapped[date | None] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:
        return f"<StudyProgress(id={self.id}, video_id={self.video_id}, chunk_index={self.chunk_index})>"
