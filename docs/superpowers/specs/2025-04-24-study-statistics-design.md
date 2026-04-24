# Study Progress Statistics Design Document

**Date:** 2025-04-24
**Feature:** Study Progress Analytics with Interactive Charts
**Status:** Draft

---

## Overview

Add comprehensive study progress statistics functionality with interactive charts using pyecharts. Users can visualize their learning patterns, track study time, monitor completion rates, and analyze consistency through time-based comparisons.

---

## Goals

1. **Track Study Metrics:** Daily study time, video completion rates, learning streaks
2. **Visualize Trends:** Interactive charts showing learning patterns over time
3. **Enable Time Comparisons:** Compare daily, weekly, and monthly statistics
4. **Support Interactivity:** Zoom, pan, toggle, and drill-down capabilities
5. **Provide Insights:** Help users understand and improve their learning habits

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Vue 3)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  ECharts    │  │  Dashboard  │  │  Period Selector    │ │
│  │  Component  │  │  View       │  │  (7d/30d/90d/1y)   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────────┼────────────┘
          │                │                    │
          └────────────────┴────────────────────┘
                           │
                           ▼ HTTP GET /api/v1/statistics/*
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                       │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐│
│  │  Statistics   │  │  Pyecharts    │  │  Data Aggregation ││
│  │  API Router   │──│  Chart Gen    │──│  Service         ││
│  └───────────────┘  └───────────────┘  └────────┬─────────┘│
└───────────────────────────────────────────────────┼──────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database (SQLite)                       │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  study_progress  │  videos  │  courses  │  users       │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Request:** Frontend requests statistics for a time period
2. **Data Query:** Backend queries SQLite for relevant progress data
3. **Aggregation:** Service aggregates raw data into time-series metrics
4. **Chart Generation:** Pyecharts generates interactive ECharts configs
5. **Response:** JSON with chart configurations and raw data
6. **Rendering:** Frontend renders ECharts with interactivity

---

## Data Models

### Statistics Schema

```python
# app/schemas/statistics.py

from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class DailyStudyStat(BaseModel):
    """Daily study statistics."""
    date: date
    total_minutes: int
    videos_completed: int
    chunks_studied: int
    streak_day: bool  # Has activity on this day


class WeeklyStudyStat(BaseModel):
    """Weekly aggregated statistics."""
    week_start: date
    week_end: date
    total_minutes: int
    avg_daily_minutes: float
    days_studied: int
    videos_completed: int


class StudyStreak(BaseModel):
    """Current and historical streak information."""
    current_streak: int  # Consecutive days with activity
    longest_streak: int
    last_study_date: Optional[date]
    total_study_days: int


class VideoProgressStat(BaseModel):
    """Progress statistics for a video."""
    video_id: str
    title: str
    total_chunks: int
    completed_chunks: int
    progress_percentage: float
    last_studied: Optional[datetime]
    total_time_spent: int  # Minutes


class ChartConfig(BaseModel):
    """Interactive chart configuration from pyecharts."""
    chart_id: str
    chart_type: str  # line, bar, calendar, etc.
    title: str
    pyecharts_option: dict  # Full ECharts option object
    interactive_features: List[str]  # datazoom, timeline, brush, etc.


class StatisticsDashboard(BaseModel):
    """Complete dashboard response."""
    period: str  # 7d, 30d, 90d, 1y
    summary: dict  # Quick stats: total time, completion rate, etc.
    streak: StudyStreak
    charts: List[ChartConfig]
    daily_stats: List[DailyStudyStat]
```

---

## API Endpoints

### Statistics Router

```python
# app/api/v1/endpoints/statistics.py

from fastapi import APIRouter, Depends, Query
from typing import Literal

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/dashboard")
async def get_dashboard(
    period: Literal["7d", "30d", "90d", "1y"] = Query(default="30d"),
    current_user: User = Depends(get_current_user),
) -> StatisticsDashboard:
    """Get complete statistics dashboard with interactive charts."""


@router.get("/study-timeline")
async def get_study_timeline(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(get_current_user),
) -> ChartConfig:
    """Get interactive study timeline chart."""


@router.get("/activity-heatmap")
async def get_activity_heatmap(
    year: int = Query(default=datetime.now().year),
    current_user: User = Depends(get_current_user),
) -> ChartConfig:
    """Get calendar heatmap of study activity."""


@router.get("/video-progress")
async def get_video_progress(
    current_user: User = Depends(get_current_user),
) -> List[VideoProgressStat]:
    """Get progress statistics for all videos."""


@router.get("/streak")
async def get_streak_info(
    current_user: User = Depends(get_current_user),
) -> StudyStreak:
    """Get current and longest streak information."""
```

---

## Interactive Charts Specification

### Chart 1: Study Timeline (Line/Area with DataZoom)

**Purpose:** Visualize daily study time over a period with zoom/pan capabilities

**Configuration:**
```python
{
    "chart_type": "line",
    "title": "Daily Study Time",
    "x_axis": "date",
    "y_axis": "minutes",
    "interactive_features": [
        "datazoom",      # Zoom and pan
        "timeline",      # Period switcher (7d/30d/90d/1y)
        "tooltip",       # Hover details
        "brush",         # Range selection
        "toolbox",       # Chart type switch
    ],
    "series": [
        {
            "name": "Study Time",
            "type": "line",
            "smooth": True,
            "areaStyle": {"opacity": 0.3},
            "markPoint": {
                "data": [
                    {"type": "max", "name": "Max"},
                    {"type": "min", "name": "Min"},
                ]
            },
            "markLine": {
                "data": [{"type": "average", "name": "Average"}]
            },
        }
    ],
    "datazoom": [
        {
            "type": "slider",
            "show": True,
            "start": 0,
            "end": 100,
        },
        {
            "type": "inside",  # Mouse wheel zoom
        },
    ],
}
```

**Time Comparison Feature:**
- Timeline buttons: 7d, 30d, 90d, 1y
- Switching updates data and maintains zoom state
- Compare mode: overlay multiple periods

### Chart 2: Activity Heatmap (Calendar View)

**Purpose:** GitHub-style activity visualization for consistency tracking

**Configuration:**
```python
{
    "chart_type": "calendar",
    "title": "Study Activity",
    "range": "2025",  # Full year
    "visual_map": {
        "min": 0,
        "max": 300,  # Max minutes per day
        "calculable": True,
        "orient": "horizontal",
        "color": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
    },
    "interactive_features": [
        "tooltip",       # Show minutes on hover
        "click",         # Drill down to day detail
        "visual_map",    # Adjust color scale
    ],
}
```

### Chart 3: Weekly Comparison (Grouped Bar with Timeline)

**Purpose:** Compare study patterns across different weeks

**Configuration:**
```python
{
    "chart_type": "bar",
    "title": "Weekly Study Comparison",
    "x_axis": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "interactive_features": [
        "timeline",      # Switch between weeks
        "legend",        # Toggle week display
        "tooltip",       # Compare values
        "toolbox",       # Switch to line chart
    ],
    "series": [
        {"name": "Current Week", "type": "bar", "data": [...]},
        {"name": "Previous Week", "type": "bar", "data": [...]},
    ],
    "timeline": {
        "data": ["Week 1", "Week 2", "Week 3", "Week 4"],
        "playable": True,
        "autoPlay": False,
    },
}
```

### Chart 4: Video Progress (Horizontal Bar)

**Purpose:** Show completion percentage for each video

**Configuration:**
```python
{
    "chart_type": "bar",
    "title": "Video Completion Progress",
    "x_axis": "percentage",
    "y_axis": "video_title",
    "direction": "horizontal",
    "interactive_features": [
        "datazoom_y",    # Scroll through videos
        "tooltip",       # Show exact progress
        "click",         # Navigate to video
    ],
    "series": [{
        "name": "Completion %",
        "type": "bar",
        "itemStyle": {
            "color": {
                "type": "linear",
                "x": 0, "y": 0, "x2": 1, "y2": 0,
                "colorStops": [
                    {"offset": 0, "color": "#83bff6"},
                    {"offset": 0.5, "color": "#188df0"},
                    {"offset": 1, "color": "#188df0"},
                ],
            }
        },
    }],
}
```

---

## Pyecharts Integration

### Chart Generation Service

```python
# app/services/chart_service.py

from pyecharts.charts import Line, Calendar, Bar, Timeline
from pyecharts import options as opts
from pyecharts.globals import ThemeType


class ChartService:
    """Generate interactive charts using pyecharts."""
    
    def create_study_timeline(
        self,
        data: List[DailyStudyStat],
        title: str = "Study Timeline",
    ) -> dict:
        """Create interactive line chart with datazoom."""
        
        dates = [str(stat.date) for stat in data]
        minutes = [stat.total_minutes for stat in data]
        
        chart = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add_xaxis(dates)
            .add_yaxis(
                "Study Time (minutes)",
                minutes,
                is_smooth=True,
                symbol_size=8,
                label_opts=opts.LabelOpts(is_show=False),
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        opts.MarkPointItem(type_="max", name="Max"),
                        opts.MarkPointItem(type_="min", name="Min"),
                    ]
                ),
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(type_="average", name="Avg")]
                ),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    axis_pointer_type="cross",
                    formatter="{b}<br/>{a}: {c} min",
                ),
                datazoom_opts=[
                    opts.DataZoomOpts(type_="slider", range_start=0, range_end=100),
                    opts.DataZoomOpts(type_="inside"),
                ],
                toolbox_opts=opts.ToolboxOpts(
                    feature=opts.ToolBoxFeatureOpts(
                        data_zoom=opts.ToolBoxFeatureDataZoomOpts(zoom_title="Zoom"),
                        restore=opts.ToolBoxFeatureRestoreOpts(),
                        save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(),
                        data_view=opts.ToolBoxFeatureDataViewOpts(),
                    )
                ),
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
                yaxis_opts=opts.AxisOpts(type_="value", name="Minutes"),
            )
        )
        
        return chart.dump_options_with_quotes()
    
    def create_activity_heatmap(
        self,
        data: List[DailyStudyStat],
        year: int,
    ) -> dict:
        """Create calendar heatmap."""
        
        # Format: [[date, value], ...]
        heatmap_data = [
            [str(stat.date), stat.total_minutes]
            for stat in data
        ]
        
        chart = (
            Calendar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add(
                "",
                heatmap_data,
                calendar_opts=opts.CalendarOpts(
                    range_=str(year),
                    daylabel_opts=opts.CalendarDayLabelOpts(name_map="en"),
                    monthlabel_opts=opts.CalendarMonthLabelOpts(name_map="en"),
                ),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"Study Activity {year}"),
                visualmap_opts=opts.VisualMapOpts(
                    max_=300,
                    min_=0,
                    orient="horizontal",
                    is_piecewise=False,
                    pos_top="230px",
                    pos_left="100px",
                ),
                tooltip_opts=opts.TooltipOpts(
                    formatter="{c} minutes on {b}",
                ),
            )
        )
        
        return chart.dump_options_with_quotes()
```

---

## Statistics Calculation Logic

### Study Time Aggregation

```python
# app/services/statistics_service.py

from datetime import date, datetime, timedelta
from typing import List, Dict
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.statistics import DailyStudyStat, StudyStreak


class StatisticsService:
    """Calculate study statistics from database."""
    
    async def get_daily_stats(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
    ) -> List[DailyStudyStat]:
        """Aggregate study time per day."""
        
        query = (
            select(
                func.date(func.datetime(study_progress.c.updated_at, 'unixepoch')).label("date"),
                func.sum(study_progress.c.current_timestamp - video_chunks.c.start_time).label("minutes"),
                func.count(func.distinct(study_progress.c.video_id)).label("videos"),
                func.count(study_progress.c.chunk_index).label("chunks"),
            )
            .select_from(study_progress.join(video_chunks))
            .where(
                and_(
                    study_progress.c.user_id == user_id,
                    study_progress.c.updated_at >= start_date,
                    study_progress.c.updated_at <= end_date,
                )
            )
            .group_by("date")
            .order_by("date")
        )
        
        result = await db.execute(query)
        return [
            DailyStudyStat(
                date=row.date,
                total_minutes=round(row.minutes / 60),
                videos_completed=row.videos,
                chunks_studied=row.chunks,
                streak_day=row.minutes > 0,
            )
            for row in result
        ]
    
    async def calculate_streak(self, user_id: str) -> StudyStreak:
        """Calculate current and longest streak."""
        
        # Get all days with activity, ordered by date
        query = (
            select(func.date(study_progress.c.updated_at).label("study_date"))
            .where(study_progress.c.user_id == user_id)
            .distinct()
            .order_by("study_date")
        )
        
        result = await db.execute(query)
        study_dates = [row.study_date for row in result]
        
        if not study_dates:
            return StudyStreak(
                current_streak=0,
                longest_streak=0,
                last_study_date=None,
                total_study_days=0,
            )
        
        # Calculate streaks
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
        
        # Check if studied today or yesterday
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
            if dates[i] == dates[i-1] + timedelta(days=1):
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        
        return longest
```

---

## Frontend Integration

### Vue Component for ECharts

```vue
<!-- frontend/src/components/statistics/StudyChart.vue -->
<template>
  <div class="study-chart">
    <div ref="chartRef" class="chart-container"></div>
    <div class="chart-controls">
      <el-radio-group v-model="selectedPeriod" @change="updatePeriod">
        <el-radio-button label="7d">Last 7 Days</el-radio-button>
        <el-radio-button label="30d">Last 30 Days</el-radio-button>
        <el-radio-button label="90d">Last 90 Days</el-radio-button>
        <el-radio-button label="1y">Last Year</el-radio-button>
      </el-radio-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { useStatisticsStore } from '@/stores/statistics.store'

const props = defineProps<{
  chartType: 'timeline' | 'heatmap' | 'weekly'
}>()

const chartRef = ref<HTMLDivElement>()
const chartInstance = ref<echarts.ECharts>()
const statisticsStore = useStatisticsStore()
const selectedPeriod = ref('30d')

onMounted(async () => {
  if (chartRef.value) {
    chartInstance.value = echarts.init(chartRef.value)
    await loadChart()
  }
})

onUnmounted(() => {
  chartInstance.value?.dispose()
})

async function loadChart() {
  const config = await statisticsStore.getChartData(
    props.chartType,
    selectedPeriod.value
  )
  
  if (chartInstance.value) {
    chartInstance.value.setOption(config.pyecharts_option, true)
    
    // Handle click events
    chartInstance.value.on('click', (params: any) => {
      if (params.componentType === 'series') {
        emit('chartClick', params)
      }
    })
  }
}

function updatePeriod() {
  loadChart()
}

// Handle window resize
window.addEventListener('resize', () => {
  chartInstance.value?.resize()
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 400px;
}

.chart-controls {
  margin-top: 16px;
  text-align: center;
}
</style>
```

---

## Performance Considerations

### Database Optimization
- Create index on `study_progress(user_id, updated_at)`
- Cache daily aggregations in Redis for 1 hour
- Pre-calculate streaks on study activity

### Chart Optimization
- Limit data points to max 365 days
- Use data sampling for large datasets
- Lazy load charts below the fold
- Use ECharts canvas renderer for better performance

### API Caching
- Cache chart configurations for 5 minutes
- Invalidate on new study activity
- Use ETags for conditional requests

---

## Security Considerations

- All endpoints require authentication
- Users can only access their own statistics
- Rate limiting: 100 requests/minute per user
- Sanitize chart data to prevent XSS in tooltips

---

## Testing Strategy

### Unit Tests
- Test statistics calculation logic
- Test streak computation
- Test chart generation

### Integration Tests
- Test API endpoints
- Test database queries
- Test period filtering

### E2E Tests
- Test chart rendering
- Test interactive features
- Test period switching

---

## Dependencies

### Backend
```toml
[project.dependencies]
"pyecharts>=2.0.0" = { version = ">=2.0.0" }
```

### Frontend
```json
{
  "dependencies": {
    "echarts": "^5.4.0",
    "vue-echarts": "^6.6.0"
  }
}
```

---

## Open Questions

1. Should we support custom date ranges beyond presets?
2. Do we need email notifications for streak milestones?
3. Should we add social features (compare with friends)?
4. Do we need export functionality (PDF/CSV)?

---

## Implementation Checklist

- [ ] Add pyecharts to pyproject.toml
- [ ] Create statistics schemas
- [ ] Create statistics service
- [ ] Create chart service with pyecharts
- [ ] Add API endpoints
- [ ] Add database indexes
- [ ] Create Vue chart components
- [ ] Add frontend routes
- [ ] Write tests
- [ ] Update documentation

---

**Ready for implementation planning**
