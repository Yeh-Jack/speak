"""Pydantic schemas for the English Learning application."""

from app.schemas.course import (
    Course,
    CourseCreate,
    CourseUpdate,
    CourseVideo,
    CourseVideoCreate,
    CourseVideoUpdate,
    ReorderVideosRequest,
)
from app.schemas.progress import StudyProgress, StudyProgressCreate, StudyProgressUpdate
from app.schemas.study_plan import StudyPlan, StudyPlanCreate, StudyPlanUpdate
from app.schemas.video import (
    Video,
    VideoChunk,
    VideoChunkCreate,
    VideoChunkUpdate,
    VideoCreate,
    VideoResponse,
    VideoUpdate,
)
from app.schemas.vocabulary import Vocabulary, VocabularyCreate, VocabularyReview, VocabularyUpdate

__all__ = [
    # Video
    "Video",
    "VideoCreate",
    "VideoUpdate",
    "VideoChunk",
    "VideoChunkCreate",
    "VideoChunkUpdate",
    "VideoResponse",
    # Course
    "Course",
    "CourseCreate",
    "CourseUpdate",
    "CourseVideo",
    "CourseVideoCreate",
    "CourseVideoUpdate",
    "ReorderVideosRequest",
    # Study Plan
    "StudyPlan",
    "StudyPlanCreate",
    "StudyPlanUpdate",
    # Progress
    "StudyProgress",
    "StudyProgressCreate",
    "StudyProgressUpdate",
    # Vocabulary
    "Vocabulary",
    "VocabularyCreate",
    "VocabularyUpdate",
    "VocabularyReview",
]
