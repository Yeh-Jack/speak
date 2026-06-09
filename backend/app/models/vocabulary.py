"""Vocabulary model."""

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Boolean, Date, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Vocabulary(Base, TimestampMixin):
    """Vocabulary item for spaced repetition learning."""

    __tablename__ = "vocabularies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    word: Mapped[str] = mapped_column(String(200), nullable=False)
    definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cefr_level: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    pronunciation: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    next_review: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    interval: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    ease_factor: Mapped[float] = mapped_column(Float, nullable=False, server_default="2.5")
    repetition_number: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    is_favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")

    def __repr__(self) -> str:
        return f"<Vocabulary(id={self.id}, word={self.word})>"
