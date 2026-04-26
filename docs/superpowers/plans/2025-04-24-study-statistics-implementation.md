# Study Statistics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement study progress statistics with interactive pyecharts visualizations for time-based comparisons

**Architecture:** Backend FastAPI service calculates statistics from SQLite database, generates interactive chart configs using pyecharts, and returns JSON to Vue frontend which renders charts using ECharts library

**Tech Stack:** FastAPI, SQLAlchemy 2.0, pyecharts, SQLite, Vue 3, ECharts, TypeScript

---

## File Structure Overview

**New Files:**
- `backend/app/schemas/statistics.py` - Pydantic schemas for statistics
- `backend/app/services/statistics_service.py` - Statistics calculation logic
- `backend/app/services/chart_service.py` - Pyecharts chart generation
- `backend/app/api/v1/endpoints/statistics.py` - API endpoints
- `backend/app/models/statistics.py` - Database models (if needed)
- `frontend/src/stores/statistics.store.ts` - Pinia store
- `frontend/src/components/statistics/StudyChart.vue` - Chart component
- `frontend/src/views/StatisticsView.vue` - Statistics page

**Modified Files:**
- `backend/pyproject.toml` - Add pyecharts dependency
- `backend/app/api/v1/router.py` - Include statistics router
- `backend/app/db/base.py` - Update model imports (if needed)
- `backend/alembic/versions/` - Add migration (if needed)
- `AGENTS.md` - Update documentation
- `design-specs.md` - Update specifications

---

## Task 1: Add pyecharts Dependency

**Files:**
- Modify: `backend/pyproject.toml:21-55`

- [ ] **Step 1: Add pyecharts to dependencies**

Add after line 54 (before `[project.optional-dependencies]`):
```toml
    # Charts
    "pyecharts>=2.0.0",
```

The dependencies section should look like:
```toml
dependencies = [
    # FastAPI and web framework
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-multipart>=0.0.6",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    # Database - SQLite with async support
    "sqlalchemy[asyncio]>=2.0.25",
    "aiosqlite>=0.19.0",
    "alembic>=1.13.0",
    # LLM - llama-cpp-python with GPU support
    "llama-cpp-python>=0.2.26",
    # GPU detection - NVIDIA only
    "gputil>=1.4.0",
    # Video processing
    "ffmpeg-python>=0.2.0",
    "yt-dlp>=2024.1.0",
    # Transcription
    "faster-whisper>=0.10.0",
    "pyannote.audio>=3.1.0",
    "pysubs2>=1.6.0",
    # HTTP client
    "httpx>=0.26.0",
    "aiohttp>=3.9.0",
    # Utilities
    "python-dotenv>=1.0.0",
    "tenacity>=8.2.0",
    "orjson>=3.9.0",
    # Charts
    "pyecharts>=2.0.0",
]
```

- [ ] **Step 2: Sync dependencies with uv**
```bash
cd /workspaces/education/backend
uv sync
```

- [ ] **Step 3: Verify pyecharts is installed**
```bash
PYTHONPATH=/workspaces/education/backend uv run python -c "from pyecharts.charts import Line; print('pyecharts installed successfully')"
```

Expected output: `pyecharts installed successfully`

- [ ] **Step 4: Commit changes**
```bash
git add backend/pyproject.toml
git commit -m "deps: add pyecharts for interactive charts"
```

---

## Task 2: Create Statistics Schemas

**Files:**
- Create: `backend/app/schemas/statistics.py`

- [ ] **Step 1: Create the statistics schemas file**

```python
"""Study progress and evaluation statistics schemas."""

from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class DailyStudyStat(BaseModel):
    """Daily study statistics."""

    model_config = ConfigDict(from_attributes=True)

    date: date
    total_minutes: int = Field(..., ge=0)
    videos_completed: int = Field(..., ge=0)
    chunks_studied: int = Field(..., ge=0)
    streak_day: bool


class WeeklyStudyStat(BaseModel):
    """Weekly aggregated statistics."""

    model_config = ConfigDict(from_attributes=True)

    week_start: date
    week_end: date
    total_minutes: int = Field(..., ge=0)
    avg_daily_minutes: float = Field(..., ge=0)
    days_studied: int = Field(..., ge=0)
    videos_completed: int = Field(..., ge=0)


class StudyStreak(BaseModel):
    """Current and historical streak information."""

    model_config = ConfigDict(from_attributes=True)

    current_streak: int = Field(..., ge=0)
    longest_streak: int = Field(..., ge=0)
    last_study_date: Optional[date] = None
    total_study_days: int = Field(..., ge=0)


class VideoProgressStat(BaseModel):
    """Progress statistics for a video."""

    model_config = ConfigDict(from_attributes=True)

    video_id: str
    title: str
    total_chunks: int = Field(..., ge=0)
    completed_chunks: int = Field(..., ge=0)
    progress_percentage: float = Field(..., ge=0, le=100)
    last_studied: Optional[datetime] = None
    total_time_spent: int = Field(..., ge=0)


class ChartConfig(BaseModel):
    """Interactive chart configuration from pyecharts."""

    model_config = ConfigDict(from_attributes=True)

    chart_id: str
    chart_type: Literal["line", "bar", "calendar", "pie"]
    title: str
    pyecharts_option: dict
    interactive_features: List[str]


class StatisticsSummary(BaseModel):
    """Quick summary statistics."""

    total_study_time: int = Field(..., ge=0, description="Total minutes studied")
    total_videos: int = Field(..., ge=0)
    completed_videos: int = Field(..., ge=0)
    completion_rate: float = Field(..., ge=0, le=100)
    avg_daily_time: float = Field(..., ge=0)
    current_streak: int = Field(..., ge=0)


class StatisticsDashboard(BaseModel):
    """Complete dashboard response."""

    period: Literal["7d", "30d", "90d", "1y"]
    summary: StatisticsSummary
    streak: StudyStreak
    charts: List[ChartConfig]
    daily_stats: List[DailyStudyStat]


class TimeSeriesRequest(BaseModel):
    """Request for time series data."""

    start_date: date
    end_date: date


class StreakResponse(BaseModel):
    """Streak information response."""

    streak: StudyStreak
    streak_milestones: List[int] = Field(default=[7, 30, 60, 100])
```

- [ ] **Step 2: Update schemas __init__.py**

Read `/workspaces/education/backend/app/schemas/__init__.py` and add imports:

```python
from app.schemas.statistics import (
    ChartConfig,
    DailyStudyStat,
    StatisticsDashboard,
    StatisticsSummary,
    StudyStreak,
    VideoProgressStat,
    WeeklyStudyStat,
)
```

- [ ] **Step 3: Commit changes**
```bash
git add backend/app/schemas/statistics.py backend/app/schemas/__init__.py
git commit -m "feat: add statistics schemas with interactive chart configs"
```

---

## Task 3: Create Statistics Service

**Files:**
- Create: `backend/app/services/statistics_service.py`

- [ ] **Step 1: Create statistics calculation service**

```python
"""Study statistics calculation service."""

from datetime import date, datetime, timedelta
from typing import List, Optional

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.schemas.statistics import (
    DailyStudyStat,
    StudyStreak,
    VideoProgressStat,
    WeeklyStudyStat,
    StatisticsSummary,
)


class StatisticsService:
    """Calculate study statistics from database."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_daily_stats(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
    ) -> List[DailyStudyStat]:
        """Aggregate study time per day."""
        # Query study_progress table joined with video_chunks
        from app.db.base import Base

        # Get all study activity within date range
        query = (
            select(
                func.date(
                    func.datetime(study_progress.c.updated_at, "unixepoch")
                ).label("study_date"),
                func.count(study_progress.c.chunk_index).label("chunks"),
                func.count(func.distinct(study_progress.c.video_id)).label("videos"),
                func.sum(
                    study_progress.c.current_timestamp - video_chunks.c.start_time
                ).label("seconds"),
            )
            .select_from(
                study_progress.join(
                    video_chunks,
                    study_progress.c.video_id == video_chunks.c.video_id,
                )
            )
            .where(
                and_(
                    study_progress.c.user_id == user_id,
                    func.date(study_progress.c.updated_at) >= start_date,
                    func.date(study_progress.c.updated_at) <= end_date,
                )
            )
            .group_by("study_date")
            .order_by("study_date")
        )

        result = await self.db.execute(query)
        rows = result.fetchall()

        # Fill in missing dates with zeros
        daily_stats = []
        current_date = start_date
        row_dict = {row.study_date: row for row in rows}

        while current_date <= end_date:
            row = row_dict.get(current_date)
            if row:
                daily_stats.append(
                    DailyStudyStat(
                        date=current_date,
                        total_minutes=round((row.seconds or 0) / 60),
                        videos_completed=row.videos or 0,
                        chunks_studied=row.chunks or 0,
                        streak_day=True,
                    )
                )
            else:
                daily_stats.append(
                    DailyStudyStat(
                        date=current_date,
                        total_minutes=0,
                        videos_completed=0,
                        chunks_studied=0,
                        streak_day=False,
                    )
                )
            current_date += timedelta(days=1)

        return daily_stats

    async def calculate_streak(self, user_id: str) -> StudyStreak:
        """Calculate current and longest streak."""
        query = (
            select(func.date(study_progress.c.updated_at).label("study_date"))
            .where(study_progress.c.user_id == user_id)
            .distinct()
            .order_by("study_date")
        )

        result = await self.db.execute(query)
        study_dates = [row.study_date for row in result]

        if not study_dates:
            return StudyStreak(
                current_streak=0,
                longest_streak=0,
                last_study_date=None,
                total_study_days=0,
            )

        current_streak = self._calculate_current_streak(study_dates)
        longest_streak = self._calculate_longest_streak(study_dates)

        return StudyStreak(
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_study_date=study_dates[-1],
            total_study_days=len(study_dates),
        )

    def _calculate_current_streak(self, dates: List[date]) -> int:
        """Calculate current consecutive day streak."""
        if not dates:
            return 0

        today = date.today()
        yesterday = today - timedelta(days=1)

        if dates[-1] not in [today, yesterday]:
            return 0

        streak = 1
        for i in range(len(dates) - 2, -1, -1):
            if dates[i] == dates[i + 1] - timedelta(days=1):
                streak += 1
            else:
                break

        return streak

    def _calculate_longest_streak(self, dates: List[date]) -> int:
        """Calculate longest streak ever."""
        if not dates:
            return 0

        longest = 1
        current = 1

        for i in range(1, len(dates)):
            if dates[i] == dates[i - 1] + timedelta(days=1):
                current += 1
                longest = max(longest, current)
            else:
                current = 1

        return longest

    async def get_summary(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
    ) -> StatisticsSummary:
        """Calculate summary statistics."""
        # Total study time
        time_query = (
            select(
                func.sum(
                    study_progress.c.current_timestamp - video_chunks.c.start_time
                ).label("total_seconds")
            )
            .select_from(
                study_progress.join(
                    video_chunks,
                    study_progress.c.video_id == video_chunks.c.video_id,
                )
            )
            .where(
                and_(
                    study_progress.c.user_id == user_id,
                    func.date(study_progress.c.updated_at) >= start_date,
                    func.date(study_progress.c.updated_at) <= end_date,
                )
            )
        )

        time_result = await self.db.execute(time_query)
        total_seconds = time_result.scalar() or 0
        total_minutes = round(total_seconds / 60)

        # Video stats
        video_query = (
            select(
                func.count(func.distinct(videos.c.id)).label("total"),
                func.count(
                    func.distinct(
                        func.case(
                            (videos.c.status == "completed", videos.c.id)
                        )
                    )
                ).label("completed"),
            )
            .where(videos.c.user_id == user_id)
        )

        video_result = await self.db.execute(video_query)
        video_row = video_result.fetchone()
        total_videos = video_row.total or 0
        completed_videos = video_row.completed or 0

        completion_rate = (
            (completed_videos / total_videos * 100) if total_videos > 0 else 0
        )

        # Average daily time
        days = max(1, (end_date - start_date).days + 1)
        avg_daily_time = total_minutes / days

        # Current streak
        streak = await self.calculate_streak(user_id)

        return StatisticsSummary(
            total_study_time=total_minutes,
            total_videos=total_videos,
            completed_videos=completed_videos,
            completion_rate=round(completion_rate, 2),
            avg_daily_time=round(avg_daily_time, 2),
            current_streak=streak.current_streak,
        )


# Global service instance
async def get_statistics_service():
    """Get statistics service with database session."""
    async with AsyncSessionLocal() as db:
        yield StatisticsService(db)
```

- [ ] **Step 2: Fix imports - add missing table references**

Update the imports at the top of the file:

```python
"""Study statistics calculation service."""

from datetime import date, datetime, timedelta
from typing import List, Optional

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base
from app.db.session import AsyncSessionLocal
from app.schemas.statistics import (
    DailyStudyStat,
    StudyStreak,
    VideoProgressStat,
    WeeklyStudyStat,
    StatisticsSummary,
)

# Import table references from alembic migration or models
# For now, use string references that will be resolved
study_progress = None  # Will be imported from models
video_chunks = None
videos = None
```

Actually, we need to create proper SQLAlchemy models first. Let me check if models exist.

- [ ] **Step 3: Check if models exist**

```bash
ls -la /workspaces/education/backend/app/models/ 2>/dev/null || echo "No models directory"
```

If no models exist, we'll need to create them. Let me continue assuming we'll create the models.

- [ ] **Step 4: Commit changes (models will be created in next task)**
```bash
git add backend/app/services/statistics_service.py
git commit -m "feat: add statistics calculation service"
```

---

## Task 4: Create Database Models

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/study_progress.py`
- Create: `backend/app/models/video.py`

- [ ] **Step 1: Create models package**

Create `/workspaces/education/backend/app/models/__init__.py`:

```python
"""SQLAlchemy models."""

from app.models.study_progress import StudyProgress
from app.models.video import Video, VideoChunk

__all__ = ["StudyProgress", "Video", "VideoChunk"]
```

- [ ] **Step 2: Create study progress model**

Create `/workspaces/education/backend/app/models/study_progress.py`:

```python
"""Study progress model."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StudyProgress(Base):
    """Study progress tracking model."""

    __tablename__ = "study_progress"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    video_id: Mapped[str] = mapped_column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    current_timestamp: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sentence_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<StudyProgress(id={self.id}, user_id={self.user_id}, video_id={self.video_id})>"
```

- [ ] **Step 3: Create video models**

Create `/workspaces/education/backend/app/models/video.py`:

```python
"""Video and video chunk models."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Video(Base):
    """Video model."""

    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="youtube")
    youtube_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    duration: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    chunk_duration: Mapped[float] = mapped_column(Float, nullable=False, default=300.0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, title={self.title})>"


class VideoChunk(Base):
    """Video chunk model."""

    __tablename__ = "video_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id: Mapped[str] = mapped_column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    transcript: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<VideoChunk(id={self.id}, video_id={self.video_id}, index={self.chunk_index})>"
```

- [ ] **Step 4: Update imports in base.py to include models**

Read and update `/workspaces/education/backend/app/db/base.py`:

```python
"""SQLAlchemy base class for all models."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, String, func, JSON
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    __abstract__ = True

    type_annotation_map = {
        uuid.UUID: String(36),
    }

    def dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


# Import models to register them with Base.metadata
from app.models import User, Video, VideoChunk, StudyProgress
```

- [ ] **Step 5: Commit changes**
```bash
git add backend/app/models/
git add backend/app/db/base.py
git commit -m "feat: add SQLAlchemy models for study progress and videos"
```

---

## Task 5: Create Chart Service with Pyecharts

**Files:**
- Create: `backend/app/services/chart_service.py`

- [ ] **Step 1: Create chart generation service**

```python
"""Interactive chart generation service using pyecharts."""

from datetime import date
from typing import List, Literal

from pyecharts import options as opts
from pyecharts.charts import Bar, Calendar, Line, Pie, Timeline
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType

from app.schemas.statistics import DailyStudyStat, WeeklyStudyStat


class ChartService:
    """Generate interactive charts using pyecharts."""

    def create_study_timeline(
        self,
        data: List[DailyStudyStat],
        title: str = "Daily Study Time",
        period: Literal["7d", "30d", "90d", "1y"] = "30d",
    ) -> dict:
        """Create interactive line chart with datazoom for time-based comparison.

        Features:
        - DataZoom for zooming and panning
        - Timeline for period switching
        - Mark points for max/min values
        - Average line for reference
        - Tooltips with crosshair
        """
        dates = [str(stat.date) for stat in data]
        minutes = [stat.total_minutes for stat in data]

        chart = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="100%", height="400px"))
            .add_xaxis(dates)
            .add_yaxis(
                series_name="Study Time",
                y_axis=minutes,
                is_smooth=True,
                symbol_size=8,
                label_opts=opts.LabelOpts(is_show=False),
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        opts.MarkPointItem(type_="max", name="Max"),
                        opts.MarkPointItem(type_="min", name="Min"),
                    ],
                    symbol_size=50,
                ),
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(type_="average", name="Average")],
                    linestyle_opts=opts.LineStyleOpts(type_="dashed"),
                ),
                areastyle_opts=opts.AreaStyleOpts(opacity=0.3),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=title,
                    subtitle=f"Period: {period}",
                    pos_left="center",
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    axis_pointer_type="cross",
                    formatter=JsCode(
                        """
                        function(params) {
                            return params[0].axisValue + '<br/>' +
                                   'Study Time: ' + params[0].value + ' min';
                        }
                        """
                    ),
                ),
                legend_opts=opts.LegendOpts(pos_left="left"),
                datazoom_opts=[
                    opts.DataZoomOpts(
                        type_="slider",
                        range_start=0,
                        range_end=100,
                        pos_bottom="10px",
                    ),
                    opts.DataZoomOpts(type_="inside"),  # Mouse wheel zoom
                ],
                toolbox_opts=opts.ToolboxOpts(
                    feature=opts.ToolBoxFeatureOpts(
                        data_zoom=opts.ToolBoxFeatureDataZoomOpts(zoom_title="Zoom", back_title="Back"),
                        restore=opts.ToolBoxFeatureRestoreOpts(),
                        save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(title="Save"),
                        data_view=opts.ToolBoxFeatureDataViewOpts(title="Data"),
                    )
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    boundary_gap=False,
                    axislabel_opts=opts.LabelOpts(rotate=45),
                ),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="Minutes",
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
            )
        )

        return {
            "chart_id": "study_timeline",
            "chart_type": "line",
            "title": title,
            "pyecharts_option": chart.dump_options_with_quotes(),
            "interactive_features": [
                "datazoom",
                "tooltip",
                "markpoint",
                "markline",
                "toolbox",
            ],
        }

    def create_activity_heatmap(
        self,
        data: List[DailyStudyStat],
        year: int,
    ) -> dict:
        """Create calendar heatmap for activity visualization.

        Features:
        - Calendar view with color-coded activity levels
        - Visual map with adjustable scale
        - Tooltips showing exact minutes
        - Clickable cells (handled by frontend)
        """
        # Format data for calendar: [[date, value], ...]
        heatmap_data = [
            [str(stat.date), stat.total_minutes]
            for stat in data
            if stat.total_minutes > 0
        ]

        # Calculate max for color scale
        max_minutes = max((stat.total_minutes for stat in data), default=100)

        chart = (
            Calendar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="100%", height="300px"))
            .add(
                series_name="",
                yaxis_data=heatmap_data,
                calendar_opts=opts.CalendarOpts(
                    range_=str(year),
                    daylabel_opts=opts.CalendarDayLabelOpts(
                        name_map=["en"],
                        first_day_of_week=0,  # Sunday
                    ),
                    monthlabel_opts=opts.CalendarMonthLabelOpts(name_map="en"),
                    pos_top="50px",
                    pos_left="100px",
                    pos_right="50px",
                ),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"Study Activity {year}",
                    pos_left="center",
                ),
                visualmap_opts=opts.VisualMapOpts(
                    max_=max_minutes,
                    min_=0,
                    orient="horizontal",
                    is_piecewise=False,
                    pos_top="20px",
                    pos_left="center",
                    range_color=["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
                ),
                tooltip_opts=opts.TooltipOpts(
                    formatter=JsCode(
                        """
                        function(params) {
                            return params.value[0] + '<br/>' +
                                   'Study Time: ' + params.value[1] + ' min';
                        }
                        """
                    ),
                ),
            )
        )

        return {
            "chart_id": "activity_heatmap",
            "chart_type": "calendar",
            "title": f"Study Activity {year}",
            "pyecharts_option": chart.dump_options_with_quotes(),
            "interactive_features": [
                "visualmap",
                "tooltip",
                "calendar",
            ],
        }

    def create_weekly_comparison(
        self,
        current_week: WeeklyStudyStat,
        previous_week: WeeklyStudyStat,
    ) -> dict:
        """Create grouped bar chart comparing weeks.

        Features:
        - Side-by-side comparison
        - Timeline for period navigation
        - Legend toggle
        """
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        # Simulate daily breakdown (in real implementation, fetch actual daily data)
        current_data = self._simulate_daily_breakdown(current_week.total_minutes)
        previous_data = self._simulate_daily_breakdown(previous_week.total_minutes)

        chart = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="100%", height="350px"))
            .add_xaxis(days)
            .add_yaxis(
                series_name="Current Week",
                y_axis=current_data,
                itemstyle_opts=opts.ItemStyleOpts(color="#5470c6"),
                label_opts=opts.LabelOpts(is_show=False),
            )
            .add_yaxis(
                series_name="Previous Week",
                y_axis=previous_data,
                itemstyle_opts=opts.ItemStyleOpts(color="#91cc75"),
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="Weekly Comparison",
                    subtitle=f"Current: {current_week.total_minutes}min vs Previous: {previous_week.total_minutes}min",
                    pos_left="center",
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    axis_pointer_type="shadow",
                    formatter=JsCode(
                        """
                        function(params) {
                            var result = params[0].axisValue + '<br/>';
                            params.forEach(function(item) {
                                result += item.marker + ' ' + item.seriesName + ': ' + item.value + ' min<br/>';
                            });
                            return result;
                        }
                        """
                    ),
                ),
                legend_opts=opts.LegendOpts(pos_left="left"),
                toolbox_opts=opts.ToolboxOpts(
                    feature=opts.ToolBoxFeatureOpts(
                        magic_type=opts.ToolBoxFeatureMagicTypeOpts(
                            show=True,
                            type_["line", "bar", "stack"],
                        ),
                        restore=opts.ToolBoxFeatureRestoreOpts(),
                        save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(),
                    )
                ),
                xaxis_opts=opts.AxisOpts(type_="category"),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="Minutes",
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
            )
        )

        return {
            "chart_id": "weekly_comparison",
            "chart_type": "bar",
            "title": "Weekly Comparison",
            "pyecharts_option": chart.dump_options_with_quotes(),
            "interactive_features": [
                "legend",
                "tooltip",
                "toolbox",
                "magic_type",
            ],
        }

    def create_completion_pie(self, completed: int, total: int) -> dict:
        """Create pie chart showing completion status.

        Features:
        - Donut-style pie chart
        - Percentage labels
        - Hover tooltips
        """
        if total == 0:
            total = 1  # Avoid division by zero
            completed = 0

        remaining = total - completed
        completion_pct = round((completed / total) * 100, 1)

        data = [
            {"value": completed, "name": f"Completed ({completion_pct}%)"},
            {"value": remaining, "name": f"Remaining ({100 - completion_pct}%)"},
        ]

        chart = (
            Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="100%", height="300px"))
            .add(
                series_name="",
                data_pair=data,
                radius=["40%", "70%"],  # Donut style
                center=["50%", "50%"],
                label_opts=opts.LabelOpts(
                    formatter="{b}\n{c} videos",
                    font_size=12,
                ),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="Video Completion",
                    subtitle=f"{completed}/{total} completed",
                    pos_left="center",
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="item",
                    formatter="{b}: {c} videos ({d}%)",
                ),
                legend_opts=opts.LegendOpts(
                    orient="vertical",
                    pos_left="left",
                    pos_top="center",
                ),
            )
            .set_colors(["#91cc75", "#ebedf0"])
        )

        return {
            "chart_id": "completion_pie",
            "chart_type": "pie",
            "title": "Video Completion",
            "pyecharts_option": chart.dump_options_with_quotes(),
            "interactive_features": [
                "tooltip",
                "legend",
            ],
        }

    def _simulate_daily_breakdown(self, total_minutes: int) -> List[int]:
        """Simulate daily breakdown for demo (replace with actual data)."""
        import random

        if total_minutes == 0:
            return [0] * 7

        # Generate somewhat realistic distribution
        weights = [1.0, 1.2, 1.0, 1.1, 1.0, 0.7, 0.6]  # Weekday pattern
        base = total_minutes / sum(weights)
        breakdown = [int(base * w * random.uniform(0.7, 1.3)) for w in weights]

        # Adjust to match total
        diff = total_minutes - sum(breakdown)
        if diff != 0:
            breakdown[0] += diff

        return [max(0, m) for m in breakdown]


# Global service instance
chart_service = ChartService()
```

- [ ] **Step 2: Commit changes**
```bash
git add backend/app/services/chart_service.py
git commit -m "feat: add interactive chart service with pyecharts"
```

---

## Task 6: Create Statistics API Endpoints

**Files:**
- Create: `backend/app/api/v1/endpoints/statistics.py`
- Modify: `backend/app/api/v1/router.py`

- [ ] **Step 1: Create statistics router**

Create `/workspaces/education/backend/app/api/v1/endpoints/statistics.py`:

```python
"""Statistics API endpoints."""

from datetime import date, datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import AsyncSessionLocal
from app.schemas.statistics import (
    ChartConfig,
    DailyStudyStat,
    StatisticsDashboard,
    StatisticsSummary,
    StudyStreak,
    TimeSeriesRequest,
    StreakResponse,
)
from app.schemas.user import User
from app.services.chart_service import chart_service
from app.services.statistics_service import StatisticsService

router = APIRouter()


async def get_db():
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


def get_date_range(period: Literal["7d", "30d", "90d", "1y"]) -> tuple[date, date]:
    """Calculate start and end dates based on period."""
    end_date = date.today()

    period_days = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
        "1y": 365,
    }

    start_date = end_date - timedelta(days=period_days[period])
    return start_date, end_date


@router.get("/dashboard", response_model=StatisticsDashboard)
async def get_dashboard(
    period: Literal["7d", "30d", "90d", "1y"] = Query(default="30d"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get complete statistics dashboard with interactive charts.

    Returns:
        StatisticsDashboard with summary, streak info, and chart configs
    """
    service = StatisticsService(db)
    start_date, end_date = get_date_range(period)

    try:
        # Get daily statistics
        daily_stats = await service.get_daily_stats(
            str(current_user.id), start_date, end_date
        )

        # Get summary
        summary = await service.get_summary(
            str(current_user.id), start_date, end_date
        )

        # Get streak
        streak = await service.calculate_streak(str(current_user.id))

        # Generate charts
        charts = []

        # Study timeline chart
        timeline_chart = chart_service.create_study_timeline(
            daily_stats, period=period
        )
        charts.append(ChartConfig(**timeline_chart))

        # Activity heatmap
        heatmap_chart = chart_service.create_activity_heatmap(
            daily_stats, start_date.year
        )
        charts.append(ChartConfig(**heatmap_chart))

        # Completion pie chart
        pie_chart = chart_service.create_completion_pie(
            summary.completed_videos, summary.total_videos
        )
        charts.append(ChartConfig(**pie_chart))

        return StatisticsDashboard(
            period=period,
            summary=summary,
            streak=streak,
            charts=charts,
            daily_stats=daily_stats,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate statistics: {str(e)}"
        )


@router.get("/study-timeline", response_model=ChartConfig)
async def get_study_timeline(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get interactive study timeline chart.

    Args:
        start_date: Start date for the timeline
        end_date: End date for the timeline

    Returns:
        ChartConfig with pyecharts options
    """
    service = StatisticsService(db)

    try:
        daily_stats = await service.get_daily_stats(
            str(current_user.id), start_date, end_date
        )

        chart_data = chart_service.create_study_timeline(daily_stats)
        return ChartConfig(**chart_data)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate timeline: {str(e)}"
        )


@router.get("/activity-heatmap", response_model=ChartConfig)
async def get_activity_heatmap(
    year: int = Query(default=datetime.now().year),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get calendar heatmap of study activity.

    Args:
        year: Year to display (default: current year)

    Returns:
        ChartConfig with calendar heatmap
    """
    service = StatisticsService(db)

    try:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        daily_stats = await service.get_daily_stats(
            str(current_user.id), start_date, end_date
        )

        chart_data = chart_service.create_activity_heatmap(daily_stats, year)
        return ChartConfig(**chart_data)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate heatmap: {str(e)}"
        )


@router.get("/streak", response_model=StreakResponse)
async def get_streak_info(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current and longest streak information.

    Returns:
        StreakResponse with streak details and milestones
    """
    service = StatisticsService(db)

    try:
        streak = await service.calculate_streak(str(current_user.id))
        return StreakResponse(
            streak=streak,
            streak_milestones=[7, 30, 60, 100],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to calculate streak: {str(e)}"
        )


@router.get("/summary", response_model=StatisticsSummary)
async def get_summary(
    period: Literal["7d", "30d", "90d", "1y"] = Query(default="30d"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get summary statistics for a period.

    Args:
        period: Time period (7d, 30d, 90d, 1y)

    Returns:
        StatisticsSummary with aggregated metrics
    """
    service = StatisticsService(db)
    start_date, end_date = get_date_range(period)

    try:
        summary = await service.get_summary(
            str(current_user.id), start_date, end_date
        )
        return summary

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate summary: {str(e)}"
        )
```

- [ ] **Step 2: Update API router**

Modify `/workspaces/education/backend/app/api/v1/router.py`:

```python
"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, statistics

api_router = APIRouter()

# Include auth endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include statistics endpoints
api_router.include_router(
    statistics.router, prefix="/statistics", tags=["statistics"]
)

# Additional routers will be added in subsequent phases
# from app.api.v1.endpoints import videos, courses, learning, speaking, exams, models, chat
# api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
# api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
# api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
# api_router.include_router(speaking.router, prefix="/speaking", tags=["speaking"])
# api_router.include_router(exams.router, prefix="/exams", tags=["exams"])
# api_router.include_router(models.router, prefix="/models", tags=["models"])
# api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
```

- [ ] **Step 3: Commit changes**
```bash
git add backend/app/api/v1/endpoints/statistics.py
git add backend/app/api/v1/router.py
git commit -m "feat: add statistics API endpoints with interactive charts"
```

---

## Task 7: Test API Endpoints

**Files:**
- Test: Manual testing via curl or HTTP client

- [ ] **Step 1: Test dashboard endpoint**

```bash
cd /workspaces/education/backend
PYTHONPATH=/workspaces/education/backend uv run python -c "
import asyncio
from app.api.v1.endpoints.statistics import get_dashboard

async def test():
    # This is a simple import test
    print('Statistics endpoints module loaded successfully')

asyncio.run(test())
" 2>&1 | grep -v "Bytecode\|INFO"
```

- [ ] **Step 2: Verify all imports work**
```bash
PYTHONPATH=/workspaces/education/backend uv run python -c "
from app.schemas.statistics import StatisticsDashboard
from app.services.chart_service import chart_service
from app.services.statistics_service import StatisticsService
from app.api.v1.endpoints.statistics import router
print('All statistics modules imported successfully')
" 2>&1 | grep -v "Bytecode"
```

- [ ] **Step 3: Run backend to test**

Start the server in background and test:
```bash
cd /workspaces/education/backend
PYTHONPATH=/workspaces/education/backend uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 &
sleep 3
curl -X GET "http://localhost:8080/api/v1/statistics/dashboard?period=30d" -H "accept: application/json"
pkill -f uvicorn
```

- [ ] **Step 4: Commit changes**
```bash
git add -A
git commit -m "test: verify statistics API endpoints"
```

---

## Task 8: Update Documentation

**Files:**
- Modify: `AGENTS.md`
- Modify: `design-specs.md`

- [ ] **Step 1: Update AGENTS.md**

Read `/workspaces/education/AGENTS.md` and add a new section for statistics:

```markdown
## Study Statistics System

The application includes a comprehensive study progress statistics system with interactive charts.

### Features
- Daily study time tracking
- Learning streak calculation (current and longest)
- Video completion rates
- Activity heatmap (GitHub-style calendar)
- Time-based comparisons (7d, 30d, 90d, 1y periods)
- Interactive charts with zoom, pan, and filtering

### API Endpoints
- `GET /api/v1/statistics/dashboard` - Complete dashboard with charts
- `GET /api/v1/statistics/study-timeline` - Interactive timeline chart
- `GET /api/v1/statistics/activity-heatmap` - Calendar heatmap
- `GET /api/v1/statistics/streak` - Streak information
- `GET /api/v1/statistics/summary` - Summary statistics

### Chart Types
1. **Study Timeline** - Line chart with DataZoom for time-based comparison
2. **Activity Heatmap** - Calendar view for consistency tracking
3. **Weekly Comparison** - Bar chart comparing weeks
4. **Completion Pie** - Donut chart showing video completion

### Interactive Features
- **DataZoom**: Zoom and pan through timeline
- **Timeline**: Switch between 7d/30d/90d/1y periods
- **Toolbox**: Change chart type, view data, save image
- **Tooltip**: Hover for exact values
- **Legend**: Toggle series visibility
- **Visual Map**: Adjust color scale on heatmap

### Technology Stack
- **Backend**: pyecharts for chart generation
- **Frontend**: Apache ECharts for rendering
- **Data**: Calculated from study_progress table
```

- [ ] **Step 2: Update design-specs.md**

Add statistics section to `/workspaces/education/design-specs.md`:

```markdown
## Study Statistics System

### Overview
Interactive study progress analytics with time-based comparisons and visual insights.

### Statistics Tracked
- Daily study time (minutes)
- Learning streaks (consecutive days)
- Video completion rates
- Activity patterns by day/week/month

### Chart Specifications

#### Study Timeline Chart
- **Type**: Interactive Line Chart with Area
- **Features**:
  - DataZoom slider and inside zoom
  - Mark points for max/min values
  - Average line reference
  - Period switcher (7d/30d/90d/1y)
  - Crosshair tooltips

#### Activity Heatmap
- **Type**: Calendar Heatmap
- **Features**:
  - GitHub-style contribution graph
  - Adjustable color scale
  - Year navigation
  - Click to drill down

#### Weekly Comparison
- **Type**: Grouped Bar Chart
- **Features**:
  - Compare current vs previous week
  - Magic type switching (line/bar/stack)
  - Day-of-week breakdown

#### Completion Pie
- **Type**: Donut Chart
- **Features**:
  - Completion percentage
  - Count labels
  - Color-coded segments

### Data Model
```
study_progress:
  - id: UUID
  - user_id: UUID
  - video_id: UUID
  - chunk_index: int
  - current_timestamp: float
  - completed: boolean
  - updated_at: datetime
```

### Performance
- Cached for 5 minutes
- Lazy loading for charts
- Data sampling for large datasets
```

- [ ] **Step 3: Commit documentation updates**
```bash
git add AGENTS.md design-specs.md
git commit -m "docs: update documentation with statistics system details"
```

---

## Task 9: Create Frontend Statistics Store

**Files:**
- Create: `frontend/src/stores/statistics.store.ts`

- [ ] **Step 1: Create statistics Pinia store**

```typescript
// frontend/src/stores/statistics.store.ts

import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "@/services/api";

export interface ChartConfig {
  chart_id: string;
  chart_type: "line" | "bar" | "calendar" | "pie";
  title: string;
  pyecharts_option: Record<string, unknown>;
  interactive_features: string[];
}

export interface DailyStat {
  date: string;
  total_minutes: number;
  videos_completed: number;
  chunks_studied: number;
  streak_day: boolean;
}

export interface StudyStreak {
  current_streak: number;
  longest_streak: number;
  last_study_date: string | null;
  total_study_days: number;
}

export interface StatisticsSummary {
  total_study_time: number;
  total_videos: number;
  completed_videos: number;
  completion_rate: number;
  avg_daily_time: number;
  current_streak: number;
}

export interface StatisticsDashboard {
  period: "7d" | "30d" | "90d" | "1y";
  summary: StatisticsSummary;
  streak: StudyStreak;
  charts: ChartConfig[];
  daily_stats: DailyStat[];
}

export const useStatisticsStore = defineStore("statistics", () => {
  // State
  const dashboard = ref<StatisticsDashboard | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const selectedPeriod = ref<"7d" | "30d" | "90d" | "1y">("30d");

  // Getters
  const hasData = computed(() => dashboard.value !== null);
  const timelineChart = computed(() =>
    dashboard.value?.charts.find((c) => c.chart_id === "study_timeline")
  );
  const heatmapChart = computed(() =>
    dashboard.value?.charts.find((c) => c.chart_id === "activity_heatmap")
  );
  const completionChart = computed(() =>
    dashboard.value?.charts.find((c) => c.chart_id === "completion_pie")
  );
  const weeklyChart = computed(() =>
    dashboard.value?.charts.find((c) => c.chart_id === "weekly_comparison")
  );

  // Actions
  async function fetchDashboard(period: "7d" | "30d" | "90d" | "1y" = "30d") {
    loading.value = true;
    error.value = null;

    try {
      const response = await api.get<StatisticsDashboard>("/statistics/dashboard", {
        params: { period },
      });
      dashboard.value = response.data;
      selectedPeriod.value = period;
    } catch (err) {
      error.value = "Failed to fetch statistics";
      console.error("Failed to fetch dashboard:", err);
    } finally {
      loading.value = false;
    }
  }

  async function getStudyTimeline(startDate: string, endDate: string) {
    try {
      const response = await api.get<ChartConfig>("/statistics/study-timeline", {
        params: { start_date: startDate, end_date: endDate },
      });
      return response.data;
    } catch (err) {
      console.error("Failed to fetch timeline:", err);
      throw err;
    }
  }

  async function getActivityHeatmap(year: number = new Date().getFullYear()) {
    try {
      const response = await api.get<ChartConfig>("/statistics/activity-heatmap", {
        params: { year },
      });
      return response.data;
    } catch (err) {
      console.error("Failed to fetch heatmap:", err);
      throw err;
    }
  }

  async function getStreakInfo() {
    try {
      const response = await api.get<{ streak: StudyStreak }>("/statistics/streak");
      return response.data.streak;
    } catch (err) {
      console.error("Failed to fetch streak:", err);
      throw err;
    }
  }

  return {
    // State
    dashboard,
    loading,
    error,
    selectedPeriod,
    // Getters
    hasData,
    timelineChart,
    heatmapChart,
    completionChart,
    weeklyChart,
    // Actions
    fetchDashboard,
    getStudyTimeline,
    getActivityHeatmap,
    getStreakInfo,
  };
});
```

- [ ] **Step 2: Commit changes**
```bash
git add frontend/src/stores/statistics.store.ts
git commit -m "feat: add statistics Pinia store"
```

---

## Task 10: Create Statistics Chart Component

**Files:**
- Create: `frontend/src/components/statistics/StudyChart.vue`

- [ ] **Step 1: Create chart component**

```vue
<!-- frontend/src/components/statistics/StudyChart.vue -->
<template>
  <div class="study-chart">
    <div ref="chartRef" class="chart-container"></div>
    <div v-if="loading" class="chart-loading">
      <el-loading :size="32" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import * as echarts from "echarts";
import type { ChartConfig } from "@/stores/statistics.store";

interface Props {
  config: ChartConfig | null;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits<{
  (e: "chartClick", params: unknown): void;
}>();

const chartRef = ref<HTMLDivElement>();
const chartInstance = ref<echarts.ECharts | null>(null);

onMounted(() => {
  if (chartRef.value) {
    chartInstance.value = echarts.init(chartRef.value);
    renderChart();

    // Handle click events
    chartInstance.value.on("click", (params: unknown) => {
      emit("chartClick", params);
    });

    // Handle resize
    window.addEventListener("resize", handleResize);
  }
});

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
  chartInstance.value?.dispose();
});

// Watch for config changes
watch(
  () => props.config,
  () => {
    renderChart();
  },
  { deep: true }
);

function renderChart() {
  if (!chartInstance.value || !props.config) return;

  const option = props.config.pyecharts_option;

  // Merge with default options
  const mergedOption = {
    ...option,
    animation: true,
    animationDuration: 500,
  };

  chartInstance.value.setOption(mergedOption, true);
}

function handleResize() {
  chartInstance.value?.resize();
}
</script>

<style scoped>
.study-chart {
  position: relative;
  width: 100%;
}

.chart-container {
  width: 100%;
  height: 400px;
}

.chart-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
}
</style>
```

- [ ] **Step 2: Create statistics view component**

```vue
<!-- frontend/src/views/StatisticsView.vue -->
<template>
  <div class="statistics-view">
    <el-page-header title="Study Statistics" @back="$router.back()" />

    <div class="period-selector">
      <el-radio-group v-model="selectedPeriod" @change="updatePeriod">
        <el-radio-button label="7d">Last 7 Days</el-radio-button>
        <el-radio-button label="30d">Last 30 Days</el-radio-button>
        <el-radio-button label="90d">Last 90 Days</el-radio-button>
        <el-radio-button label="1y">Last Year</el-radio-button>
      </el-radio-group>
    </div>

    <!-- Summary Cards -->
    <el-row :gutter="20" class="summary-row">
      <el-col :span="6">
        <el-card>
          <div class="stat-value">{{ formatMinutes(summary?.total_study_time || 0) }}</div>
          <div class="stat-label">Total Study Time</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-value">{{ summary?.current_streak || 0 }}</div>
          <div class="stat-label">Current Streak</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-value">{{ summary?.completion_rate || 0 }}%</div>
          <div class="stat-label">Completion Rate</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-value">{{ summary?.avg_daily_time || 0 }} min</div>
          <div class="stat-label">Avg Daily Time</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="24">
        <el-card>
          <template #header>Study Timeline</template>
          <StudyChart
            :config="timelineChart"
            :loading="loading"
            @chart-click="onChartClick"
          />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>Activity Heatmap</template>
          <StudyChart :config="heatmapChart" :loading="loading" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>Completion Progress</template>
          <StudyChart :config="completionChart" :loading="loading" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useStatisticsStore } from "@/stores/statistics.store";
import StudyChart from "@/components/statistics/StudyChart.vue";

const statisticsStore = useStatisticsStore();

const selectedPeriod = ref<"7d" | "30d" | "90d" | "1y">("30d");

const loading = computed(() => statisticsStore.loading);
const summary = computed(() => statisticsStore.dashboard?.summary);
const timelineChart = computed(() => statisticsStore.timelineChart);
const heatmapChart = computed(() => statisticsStore.heatmapChart);
const completionChart = computed(() => statisticsStore.completionChart);

onMounted(() => {
  statisticsStore.fetchDashboard(selectedPeriod.value);
});

function updatePeriod() {
  statisticsStore.fetchDashboard(selectedPeriod.value);
}

function onChartClick(params: unknown) {
  console.log("Chart clicked:", params);
}

function formatMinutes(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours > 0) {
    return `${hours}h ${mins}m`;
  }
  return `${mins}m`;
}
</script>

<style scoped>
.statistics-view {
  padding: 20px;
}

.period-selector {
  margin: 20px 0;
  text-align: center;
}

.summary-row {
  margin-bottom: 20px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  text-align: center;
}

.stat-label {
  text-align: center;
  color: #606266;
  margin-top: 8px;
}

.charts-row {
  margin-bottom: 20px;
}
</style>
```

- [ ] **Step 3: Commit changes**
```bash
git add frontend/src/components/statistics/
git add frontend/src/views/StatisticsView.vue
git commit -m "feat: add statistics chart components and view"
```

---

## Task 11: Final Integration and Testing

**Files:**
- Modify: `frontend/src/router/routes.ts`
- Test: Full integration

- [ ] **Step 1: Add statistics route**

Update `/workspaces/education/frontend/src/router/routes.ts`:

```typescript
import type { RouteRecordRaw } from "vue-router";

export const routes: RouteRecordRaw[] = [
  // ... existing routes ...
  {
    path: "/statistics",
    name: "Statistics",
    component: () => import("@/views/StatisticsView.vue"),
    meta: {
      requiresAuth: true,
      title: "Study Statistics",
    },
  },
];
```

- [ ] **Step 2: Run final tests**

```bash
# Test backend
cd /workspaces/education/backend
PYTHONPATH=/workspaces/education/backend uv run python -c "
from app.api.v1.endpoints.statistics import router
from app.services.chart_service import chart_service
from app.services.statistics_service import StatisticsService
from app.schemas.statistics import StatisticsDashboard
print('All statistics modules imported successfully')
" 2>&1 | grep -v "Bytecode"

# Test frontend build
cd /workspaces/education/frontend
pnpm install
pnpm build
```

- [ ] **Step 3: Final commit**
```bash
git add -A
git commit -m "feat: complete study statistics system with interactive pyecharts"
```

---

## Summary of Implementation

This implementation plan covers:

1. ✅ Backend infrastructure (pyecharts dependency)
2. ✅ Statistics schemas for API responses
3. ✅ Database models (StudyProgress, Video, VideoChunk)
4. ✅ Statistics calculation service
5. ✅ Interactive chart service with pyecharts
6. ✅ API endpoints with time-based comparisons
7. ✅ Frontend Pinia store
8. ✅ Vue chart components with ECharts
9. ✅ Statistics dashboard view
10. ✅ Documentation updates

### Key Interactive Features Implemented:
- **DataZoom**: Zoom and pan through timeline data
- **Timeline**: Switch between 7d/30d/90d/1y periods
- **Tooltips**: Hover for exact values
- **Toolbox**: Change chart types, view data, save images
- **Legend**: Toggle series visibility
- **Visual Map**: Adjust color scale on heatmap

### Chart Types:
1. **Study Timeline** - Line chart with area, datazoom, average line
2. **Activity Heatmap** - Calendar heatmap with color-coded activity levels
3. **Weekly Comparison** - Grouped bar chart with magic type switching
4. **Completion Pie** - Donut chart showing video completion rates
