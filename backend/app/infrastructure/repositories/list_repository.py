"""Repository for mailing list persistence."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import Base
from app.infrastructure.database.models import MailingList, ListContact
from .base import BaseRepository


class MailingListRepository(BaseRepository[MailingList]):
    """Repository for MailingList operations."""

    model = MailingList

    async def list_for_user(self, user_id: str) -> list[MailingList]:
        """Get all mailing lists for a user."""
        stmt = select(self.model).where(self.model.user_id == user_id).order_by(self.model.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_and_name(self, user_id: str, name: str) -> MailingList | None:
        """Get a list by user ID and name."""
        stmt = select(self.model).where(
            (self.model.user_id == user_id) & (self.model.name == name)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_with_contacts(self, list_id: str) -> MailingList | None:
        """Get a list with its contacts loaded."""
        stmt = select(self.model).where(self.model.id == list_id).options(
            selectinload(self.model.memberships)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def add_contact(self, list_id: str, contact_id: str) -> ListContact:
        """Add a contact to a mailing list."""
        membership = ListContact(list_id=list_id, contact_id=contact_id)
        self.session.add(membership)
        await self.session.commit()
        await self.session.refresh(membership)
        return membership

    async def remove_contact(self, list_id: str, contact_id: str) -> bool:
        """Remove a contact from a mailing list."""
        stmt = select(ListContact).where(
            (ListContact.list_id == list_id) & (ListContact.contact_id == contact_id)
        )
        result = await self.session.execute(stmt)
        membership = result.scalars().first()
        
        if membership:
            await self.session.delete(membership)
            await self.session.commit()
            return True
        return False

    async def get_list_contacts(self, list_id: str) -> list[ListContact]:
        """Get all contacts in a mailing list."""
        stmt = select(ListContact).where(ListContact.list_id == list_id).options(
            selectinload(ListContact.contact)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_contact_list_count(self, list_id: str) -> int:
        """Count contacts in a list."""
        stmt = select(ListContact).where(ListContact.list_id == list_id)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
