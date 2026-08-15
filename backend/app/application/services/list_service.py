"""Business logic for mailing list management."""

from datetime import datetime

from app.application.services.base_service import BaseService
from app.infrastructure.repositories.list_repository import MailingListRepository
from app.infrastructure.database.models import MailingList


class MailingListService(BaseService[MailingListRepository]):
    """Handle mailing list CRUD and user-scoped queries."""

    async def list_lists(self, user_id: str) -> list[dict]:
        """Return all mailing lists for a user."""
        lists = await self.repository.list_for_user(user_id)
        return [self._serialize(lst) for lst in lists]

    async def get_list(self, user_id: str, list_id: str):
        """Fetch one list if it belongs to the user."""
        lst = await self.repository.get_by_id(list_id)
        if not lst or lst.user_id != user_id:
            return None
        return self._serialize(lst)

    async def create_list(self, user_id: str, payload: dict):
        """Create a new mailing list for the user."""
        existing = await self.repository.get_by_user_and_name(user_id, payload["name"])
        if existing:
            raise ValueError("List with this name already exists")

        lst = MailingList(
            user_id=user_id,
            name=payload["name"],
            description=payload.get("description", ""),
            is_active=payload.get("is_active", True),
        )

        created = await self.repository.create(lst)
        return self._serialize(created)

    async def update_list(self, user_id: str, list_id: str, payload: dict):
        """Update an existing list."""
        lst = await self.repository.get_by_id(list_id)
        if not lst or lst.user_id != user_id:
            return None

        if "name" in payload and payload["name"]:
            existing = await self.repository.get_by_user_and_name(user_id, payload["name"])
            if existing and existing.id != list_id:
                raise ValueError("List with this name already exists")
            lst.name = payload["name"]

        if "description" in payload:
            lst.description = payload["description"]

        if "is_active" in payload:
            lst.is_active = payload["is_active"]

        lst.updated_at = datetime.utcnow()
        updated = await self.repository.update(lst)
        return self._serialize(updated)

    async def delete_list(self, user_id: str, list_id: str) -> bool:
        """Delete a list if owned by the user."""
        lst = await self.repository.get_by_id(list_id)
        if not lst or lst.user_id != user_id:
            return False
        await self.repository.delete(lst)
        return True

    async def add_contact_to_list(self, user_id: str, list_id: str, contact_id: str):
        """Add a contact to a list."""
        lst = await self.repository.get_by_id(list_id)
        if not lst or lst.user_id != user_id:
            return None

        membership = await self.repository.add_contact(list_id, contact_id)
        
        # Update contact count
        count = await self.repository.get_contact_list_count(list_id)
        lst.contact_count = count
        await self.repository.update(lst)
        
        return {"id": membership.id, "list_id": membership.list_id, "contact_id": membership.contact_id}

    async def remove_contact_from_list(self, user_id: str, list_id: str, contact_id: str) -> bool:
        """Remove a contact from a list."""
        lst = await self.repository.get_by_id(list_id)
        if not lst or lst.user_id != user_id:
            return False

        removed = await self.repository.remove_contact(list_id, contact_id)
        
        if removed:
            # Update contact count
            count = await self.repository.get_contact_list_count(list_id)
            lst.contact_count = count
            await self.repository.update(lst)
        
        return removed

    async def get_list_contacts(self, user_id: str, list_id: str) -> list[dict] | None:
        """Get all contacts in a list."""
        lst = await self.repository.get_by_id(list_id)
        if not lst or lst.user_id != user_id:
            return None

        memberships = await self.repository.get_list_contacts(list_id)
        return [
            {
                "id": m.contact.id,
                "email": m.contact.email,
                "first_name": m.contact.first_name,
                "last_name": m.contact.last_name,
                "status": m.contact.status,
                "added_at": m.added_at.isoformat() if m.added_at else None,
            }
            for m in memberships
        ]

    @staticmethod
    def _serialize(lst) -> dict:
        return {
            "id": lst.id,
            "user_id": lst.user_id,
            "name": lst.name,
            "description": lst.description,
            "contact_count": lst.contact_count,
            "is_active": lst.is_active,
            "created_at": lst.created_at.isoformat() if lst.created_at else None,
            "updated_at": lst.updated_at.isoformat() if lst.updated_at else None,
        }
