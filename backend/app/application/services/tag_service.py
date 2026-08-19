"""Business logic for tag management."""

from datetime import datetime

from app.application.services.base_service import BaseService
from app.infrastructure.repositories.tag_repository import TagRepository
from app.infrastructure.database.models import Tag


class TagService(BaseService[TagRepository]):
    """Handle tag CRUD and user-scoped queries."""

    async def list_tags(self, user_id: str) -> list[dict]:
        """Return all tags for a user."""
        tags = await self.repository.list_for_user(user_id)
        return [self._serialize(tag) for tag in tags]

    async def get_tag(self, user_id: str, tag_id: str):
        """Fetch one tag if it belongs to the user."""
        tag = await self.repository.get_by_id(tag_id)
        if not tag or tag.user_id != user_id:
            return None
        return self._serialize(tag)

    async def create_tag(self, user_id: str, payload: dict):
        """Create a new tag for the user."""
        existing = await self.repository.get_by_user_and_name(user_id, payload["name"])
        if existing:
            raise ValueError("Tag with this name already exists")

        tag = Tag(
            user_id=user_id,
            name=payload["name"],
            description=payload.get("description", ""),
        )

        created = await self.repository.create(tag)
        return self._serialize(created)

    async def update_tag(self, user_id: str, tag_id: str, payload: dict):
        """Update an existing tag."""
        tag = await self.repository.get_by_id(tag_id)
        if not tag or tag.user_id != user_id:
            return None

        if "name" in payload and payload["name"]:
            existing = await self.repository.get_by_user_and_name(user_id, payload["name"])
            if existing and existing.id != tag_id:
                raise ValueError("Tag with this name already exists")
            tag.name = payload["name"]

        if "description" in payload:
            tag.description = payload["description"]

        updated = await self.repository.update(tag)
        return self._serialize(updated)

    async def delete_tag(self, user_id: str, tag_id: str) -> bool:
        """Delete a tag if owned by the user."""
        tag = await self.repository.get_by_id(tag_id)
        if not tag or tag.user_id != user_id:
            return False
        await self.repository.delete(tag)
        return True

    async def assign_tag_to_contact(self, user_id: str, tag_id: str, contact_id: str):
        """Assign a tag to a contact."""
        tag = await self.repository.get_by_id(tag_id)
        if not tag or tag.user_id != user_id:
            return None

        assignment = await self.repository.assign_to_contact(tag_id, contact_id)
        return {"id": assignment.id, "tag_id": assignment.tag_id, "contact_id": assignment.contact_id}

    async def remove_tag_from_contact(self, user_id: str, tag_id: str, contact_id: str) -> bool:
        """Remove a tag from a contact."""
        tag = await self.repository.get_by_id(tag_id)
        if not tag or tag.user_id != user_id:
            return False
        return await self.repository.remove_from_contact(tag_id, contact_id)

    async def get_contact_tags(self, user_id: str, contact_id: str) -> list[dict]:
        """Get all tags for a contact (user-scoped)."""
        tags = await self.repository.get_contact_tags(contact_id)
        # Filter by user_id to ensure ownership
        user_tags = [tag for tag in tags if tag.user_id == user_id]
        return [self._serialize(tag) for tag in user_tags]

    @staticmethod
    def _serialize(tag) -> dict:
        return {
            "id": tag.id,
            "user_id": tag.user_id,
            "name": tag.name,
            "description": tag.description,
            "contact_count": tag.contact_count,
            "created_at": tag.created_at.isoformat() if tag.created_at else None,
        }
