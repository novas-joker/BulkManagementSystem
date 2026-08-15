"""
User Domain Entity
Represents a user account in the MailForge application.
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from dataclasses import dataclass, field


class UserRole(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass
class User:
    """
    Domain entity representing a user account.
    
    Attributes:
        id: Unique identifier
        email: User's email address (login credential)
        full_name: User's full name
        password_hash: Hashed password (never stored in plaintext)
        role: User's role in the system
        status: Account status (active, inactive, suspended)
        is_verified: Email verification status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login_at: Last login timestamp
    """
    id: Optional[str] = None
    email: str = ""
    full_name: str = ""
    password_hash: str = ""
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None

    def is_active(self) -> bool:
        """Check if user account is active."""
        return self.status == UserStatus.ACTIVE

    def can_access_campaigns(self) -> bool:
        """Check if user can access campaigns."""
        return self.is_active() and self.is_verified
