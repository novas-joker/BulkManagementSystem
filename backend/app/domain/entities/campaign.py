"""
Campaign-related domain entities.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from dataclasses import dataclass, field


class CampaignStatus(str, Enum):
    """Campaign lifecycle status."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    FAILED = "failed"


class CampaignType(str, Enum):
    """Campaign type."""
    BULK = "bulk"
    TRANSACTIONAL = "transactional"
    AUTOMATION = "automation"
    NEWSLETTER = "newsletter"


@dataclass
class Campaign:
    """Domain entity representing a campaign."""
    id: Optional[str] = None
    user_id: str = ""
    template_id: Optional[str] = None
    name: str = ""
    subject: str = ""
    status: CampaignStatus = CampaignStatus.DRAFT
    campaign_type: CampaignType = CampaignType.BULK
    audience_criteria: dict = field(default_factory=dict)
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    total_recipients: int = 0
    delivered_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    bounced_count: int = 0
    failed_count: int = 0
    is_test: bool = False

    def is_active(self) -> bool:
        """Return whether the campaign is currently active."""
        return self.status in {CampaignStatus.SCHEDULED, CampaignStatus.SENDING}


@dataclass
class CampaignRecipient:
    """Domain entity representing a recipient in a campaign."""
    id: Optional[str] = None
    campaign_id: str = ""
    contact_id: str = ""
    email: str = ""
    status: str = "pending"
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    bounced_at: Optional[datetime] = None
    failed_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EmailEvent:
    """Captured email engagement event."""
    id: Optional[str] = None
    campaign_id: Optional[str] = None
    contact_id: Optional[str] = None
    email: str = ""
    event_type: str = "sent"
    event_data: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
