"""Study plan model."""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.video import Video


class StudyPlan(Base, TimestampMixin):
    """Study plan for a video or chunk."""

    __tablename__ = "study_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    objectives: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    vocabulary: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    grammar: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes_zh: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    overall_difficulty: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    estimated_time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    video: Mapped["Video"] = relationship("Video", back_populates="study_plans")

    def __repr__(self) -> str:
        return (
            f"<StudyPlan(id={self.id}, video_id={self.video_id}, chunk_index={self.chunk_index})>"
        )
