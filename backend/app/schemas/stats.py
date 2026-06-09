"""Statistics schema."""

from datetime import date

from pydantic import BaseModel


class DashboardStats(BaseModel):
    words_learned: int = 0
    hours_learned: float = 0
    streak_days: int = 0
    sentences_practiced: int = 0
    daily_goal_minutes: int = 30
    daily_goal_progress: float = 0.0
    daily_goal_remaining: int = 30
    today_minutes: float = 0.0
    date: date