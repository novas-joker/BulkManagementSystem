"""
Contact Domain Entity
Represents an email contact in the MailForge application.
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from dataclasses import dataclass, field


class ContactStatus(str, Enum):
    """Contact subscription status."""
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    BOUNCED = "bounced"
    COMPLAINED = "complained"


class ContactSource(str, Enum):
    """How the contact was added to the system."""
    MANUAL = "manual"
    IMPORT = "import"
    API = "api"
    SIGNUP_FORM = "signup_form"
    ZOHO_SYNC = "zoho_sync"


@dataclass
class Contact:
    """
    Domain entity representing an email contact.
    
    Attributes:
        id: Unique identifier
        user_id: ID of the user who owns this contact
        email: Contact's email address
        first_name: Contact's first name
        last_name: Contact's last name
        status: Subscription status
        source: How contact was added
        custom_fields: Dictionary of custom field values (for flexibility)
        is_valid_email: Email validation status
        created_at: When contact was added
        updated_at: Last update timestamp
    """
    id: Optional[str] = None
    user_id: str = ""
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    status: ContactStatus = ContactStatus.SUBSCRIBED
    source: ContactSource = ContactSource.MANUAL
    custom_fields: dict = field(default_factory=dict)
    is_valid_email: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def full_name(self) -> str:
        """Get contact's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def is_subscribed(self) -> bool:
        """Check if contact is subscribed."""
        return self.status == ContactStatus.SUBSCRIBED

    def is_deliverable(self) -> bool:
        """Check if contact can receive emails."""
        return self.is_subscribed() and self.is_valid_email
