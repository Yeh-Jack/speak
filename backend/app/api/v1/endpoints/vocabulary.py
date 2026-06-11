"""Vocabulary endpoints for spaced repetition learning."""

from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.vocabulary import Vocabulary as VocabularyModel
from app.repositories.vocabulary import VocabularyRepository
from app.schemas.vocabulary import Vocabulary, VocabularyReview

router = APIRouter()


class FavoriteWord(BaseModel):
    word: str


class FavoriteListResponse(BaseModel):
    words: List[str]


@router.get("/reviewed", response_model=List[str])
async def get_reviewed_vocabulary(
    db: AsyncSession = Depends(get_db),
):
    """Get all vocabulary words that have been reviewed."""
    repo = VocabularyRepository(db)
    return await repo.get_reviewed_words()


@router.get("/favorites", response_model=FavoriteListResponse)
async def get_favorite_vocabulary(
    db: AsyncSession = Depends(get_db),
):
    """Get all favorite vocabulary words."""
    repo = VocabularyRepository(db)
    favorites = await repo.get_favorites()
    return FavoriteListResponse(words=[v.word for v in favorites])


@router.post("/favorites/{word}/toggle", response_model=Vocabulary)
async def toggle_favorite_vocabulary(
    word: str,
    db: AsyncSession = Depends(get_db),
):
    """Toggle favorite status of a vocabulary word."""
    repo = VocabularyRepository(db)
    vocab = await repo.get_by_word(word)

    if not vocab:
        vocab = VocabularyModel(
            word=word.lower().strip(),
            is_favorite=True,
        )
        db.add(vocab)
    else:
        vocab.is_favorite = not vocab.is_favorite

    await db.commit()
    await db.refresh(vocab)
    return vocab


@router.get("/{word}", response_model=Vocabulary)
async def get_vocabulary(
    word: str,
    db: AsyncSession = Depends(get_db),
):
    """Get vocabulary by word."""
    repo = VocabularyRepository(db)
    vocab = await repo.get_by_word(word)
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
    return vocab


@router.post("/{word}/review", response_model=Vocabulary)
async def review_vocabulary(
    word: str,
    review_data: VocabularyReview,
    db: AsyncSession = Depends(get_db),
):
    """Review vocabulary and update spaced repetition schedule.

    Uses simplified SM-2 algorithm:
    - quality 0-2: Reset (needs review again soon)
    - quality 3-5: Success (schedule next review)
    """
    repo = VocabularyRepository(db)
    vocab = await repo.get_by_word(word)

    if not vocab:
        vocab = VocabularyModel(
            word=word.lower().strip(),
            review_count=1,
        )
        db.add(vocab)
        await db.flush()
    else:
        quality = review_data.quality

        if quality < 3:
            vocab.review_count = 0
            vocab.next_review = date.today() + timedelta(days=1)
        else:
            vocab.review_count += 1
            intervals = [1, 3, 7, 14, 30, 60]
            interval_days = intervals[min(vocab.review_count, len(intervals) - 1)]
            vocab.next_review = date.today() + timedelta(days=interval_days)

    await db.commit()
    await db.refresh(vocab)
    return vocab