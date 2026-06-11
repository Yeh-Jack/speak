"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import chat, videos, stats, speaking, llm, vocabulary, migrate

api_router = APIRouter()

api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(speaking.router, prefix="/speaking", tags=["speaking"])
api_router.include_router(llm.router, prefix="/llm", tags=["llm"])
api_router.include_router(vocabulary.router, prefix="/vocabulary", tags=["vocabulary"])
api_router.include_router(migrate.router, prefix="/admin", tags=["admin"])
