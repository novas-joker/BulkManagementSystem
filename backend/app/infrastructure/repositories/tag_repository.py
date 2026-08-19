"""Repository for tag persistence."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models import Tag, ContactTag
from .base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    """Repository for Tag operations."""

    model = Tag

    async def list_for_user(self, user_id: str) -> list[Tag]:
        """Get all tags for a user."""
        stmt = select(self.model).where(self.model.user_id == user_id).order_by(self.model.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_and_name(self, user_id: str, name: str) -> Tag | None:
        """Get a tag by user ID and name."""
        stmt = select(self.model).where(
            (self.model.user_id == user_id) & (self.model.name == name)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def assign_to_contact(self, tag_id: str, contact_id: str) -> ContactTag:
        """Assign a tag to a contact."""
        tag_assignment = ContactTag(tag_id=tag_id, contact_id=contact_id)
        self.session.add(tag_assignment)
        await self.session.commit()
        await self.session.refresh(tag_assignment)
        return tag_assignment

    async def remove_from_contact(self, tag_id: str, contact_id: str) -> bool:
        """Remove a tag from a contact."""
        stmt = select(ContactTag).where(
            (ContactTag.tag_id == tag_id) & (ContactTag.contact_id == contact_id)
        )
        result = await self.session.execute(stmt)
        assignment = result.scalars().first()
        
        if assignment:
            await self.session.delete(assignment)
            await self.session.commit()
            return True
        return False

    async def get_contact_tags(self, contact_id: str) -> list[Tag]:
        """Get all tags for a contact."""
        stmt = select(Tag).join(ContactTag).where(
            ContactTag.contact_id == contact_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_tagged_contacts(self, tag_id: str) -> list[ContactTag]:
        """Get all contacts with a specific tag."""
        stmt = select(ContactTag).where(ContactTag.tag_id == tag_id).options(
            selectinload(ContactTag.contact)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
