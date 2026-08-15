"""
External provider and suppression domain entities.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from dataclasses import dataclass, field


class ProviderType(str, Enum):
    """External email provider."""
    ZEPTOMAIL = "zeptomail"
    SMTP = "smtp"
    ZOHO_CAMPAIGNS = "zoho_campaigns"


@dataclass
class ProviderCredential:
    """Encrypted credential for external provider integration."""
    id: Optional[str] = None
    user_id: str = ""
    provider: ProviderType = ProviderType.ZEPTOMAIL
    credential_name: str = ""
    encrypted_value: str = ""
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Suppression:
    """Suppressed recipient record for delivery controls."""
    id: Optional[str] = None
    user_id: str = ""
    email: str = ""
    reason: str = ""
    source: str = "manual"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Integration:
    """Third-party integration configuration for a user."""
    id: Optional[str] = None
    user_id: str = ""
    name: str = ""
    provider: ProviderType = ProviderType.ZOHO_CAMPAIGNS
    is_active: bool = True
    config: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
