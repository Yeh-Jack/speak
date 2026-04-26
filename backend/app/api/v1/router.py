"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import courses, videos

api_router = APIRouter()

api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
