"""Study plan repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.study_plan import StudyPlan
from app.models.vocabulary import Vocabulary
from app.repositories.base import BaseRepository


class StudyPlanRepository(BaseRepository[StudyPlan]):
    """Repository for StudyPlan model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, StudyPlan)

    async def get_by_video_id(self, video_id: UUID) -> StudyPlan | None:
        """Get study plan for a video (overall plan, chunk_index is null)."""
        if isinstance(video_id, UUID):
            video_id = str(video_id)
        result = await self.session.execute(
            select(StudyPlan).where(StudyPlan.video_id == video_id, StudyPlan.chunk_index.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_video_and_chunk(self, video_id: UUID, chunk_index: int) -> StudyPlan | None:
        """Get study plan for a specific chunk."""
        if isinstance(video_id, UUID):
            video_id = str(video_id)
        result = await self.session.execute(
            select(StudyPlan).where(
                StudyPlan.video_id == video_id, StudyPlan.chunk_index == chunk_index
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_video_id(self, video_id: UUID) -> list[StudyPlan]:
        """Get all study plans for a video (including chunk-specific)."""
        if isinstance(video_id, UUID):
            video_id = str(video_id)
        result = await self.session.execute(
            select(StudyPlan).where(StudyPlan.video_id == video_id).order_by(StudyPlan.chunk_index)
        )
        return list(result.scalars().all())

    async def create(self, video_id: UUID, study_plan_data: dict) -> StudyPlan:
        """Create a study plan for a video and save vocabulary items to database."""
        study_plan = StudyPlan(
            video_id=str(video_id),
            chunk_index=None,
            objectives=study_plan_data.get("objectives", []),
            vocabulary=study_plan_data.get("vocabulary", []),
            grammar=study_plan_data.get("grammar", []),
            notes=study_plan_data.get("notes"),
            notes_zh=study_plan_data.get("notes_zh"),
            overall_difficulty=study_plan_data.get("overall_difficulty"),
            estimated_time=study_plan_data.get("estimated_time"),
        )
        self.session.add(study_plan)
        await self.session.flush()

        await self._save_vocabulary_items(study_plan_data.get("vocabulary", []))

        await self.session.refresh(study_plan)
        return study_plan

    async def _save_vocabulary_items(self, vocabulary_items: list[dict]) -> None:
        """Save vocabulary items to the vocabulary table."""
        for item in vocabulary_items:
            word = item.get("word", "").strip().lower()
            if not word:
                continue

            existing = await self.session.execute(
                select(Vocabulary).where(Vocabulary.word == word)
            )
            vocab = existing.scalar_one_or_none()

            if vocab:
                vocab.definition = item.get("definition") or vocab.definition
                vocab.context = item.get("context") or vocab.context
                vocab.cefr_level = item.get("cefr_level") or item.get("difficulty") or vocab.cefr_level
            else:
                vocab = Vocabulary(
                    word=word,
                    definition=item.get("definition"),
                    context=item.get("context"),
                    cefr_level=item.get("cefr_level") or item.get("difficulty"),
                    pronunciation=item.get("pronunciation"),
                )
                self.session.add(vocab)

        await self.session.flush()
