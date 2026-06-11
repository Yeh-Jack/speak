"""Statistics service for calculating user learning metrics."""

from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import StudyProgress


DEFAULT_DAILY_GOAL_MINUTES = 30


class StatsService:
    """Service for calculating dashboard statistics."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_dashboard_stats(self, daily_goal_minutes: int = DEFAULT_DAILY_GOAL_MINUTES) -> dict:
        """Calculate dashboard statistics from study progress.

        Args:
            daily_goal_minutes: Target minutes per day (default 30)

        Returns:
            Dictionary with dashboard statistics
        """
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        words_learned = await self._count_words_learned()
        hours_learned = await self._calculate_hours_learned()
        streak_days = await self._calculate_streak_days()
        sentences_practiced = await self._count_sentences_practiced()
        today_minutes = await self._calculate_today_minutes(today_start, today_end)

        daily_goal_progress = min(100.0, (today_minutes / daily_goal_minutes) * 100) if daily_goal_minutes > 0 else 0.0
        daily_goal_remaining = max(0, daily_goal_minutes - int(today_minutes))

        return {
            "words_learned": words_learned,
            "hours_learned": round(hours_learned, 2),
            "streak_days": streak_days,
            "sentences_practiced": sentences_practiced,
            "daily_goal_minutes": daily_goal_minutes,
            "daily_goal_progress": round(daily_goal_progress, 1),
            "daily_goal_remaining": daily_goal_remaining,
            "today_minutes": round(today_minutes, 1),
            "date": today,
        }

    async def _count_words_learned(self) -> int:
        """Count vocabulary items that have been reviewed at least once."""
        from app.models.vocabulary import Vocabulary
        result = await self.session.execute(
            select(func.count()).where(Vocabulary.review_count > 0)
        )
        return result.scalar() or 0

    async def _calculate_hours_learned(self) -> float:
        """Calculate total hours learned from all progress records."""
        result = await self.session.execute(
            select(func.sum(StudyProgress.current_timestamp)).where(
                StudyProgress.completed.is_(True)
            )
        )
        total_seconds = result.scalar() or 0
        return total_seconds / 3600

    async def _calculate_streak_days(self) -> int:
        """Calculate consecutive days with study activity."""
        result = await self.session.execute(
            select(func.date(StudyProgress.created_at))
            .where(StudyProgress.completed.is_(True))
            .distinct()
            .order_by(func.date(StudyProgress.created_at).desc())
        )
        dates = [row[0] for row in result.fetchall()]

        if not dates:
            return 0

        streak = 0
        expected_date = date.today()

        for d in dates:
            if isinstance(d, str):
                d = datetime.strptime(d, "%Y-%m-%d").date()

            if d == expected_date:
                streak += 1
                expected_date -= timedelta(days=1)
            elif d == expected_date + timedelta(days=1):
                streak += 1
                expected_date = d - timedelta(days=1)
            else:
                break

        return streak

    async def _count_sentences_practiced(self) -> int:
        """Count completed study chunks (proxy for sentences practiced)."""
        result = await self.session.execute(
            select(func.count()).where(StudyProgress.completed.is_(True))
        )
        return result.scalar() or 0

    async def _calculate_today_minutes(self, today_start, today_end) -> float:
        """Calculate total minutes studied today."""
        result = await self.session.execute(
            select(func.sum(StudyProgress.current_timestamp)).where(
                func.date(StudyProgress.created_at) == today_start.date(),
                StudyProgress.current_timestamp > 0,
            )
        )
        total_seconds = result.scalar() or 0
        return total_seconds / 60