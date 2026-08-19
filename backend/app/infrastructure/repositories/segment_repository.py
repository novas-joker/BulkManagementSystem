"""Repository for segment persistence."""

from sqlalchemy import select, and_

from app.infrastructure.database.models import Segment, Contact, ContactTag, MailingList, ListContact
from .base import BaseRepository


class SegmentRepository(BaseRepository[Segment]):
    """Repository for Segment operations."""

    model = Segment

    async def list_for_user(self, user_id: str) -> list[Segment]:
        """Get all segments for a user."""
        stmt = select(self.model).where(self.model.user_id == user_id).order_by(self.model.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_and_name(self, user_id: str, name: str) -> Segment | None:
        """Get a segment by user ID and name."""
        stmt = select(self.model).where(
            (self.model.user_id == user_id) & (self.model.name == name)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def evaluate_segment(self, segment: Segment) -> list[Contact]:
        """Evaluate segment criteria and return matching contacts."""
        # Get the user's contacts
        stmt = select(Contact).where(Contact.user_id == segment.user_id)
        result = await self.session.execute(stmt)
        contacts = list(result.scalars().all())
        
        # If no filter criteria, return all contacts
        if not segment.filter_criteria:
            return contacts
        
        # Apply filters
        filtered_contacts = []
        criteria = segment.filter_criteria
        
        for contact in contacts:
            matches = True
            
            # Check status filter
            if "status" in criteria and contact.status != criteria["status"]:
                matches = False
            
            # Check source filter
            if "source" in criteria and contact.source != criteria["source"]:
                matches = False
            
            # Check tags filter
            if "tags" in criteria and criteria["tags"]:
                contact_stmt = select(ContactTag).where(ContactTag.contact_id == contact.id)
                contact_result = await self.session.execute(contact_stmt)
                contact_tags = [ct.tag_id for ct in contact_result.scalars().all()]
                
                if not any(tag_id in contact_tags for tag_id in criteria["tags"]):
                    matches = False
            
            # Check list filter
            if "lists" in criteria and criteria["lists"]:
                list_stmt = select(ListContact).where(ListContact.contact_id == contact.id)
                list_result = await self.session.execute(list_stmt)
                contact_lists = [lc.list_id for lc in list_result.scalars().all()]
                
                if not any(list_id in contact_lists for list_id in criteria["lists"]):
                    matches = False
            
            if matches:
                filtered_contacts.append(contact)
        
        return filtered_contacts
