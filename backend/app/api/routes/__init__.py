"""API route endpoints."""

from .auth import router as auth_router
from .contacts import router as contacts_router
from .templates import router as templates_router
from .lists import router as lists_router
from .tags import router as tags_router
from .segments import router as segments_router
from .suppressions import router as suppressions_router

__all__ = [
    "auth_router",
    "contacts_router",
    "templates_router",
    "lists_router",
    "tags_router",
    "segments_router",
    "suppressions_router",
]
