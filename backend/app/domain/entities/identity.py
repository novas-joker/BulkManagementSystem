"""
Authentication and session domain entities.
"""
from datetime import datetime
from typing import Optional

from dataclasses import dataclass, field


@dataclass
class RefreshToken:
    """Refresh token issued to a user session."""
    id: Optional[str] = None
    user_id: str = ""
    token: str = ""
    expires_at: Optional[datetime] = None
    revoked: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_expired(self, current_time: Optional[datetime] = None) -> bool:
        """Check if the token has expired."""
        if current_time is None:
            current_time = datetime.utcnow()
        if self.expires_at is None:
            return False
        return current_time >= self.expires_at
