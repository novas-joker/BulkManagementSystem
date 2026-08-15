"""
Database Configuration and Setup
Async SQLAlchemy engine and session management
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# ─── Async Engine ────────────────────────────────────────────────────────────

async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.is_development(),
    future=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=20,
    max_overflow=10,
)

# ─── Session Factory ─────────────────────────────────────────────────────────

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# ─── Base for ORM Models ────────────────────────────────────────────────────

Base = declarative_base()


# ─── Session Dependency ────────────────────────────────────────────────────

async def get_db() ->AsyncGenerator[AsyncSession, None]:
    """Dependency for database session in routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
