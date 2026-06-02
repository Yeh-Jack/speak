"""Video model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.chunk import VideoChunk
    from app.models.study_plan import StudyPlan
    from app.models.transcript import Transcript


class Video(Base, TimestampMixin):
    """Video entity representing a YouTube video for learning."""

    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, server_default="youtube")
    youtube_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    duration: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.0")
    chunk_duration: Mapped[float] = mapped_column(Float, nullable=False, server_default="300.0")
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="pending")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    thumbnail: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    uploader: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    upload_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    view_count: Mapped[Optional[int]] = mapped_column(Float, nullable=True)
    like_count: Mapped[Optional[int]] = mapped_column(Float, nullable=True)

    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    chunks: Mapped[list["VideoChunk"]] = relationship(
        "VideoChunk", back_populates="video", cascade="all, delete-orphan", lazy="selectin"
    )
    transcripts: Mapped[list["Transcript"]] = relationship(
        "Transcript", back_populates="video", cascade="all, delete-orphan", lazy="selectin"
    )
    study_plans: Mapped[list["StudyPlan"]] = relationship(
        "StudyPlan", back_populates="video", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, title={self.title}, status={self.status})>"
