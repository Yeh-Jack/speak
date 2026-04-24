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

    print("Database initialized successfully")


if __name__ == "__main__":
    asyncio.run(init_db())
