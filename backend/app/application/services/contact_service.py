"""Business logic for contact management."""

from datetime import datetime

from app.application.services.base_service import BaseService
from app.infrastructure.repositories.contact_repository import ContactRepository


class ContactService(BaseService[ContactRepository]):
    """Handle contact CRUD and user-scoped queries."""

    async def list_contacts(self, user_id: str) -> list[dict]:
        """Return all contacts for a user."""
        contacts = await self.repository.list_for_user(user_id)
        return [self._serialize(contact) for contact in contacts]

    async def get_contact(self, user_id: str, contact_id: str):
        """Fetch one contact if it belongs to the user."""
        contact = await self.repository.get_by_id(contact_id)
        if not contact or contact.user_id != user_id:
            return None
        return self._serialize(contact)

    async def create_contact(self, user_id: str, payload: dict):
        """Create a new user contact."""
        from app.infrastructure.database.models import Contact

        existing = await self.repository.get_by_user_and_email(user_id, payload["email"])
        if existing:
            raise ValueError("Contact with this email already exists")

        contact = Contact(
            user_id=user_id,
            email=payload["email"],
            first_name=payload.get("first_name", ""),
            last_name=payload.get("last_name", ""),
            status=payload.get("status", "subscribed"),
            source=payload.get("source", "manual"),
            custom_fields=payload.get("custom_fields", {}),
            is_valid_email=payload.get("is_valid_email", True),
        )

        created = await self.repository.create(contact)
        return self._serialize(created)

    async def update_contact(self, user_id: str, contact_id: str, payload: dict):
        """Update an existing contact."""
        contact = await self.repository.get_by_id(contact_id)
        if not contact or contact.user_id != user_id:
            return None

        for field in ["first_name", "last_name", "status", "source", "custom_fields", "is_valid_email"]:
            if field in payload and payload[field] is not None:
                setattr(contact, field, payload[field])

        contact.updated_at = datetime.utcnow()
        updated = await self.repository.update(contact)
        return self._serialize(updated)

    async def delete_contact(self, user_id: str, contact_id: str) -> bool:
        """Delete a contact if owned by the user."""
        contact = await self.repository.get_by_id(contact_id)
        if not contact or contact.user_id != user_id:
            return False
        await self.repository.delete(contact)
        return True

    @staticmethod
    def _serialize(contact) -> dict:
        return {
            "id": contact.id,
            "user_id": contact.user_id,
            "email": contact.email,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "status": contact.status,
            "source": contact.source,
            "custom_fields": contact.custom_fields or {},
            "is_valid_email": contact.is_valid_email,
            "created_at": contact.created_at.isoformat() if contact.created_at else None,
            "updated_at": contact.updated_at.isoformat() if contact.updated_at else None,
        }
