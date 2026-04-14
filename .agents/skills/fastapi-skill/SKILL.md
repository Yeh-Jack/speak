# FastAPI Skill

## Description
Expert-level FastAPI development with SQLAlchemy, Pydantic, and async patterns.

## When to Use
Use this skill when working with FastAPI backend code, API endpoints, database models, or authentication.

## Guidelines

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Pydantic settings
│   ├── api/
│   │   ├── deps.py          # Dependencies (auth, DB)
│   │   └── v1/
│   │       └── endpoints/   # Route handlers
│   ├── core/
│   │   ├── security.py      # JWT, password hashing
│   │   └── logger.py        # Structured logging
│   ├── db/
│   │   ├── base.py          # Base model
│   │   └── session.py       # DB session
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   └── services/            # Business logic
```

### Coding Patterns
1. **Type hints are mandatory** - Use `from typing import Optional, List, Dict`
2. **Use async/await** for I/O operations (DB, HTTP)
3. **Pydantic v2** for all schemas
4. **Dependency injection** with FastAPI `Depends()`
5. **Repository pattern** for DB operations
6. **Service layer** for business logic

### Dependencies
```python
# Core
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Database
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.28.0  # PostgreSQL driver
alembic>=1.12.0

# Auth
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6

# Async
httpx>=0.24.0
celery>=5.3.0
redis>=4.6.0
```

### Example: Dependency Injection
```python
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    # JWT validation logic
    ...
```

### Example: Service Layer
```python
class VideoService:
    def __init__(self, video_repo: VideoRepository):
        self.video_repo = video_repo

    async def create_video(self, video_in: VideoCreate) -> Video:
        video = Video(**video_in.model_dump())
        return await self.video_repo.create(video)
```

## Resources
- FastAPI Docs: https://fastapi.tiangolo.com
- Pydantic Docs: https://docs.pydantic.dev
- SQLAlchemy Docs: https://docs.sqlalchemy.org
