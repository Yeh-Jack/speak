"""Transcript model."""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.video import Video


class Transcript(Base, TimestampMixin):
    """Transcript for a video."""

    __tablename__ = "transcripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False, server_default="youtube")
    segments: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    full_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    video: Mapped["Video"] = relationship("Video", back_populates="transcripts")

    def __repr__(self) -> str:
        return f"<Transcript(id={self.id}, video_id={self.video_id}, source={self.source})>"
