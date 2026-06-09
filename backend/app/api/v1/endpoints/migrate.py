"""Migration endpoint to populate vocabularies table from existing study plans."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.models.study_plan import StudyPlan
from app.models.vocabulary import Vocabulary
from app.repositories.base import BaseRepository

router = APIRouter()


@router.post("/migrate-vocabulary")
async def migrate_vocabulary(db: AsyncSession = Depends(get_db)):
    """Migrate vocabulary items from study_plans.vocabulary JSON to vocabularies table.

    This is a one-time migration for existing videos whose study plans were created
    before vocabulary items were saved to the database.
    """
    result = await db.execute(select(StudyPlan))
    study_plans = result.scalars().all()

    migrated_count = 0
    existing_count = 0

    for sp in study_plans:
        vocabulary_items = sp.vocabulary or []
        for item in vocabulary_items:
            word = item.get("word", "").strip().lower()
            if not word:
                continue

            existing = await db.execute(
                select(Vocabulary).where(Vocabulary.word == word)
            )
            vocab = existing.scalar_one_or_none()

            if vocab:
                existing_count += 1
                continue

            vocab = Vocabulary(
                word=word,
                definition=item.get("definition"),
                context=item.get("context"),
                cefr_level=item.get("cefr_level") or item.get("difficulty"),
                pronunciation=item.get("pronunciation"),
            )
            db.add(vocab)
            migrated_count += 1

    await db.commit()

    return {
        "migrated": migrated_count,
        "already_exists": existing_count,
        "total_study_plans_processed": len(study_plans),
    }