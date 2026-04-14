"""Pydantic schemas for the English Learning application."""

from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.schemas.auth import Token, TokenPayload, LoginRequest, RegisterRequest
from app.schemas.video import (
    Video,
    VideoCreate,
    VideoUpdate,
    VideoInDB,
    VideoChunk,
    VideoChunkCreate,
    VideoChunkUpdate,
)
from app.schemas.course import (
    Course,
    CourseCreate,
    CourseUpdate,
    CourseInDB,
    CourseVideo,
    CourseVideoCreate,
    CourseVideoUpdate,
)
from app.schemas.study_plan import StudyPlan, StudyPlanCreate, StudyPlanUpdate
from app.schemas.progress import StudyProgress, StudyProgressCreate, StudyProgressUpdate
from app.schemas.vocabulary import Vocabulary, VocabularyCreate, VocabularyUpdate, VocabularyReview
from app.schemas.exam import (
    Exam,
    ExamCreate,
    ExamQuestion,
    ExamQuestionCreate,
    ExamResult,
    ExamResultCreate,
    ExamSubmission,
)

__all__ = [
    # User
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    # Auth
    "Token",
    "TokenPayload",
    "LoginRequest",
    "RegisterRequest",
    # Video
    "Video",
    "VideoCreate",
    "VideoUpdate",
    "VideoInDB",
    "VideoChunk",
    "VideoChunkCreate",
    "VideoChunkUpdate",
    # Course
    "Course",
    "CourseCreate",
    "CourseUpdate",
    "CourseInDB",
    "CourseVideo",
    "CourseVideoCreate",
    "CourseVideoUpdate",
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
    # Exam
    "Exam",
    "ExamCreate",
    "ExamQuestion",
    "ExamQuestionCreate",
    "ExamResult",
    "ExamResultCreate",
    "ExamSubmission",
]
