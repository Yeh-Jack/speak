"""Statistics endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.stats import DashboardStats
from app.services.stats_service import StatsService

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    daily_goal_minutes: int = 30,
    db: AsyncSession = Depends(get_db),
) -> DashboardStats:
    """Get dashboard statistics.

    Returns aggregated statistics about user learning progress:
    - words_learned: Estimated words learned
    - hours_learned: Total hours of study
    - streak_days: Consecutive days with activity
    - sentences_practiced: Number of completed study sessions
    - daily_goal_minutes: Target daily study minutes
    - daily_goal_progress: Today's progress toward goal (0-100%)
    - daily_goal_remaining: Minutes remaining today
    - today_minutes: Actual minutes studied today
    - date: Current date
    """
    stats_service = StatsService(db)
    stats = await stats_service.get_dashboard_stats(daily_goal_minutes=daily_goal_minutes)
    return DashboardStats(**stats)