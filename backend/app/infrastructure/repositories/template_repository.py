"""Repository for template persistence and lookup."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import EmailTemplate

from .base import BaseRepository


class TemplateRepository(BaseRepository[EmailTemplate]):
    """Database access for email templates."""

    model = EmailTemplate

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_user_and_name(self, user_id: str, name: str) -> EmailTemplate | None:
        """Return a template by name for a user."""
        stmt = select(EmailTemplate).where(EmailTemplate.user_id == user_id, EmailTemplate.name == name)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_for_user(self, user_id: str) -> list[EmailTemplate]:
        """Return all templates for a user."""
        stmt = select(EmailTemplate).where(EmailTemplate.user_id == user_id).order_by(EmailTemplate.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
