"""Speaking practice record model."""

import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class SpeakingPracticeRecord(Base, TimestampMixin):
    """Record of a speaking practice session."""

    __tablename__ = "speaking_practice_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    segment_start: Mapped[float] = mapped_column(Float, nullable=False)
    segment_end: Mapped[float] = mapped_column(Float, nullable=False)
    character_text: Mapped[str] = mapped_column(Text, nullable=False)
    user_recording_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")

    def __repr__(self) -> str:
        return f"<SpeakingPracticeRecord(id={self.id}, video_id={self.video_id}, similarity={self.similarity_score})>"