"""Course models."""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.video import Video


class Course(Base, TimestampMixin):
    """Course entity representing a learning course."""

    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="pending")
    current_video_index: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    course_videos: Mapped[list["CourseVideo"]] = relationship(
        "CourseVideo", back_populates="course", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Course(id={self.id}, title={self.title}, status={self.status})>"


class CourseVideo(Base, TimestampMixin):
    """Association between Course and Video with ordering."""

    __tablename__ = "course_videos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    video_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    study_plan: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    course: Mapped["Course"] = relationship("Course", back_populates="course_videos")
    video: Mapped["Video"] = relationship("Video")

    def __repr__(self) -> str:
        return f"<CourseVideo(id={self.id}, course_id={self.course_id}, video_id={self.video_id})>"
