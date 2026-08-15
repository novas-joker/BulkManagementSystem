"""Repository pattern implementations."""

from .base import BaseRepository
from .contact_repository import ContactRepository
from .template_repository import TemplateRepository
from .user_repository import UserRepository

__all__ = ["BaseRepository", "ContactRepository", "TemplateRepository", "UserRepository"]
