"""Domain entities for the MailForge application."""

from .user import User, UserRole, UserStatus
from .contact import Contact, ContactStatus, ContactSource
from .audience import MailingList, Tag, Segment
from .template import EmailTemplate, TemplateType
from .campaign import Campaign, CampaignStatus, CampaignType, CampaignRecipient, EmailEvent
from .identity import RefreshToken
from .provider import ProviderCredential, ProviderType, Suppression, Integration

__all__ = [
    "User",
    "UserRole",
    "UserStatus",
    "Contact",
    "ContactStatus",
    "ContactSource",
    "MailingList",
    "Tag",
    "Segment",
    "EmailTemplate",
    "TemplateType",
    "Campaign",
    "CampaignStatus",
    "CampaignType",
    "CampaignRecipient",
    "EmailEvent",
    "RefreshToken",
    "ProviderCredential",
    "ProviderType",
    "Suppression",
    "Integration",
]
