"""Repository for suppression list persistence."""

from sqlalchemy import select

from app.infrastructure.database.models import Suppression
from .base import BaseRepository


class SuppressionRepository(BaseRepository[Suppression]):
    """Repository for Suppression operations."""

    model = Suppression

    async def list_for_user(self, user_id: str) -> list[Suppression]:
        """Get all suppressions for a user."""
        stmt = select(self.model).where(self.model.user_id == user_id).order_by(self.model.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_and_email(self, user_id: str, email: str) -> Suppression | None:
        """Get a suppression by user ID and email."""
        stmt = select(self.model).where(
            (self.model.user_id == user_id) & (self.model.email == email)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def is_suppressed(self, user_id: str, email: str) -> bool:
        """Check if an email is suppressed for a user."""
        suppression = await self.get_by_user_and_email(user_id, email)
        return suppression is not None

    async def suppress(self, user_id: str, email: str, reason: str = "", source: str = "manual") -> Suppression:
        """Add an email to the suppression list."""
        existing = await self.get_by_user_and_email(user_id, email)
        if existing:
            return existing
        
        suppression = Suppression(
            user_id=user_id,
            email=email,
            reason=reason,
            source=source,
        )
        return await self.create(suppression)

    async def unsuppress(self, user_id: str, email: str) -> bool:
        """Remove an email from the suppression list."""
        suppression = await self.get_by_user_and_email(user_id, email)
        if suppression:
            await self.delete(suppression)
            return True
        return False
