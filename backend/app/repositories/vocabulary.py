"""Vocabulary repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vocabulary import Vocabulary
from app.repositories.base import BaseRepository


class VocabularyRepository(BaseRepository[Vocabulary]):
    """Repository for Vocabulary model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Vocabulary)

    async def get_by_word(self, word: str) -> Vocabulary | None:
        """Get vocabulary by word."""
        result = await self.session.execute(
            select(Vocabulary).where(Vocabulary.word == word.lower())
        )
        return result.scalar_one_or_none()

    async def get_due_for_review(self) -> list[Vocabulary]:
        """Get vocabulary items due for review."""
        from datetime import date

        result = await self.session.execute(
            select(Vocabulary).where(Vocabulary.next_review <= date.today())
        )
        return list(result.scalars().all())

    async def get_by_cefr_level(self, level: str) -> list[Vocabulary]:
        """Get vocabulary by CEFR level."""
        result = await self.session.execute(
            select(Vocabulary).where(Vocabulary.cefr_level == level)
        )
        return list(result.scalars().all())

    async def search(self, query: str, limit: int = 50) -> list[Vocabulary]:
        """Search vocabulary by word prefix."""
        result = await self.session.execute(
            select(Vocabulary).where(Vocabulary.word.like(f"{query.lower()}%")).limit(limit)
        )
        return list(result.scalars().all())

    async def get_reviewed_words(self) -> list[str]:
        """Get all words that have been reviewed at least once."""
        result = await self.session.execute(
            select(Vocabulary.word).where(Vocabulary.review_count > 0)
        )
        return [row[0] for row in result.fetchall()]

    async def get_favorites(self) -> list[Vocabulary]:
        """Get all favorite vocabulary items."""
        result = await self.session.execute(
            select(Vocabulary).where(Vocabulary.is_favorite == True)
        )
        return list(result.scalars().all())
