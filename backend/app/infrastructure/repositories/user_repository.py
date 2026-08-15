"""Repository for user persistence and queries."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import User

from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Handle user-specific database operations."""

    model = User

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_email(self, email: str) -> User | None:
        """Return a user by email address."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_active_users(self) -> list[User]:
        """Return all active users."""
        stmt = select(User).where(User.status == "active")
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
