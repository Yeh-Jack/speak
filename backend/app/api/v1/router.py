"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import chat, videos

api_router = APIRouter()

api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
