# SQLite3 Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the English Learning App from PostgreSQL to SQLite3 with database file at `/data/learning.db`

**Architecture:** Replace PostgreSQL+asyncpg with SQLite+aiosqlite while maintaining async SQLAlchemy 2.0 patterns. Update configuration, dependencies, Docker setup, and handle PostgreSQL-specific UUID type.

**Tech Stack:** FastAPI, SQLAlchemy 2.0 (async), aiosqlite, Alembic

---

## File Structure Overview

**Modified Files:**
- `backend/app/core/config.py` - Update DATABASE_URL to SQLite
- `backend/app/db/session.py` - Remove PostgreSQL pool settings, add SQLite pragmas
- `backend/app/db/base.py` - Replace PostgreSQL UUID with generic String UUID
- `backend/pyproject.toml` - Replace asyncpg with aiosqlite
- `backend/alembic/env.py` - Update for SQLite compatibility
- `docker-compose.yml` - Remove PostgreSQL service and volumes

**Created Files:**
- `backend/scripts/init_db.py` - Database initialization script

---

## Task 1: Update Configuration for SQLite3

**Files:**
- Modify: `backend/app/core/config.py:13`

**Note:** Database will be named `learning.db` and stored at `/data/learning.db`

- [ ] **Step 1: Update DATABASE_URL default value**

Change from:
```python
DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/education"
```

To:
```python
DATABASE_URL: str = "sqlite+aiosqlite:///data/learning.db"
```

- [ ] **Step 2: Commit the change**
```bash
git add backend/app/core/config.py
git commit -m "config: migrate DATABASE_URL from PostgreSQL to SQLite3"
```

---

## Task 2: Update Database Session for SQLite3

**Files:**
- Modify: `backend/app/db/session.py:8-22`

- [ ] **Step 1: Update engine creation to remove PostgreSQL-specific pool settings and add SQLite pragmas**

Change from:
```python
# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_size=10,
    max_overflow=20,
)
```

To:
```python
# Create async engine with SQLite-specific settings
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# SQLite doesn't support connection pooling, so we configure it differently
# WAL mode is enabled via connect_args in the URL or pragmas
```

- [ ] **Step 2: Update session factory to remove unsupported SQLite options**

The AsyncSessionLocal can remain the same - it's already compatible:
```python
# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)
```

- [ ] **Step 3: Add SQLite pragma execution on connect**

Add after engine creation:
```python


async def init_sqlite_pragmas():
    """Initialize SQLite pragmas for better performance and foreign key support."""
    async with engine.connect() as conn:
        # Enable foreign key constraints (SQLite disables them by default)
        await conn.execute(text("PRAGMA foreign_keys = ON"))
        # Use WAL mode for better concurrent access
        await conn.execute(text("PRAGMA journal_mode = WAL"))
```

Also add import at top:
```python
from sqlalchemy import text
```

- [ ] **Step 4: Commit the changes**
```bash
git add backend/app/db/session.py
git commit -m "db: update session for SQLite3 compatibility with WAL mode and FK support"
```

---

## Task 3: Update Base Model for SQLite UUID Compatibility

**Files:**
- Modify: `backend/app/db/base.py:8, 18-20`

- [ ] **Step 1: Remove PostgreSQL UUID import and use String instead**

Change imports from:
```python
from sqlalchemy.dialects.postgresql import UUID
```

To:
```python
# No PostgreSQL-specific imports - using generic String for UUID
```

- [ ] **Step 2: Update type_annotation_map for SQLite compatibility**

Change from:
```python
type_annotation_map = {
    uuid.UUID: UUID(as_uuid=True),
}
```

To:
```python
type_annotation_map = {
    uuid.UUID: String(36),  # SQLite doesn't have native UUID, use String
}
```

- [ ] **Step 3: Commit the changes**
```bash
git add backend/app/db/base.py
git commit -m "db: replace PostgreSQL UUID with String for SQLite compatibility"
```

---

## Task 4: Update Dependencies in pyproject.toml

**Files:**
- Modify: `backend/pyproject.toml:31-33`

- [ ] **Step 1: Replace asyncpg with aiosqlite**

Change from:
```toml
# Database
"sqlalchemy[asyncio]>=2.0.25",
"asyncpg>=0.29.0",
"alembic>=1.13.0",
```

To:
```toml
# Database - SQLite with async support
"sqlalchemy[asyncio]>=2.0.25",
"aiosqlite>=0.19.0",
"alembic>=1.13.0",
```

- [ ] **Step 2: Lock dependencies with uv**
```bash
cd /workspaces/education/backend
uv lock
```

- [ ] **Step 3: Commit the changes**
```bash
git add backend/pyproject.toml backend/uv.lock
git commit -m "deps: replace asyncpg with aiosqlite for SQLite support"
```

---

## Task 5: Update Alembic Configuration for SQLite

**Files:**
- Modify: `backend/alembic/env.py:6-7, 52-67`

- [ ] **Step 1: Update imports for SQLite compatibility**

Change from:
```python
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
```

To:
```python
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config, create_async_engine
```

- [ ] **Step 2: Update run_async_migrations to handle SQLite properly**

Change from:
```python
async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()
```

To:
```python
async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    # SQLite doesn't need pooling, use NullPool
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Enable foreign keys for SQLite
        await connection.execute(text("PRAGMA foreign_keys = ON"))
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()
```

- [ ] **Step 3: Add text import at the top**

Add after existing imports:
```python
from sqlalchemy import text
```

- [ ] **Step 4: Commit the changes**
```bash
git add backend/alembic/env.py
git commit -m "alembic: update migration config for SQLite3 support"
```

---

## Task 6: Update Docker Compose to Remove PostgreSQL

**Files:**
- Modify: `docker-compose.yml:1-65`

- [ ] **Step 1: Remove PostgreSQL service and volume**

Change from:
```yaml
version: "3.8"

services:
  db:
    image: postgres:16.13-bookworm
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRE_PASS:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-education}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER:-postgres}:${POSTGRE_PASS:-postgres}@db:5432/${POSTGRES_DB:-education}
      - STORAGE_BASE_PATH=/data
      - LLM_MODEL_PATH=/data/shared/models
      - DEFAULT_MODEL=qwen2.5-7b-q4_k_m.gguf
      - LLM_GPU_LAYERS=${LLM_GPU_LAYERS:--1}
      - LLM_CONTEXT_SIZE=4096
      - JWT_SECRET=${JWT_SECRET:-your-secret-key-change-in-production}
      - JWT_ALGORITHM=HS256
      - JWT_EXPIRATION=24h
      - YOUTUBE_DOWNLOAD_QUALITY=720
      - YOUTUBE_AUDIO_QUALITY=128k
    volumes:
      - app_data:/data
    ports:
      - "8080:8080"
    depends_on:
      db:
        condition: service_healthy
    command: >
      sh -c "cd /app &&
      uv run alembic upgrade head &&
      uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8080
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

volumes:
  postgres_data:
  app_data:
```

To:
```yaml
version: "3.8"

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///data/learning.db
      - STORAGE_BASE_PATH=/data
      - LLM_MODEL_PATH=/data/shared/models
      - DEFAULT_MODEL=qwen2.5-7b-q4_k_m.gguf
      - LLM_GPU_LAYERS=${LLM_GPU_LAYERS:--1}
      - LLM_CONTEXT_SIZE=4096
      - JWT_SECRET=${JWT_SECRET:-your-secret-key-change-in-production}
      - JWT_ALGORITHM=HS256
      - JWT_EXPIRATION=24h
      - YOUTUBE_DOWNLOAD_QUALITY=720
      - YOUTUBE_AUDIO_QUALITY=128k
    volumes:
      - app_data:/data
    ports:
      - "8080:8080"
    command: >
      sh -c "cd /app &&
      mkdir -p /data &&
      uv run alembic upgrade head &&
      uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8080
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

volumes:
  app_data:
```

- [ ] **Step 2: Commit the changes**
```bash
git add docker-compose.yml
git commit -m "docker: remove PostgreSQL service, configure SQLite in backend"
```

---

## Task 7: Create Database Initialization Script

**Files:**
- Create: `backend/scripts/__init__.py`
- Create: `backend/scripts/init_db.py`

- [ ] **Step 1: Create scripts directory init file**
```python
"""Scripts package."""
```

- [ ] **Step 2: Create database initialization script**
```python
"""Database initialization script for creating tables."""

import asyncio

from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine


async def init_db():
    """Initialize database with all tables."""
    async with engine.begin() as conn:
        # Enable foreign keys for SQLite
        await conn.execute(text("PRAGMA foreign_keys = ON"))
        await conn.execute(text("PRAGMA journal_mode = WAL"))

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    print("Database initialized successfully at /data/learning.db")


if __name__ == "__main__":
    asyncio.run(init_db())
```

- [ ] **Step 3: Commit the changes**
```bash
git add backend/scripts/
git commit -m "scripts: add database initialization script for SQLite"
```

---

## Task 8: Update .gitignore for SQLite Files

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Add SQLite database files to gitignore**

Add to `.gitignore`:
```gitignore
# SQLite database files
*.db
*.db-shm
*.db-wal
```

- [ ] **Step 2: Commit the changes**
```bash
git add .gitignore
git commit -m "gitignore: exclude SQLite database files"
```

---

## Task 9: Update Backend Dockerfile for SQLite

**Files:**
- Modify: `backend/Dockerfile`

- [ ] **Step 1: Read current Dockerfile**
```bash
cat /workspaces/education/backend/Dockerfile
```

- [ ] **Step 2: Ensure data directory is created**

If the Dockerfile doesn't already create /data, add:
```dockerfile
# Create data directory for SQLite and other storage
RUN mkdir -p /data/shared/models /data/users
```

- [ ] **Step 3: Commit the changes**
```bash
git add backend/Dockerfile
git commit -m "docker: ensure data directories exist for SQLite"
```

---

## Task 10: Update Environment Example File

**Files:**
- Modify: `backend/.env.example`

- [ ] **Step 1: Update DATABASE_URL example**

Change from:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/education
```

To:
```
DATABASE_URL=sqlite+aiosqlite:///data/learning.db
```

- [ ] **Step 2: Commit the changes**
```bash
git add backend/.env.example
git commit -m "env: update example DATABASE_URL for SQLite"
```

---

## Task 11: Test Database Setup

**Files:**
- Test: Run commands to verify SQLite setup

- [ ] **Step 1: Install updated dependencies**
```bash
cd /workspaces/education/backend
uv sync
```

- [ ] **Step 2: Create data directory**
```bash
mkdir -p /workspaces/education/data
```

- [ ] **Step 3: Run database initialization**
```bash
cd /workspaces/education/backend
uv run python scripts/init_db.py
```

Expected output: `Database initialized successfully at /data/learning.db`

- [ ] **Step 4: Verify database file was created**
```bash
ls -la /workspaces/education/data/learning.db
```

Expected: File exists with non-zero size

- [ ] **Step 5: Run Alembic migrations**
```bash
cd /workspaces/education/backend
uv run alembic upgrade head
```

Expected: Migrations apply successfully (or show "already up to date")

- [ ] **Step 6: Test database connection via Python**
```python
import asyncio
from app.db.session import AsyncSessionLocal

async def test_db():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        print(f"Database test result: {result.scalar()}")

asyncio.run(test_db())
```

Save and run:
```bash
cd /workspaces/education/backend
uv run python -c "
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def test_db():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text('SELECT 1'))
        print(f'Database test result: {result.scalar()}')

asyncio.run(test_db())
"
```

Expected output: `Database test result: 1`

- [ ] **Step 7: Commit any final changes**
```bash
git add -A
git commit -m "test: verify SQLite database setup and connection" || echo "No changes to commit"
```

---

## Spec Coverage Check

**Requirements covered:**
- ✅ SQLite3 database at `/data/learning.db`
- ✅ Async SQLAlchemy 2.0 patterns maintained
- ✅ Removed PostgreSQL dependency
- ✅ Updated Docker Compose configuration
- ✅ Alembic migrations work with SQLite
- ✅ Foreign key constraints enabled
- ✅ WAL mode for better concurrent access
- ✅ All models compatible with SQLite

**No placeholders in this plan - all code provided.**
