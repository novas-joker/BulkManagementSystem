"""Business logic for segment management."""

from datetime import datetime

from app.application.services.base_service import BaseService
from app.infrastructure.repositories.segment_repository import SegmentRepository
from app.infrastructure.database.models import Segment


class SegmentService(BaseService[SegmentRepository]):
    """Handle segment CRUD and evaluation."""

    async def list_segments(self, user_id: str) -> list[dict]:
        """Return all segments for a user."""
        segments = await self.repository.list_for_user(user_id)
        return [self._serialize(segment) for segment in segments]

    async def get_segment(self, user_id: str, segment_id: str):
        """Fetch one segment if it belongs to the user."""
        segment = await self.repository.get_by_id(segment_id)
        if not segment or segment.user_id != user_id:
            return None
        return self._serialize(segment)

    async def create_segment(self, user_id: str, payload: dict):
        """Create a new segment for the user."""
        existing = await self.repository.get_by_user_and_name(user_id, payload["name"])
        if existing:
            raise ValueError("Segment with this name already exists")

        segment = Segment(
            user_id=user_id,
            name=payload["name"],
            description=payload.get("description", ""),
            filter_criteria=payload.get("filter_criteria", {}),
            is_active=payload.get("is_active", True),
        )

        created = await self.repository.create(segment)
        return self._serialize(created)

    async def update_segment(self, user_id: str, segment_id: str, payload: dict):
        """Update an existing segment."""
        segment = await self.repository.get_by_id(segment_id)
        if not segment or segment.user_id != user_id:
            return None

        if "name" in payload and payload["name"]:
            existing = await self.repository.get_by_user_and_name(user_id, payload["name"])
            if existing and existing.id != segment_id:
                raise ValueError("Segment with this name already exists")
            segment.name = payload["name"]

        if "description" in payload:
            segment.description = payload["description"]

        if "filter_criteria" in payload:
            segment.filter_criteria = payload["filter_criteria"]

        if "is_active" in payload:
            segment.is_active = payload["is_active"]

        segment.updated_at = datetime.utcnow()
        updated = await self.repository.update(segment)
        return self._serialize(updated)

    async def delete_segment(self, user_id: str, segment_id: str) -> bool:
        """Delete a segment if owned by the user."""
        segment = await self.repository.get_by_id(segment_id)
        if not segment or segment.user_id != user_id:
            return False
        await self.repository.delete(segment)
        return True

    async def preview_segment(self, user_id: str, segment_id: str) -> dict:
        """Preview contacts matching a segment's criteria."""
        segment = await self.repository.get_by_id(segment_id)
        if not segment or segment.user_id != user_id:
            return None

        matching_contacts = await self.repository.evaluate_segment(segment)
        
        # Update segment contact count
        segment.contact_count = len(matching_contacts)
        await self.repository.update(segment)

        return {
            "segment_id": segment.id,
            "segment_name": segment.name,
            "total_contacts": len(matching_contacts),
            "contacts": [
                {
                    "id": contact.id,
                    "email": contact.email,
                    "first_name": contact.first_name,
                    "last_name": contact.last_name,
                    "status": contact.status,
                }
                for contact in matching_contacts[:100]  # Limit to 100 for preview
            ],
        }

    @staticmethod
    def _serialize(segment) -> dict:
        return {
            "id": segment.id,
            "user_id": segment.user_id,
            "name": segment.name,
            "description": segment.description,
            "filter_criteria": segment.filter_criteria or {},
            "contact_count": segment.contact_count,
            "is_active": segment.is_active,
            "created_at": segment.created_at.isoformat() if segment.created_at else None,
            "updated_at": segment.updated_at.isoformat() if segment.updated_at else None,
        }
