"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth

api_router = APIRouter()

# Include auth endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Additional routers will be added in subsequent phases
# from app.api.v1.endpoints import videos, courses, learning, speaking, exams, models, chat
# api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
# api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
# api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
# api_router.include_router(speaking.router, prefix="/speaking", tags=["speaking"])
# api_router.include_router(exams.router, prefix="/exams", tags=["exams"])
# api_router.include_router(models.router, prefix="/models", tags=["models"])
# api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
