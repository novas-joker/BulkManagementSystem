"""Repository pattern implementations."""

from .base import BaseRepository
from .contact_repository import ContactRepository
from .template_repository import TemplateRepository
from .user_repository import UserRepository
from .refresh_token_repository import RefreshTokenRepository
from .list_repository import MailingListRepository
from .tag_repository import TagRepository
from .segment_repository import SegmentRepository
from .suppression_repository import SuppressionRepository

__all__ = [
    "BaseRepository",
    "ContactRepository",
    "TemplateRepository",
    "UserRepository",
    "RefreshTokenRepository",
    "MailingListRepository",
    "TagRepository",
    "SegmentRepository",
    "SuppressionRepository",
]
