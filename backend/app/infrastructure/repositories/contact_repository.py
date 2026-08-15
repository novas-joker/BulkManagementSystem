"""Repository for contact persistence and lookup."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import Contact

from .base import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    """Database access for contacts."""

    model = Contact

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_user_and_email(self, user_id: str, email: str) -> Contact | None:
        """Return the contact for a user by email."""
        stmt = select(Contact).where(Contact.user_id == user_id, Contact.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_for_user(self, user_id: str) -> list[Contact]:
        """Return all contacts belonging to a user."""
        stmt = select(Contact).where(Contact.user_id == user_id).order_by(Contact.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_for_user(self, user_id: str, query: str) -> list[Contact]:
        """Search contacts by email or name for a user."""
        like_query = f"%{query}%"
        stmt = (
            select(Contact)
            .where(Contact.user_id == user_id)
            .where((Contact.email.ilike(like_query)) | (Contact.first_name.ilike(like_query)) | (Contact.last_name.ilike(like_query)))
            .order_by(Contact.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
