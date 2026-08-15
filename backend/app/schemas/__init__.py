"""Pydantic schemas for request/response validation."""

from .auth import (
    TokenResponse,
    UserLoginRequest,
    UserProfileResponse,
    UserRegisterRequest,
    UserSummary,
)
from .contact import ContactCreateRequest, ContactResponse, ContactUpdateRequest
from .template import TemplateCreateRequest, TemplateResponse, TemplateUpdateRequest

__all__ = [
    "UserRegisterRequest",
    "UserLoginRequest",
    "TokenResponse",
    "UserSummary",
    "UserProfileResponse",
    "ContactCreateRequest",
    "ContactUpdateRequest",
    "ContactResponse",
    "TemplateCreateRequest",
    "TemplateUpdateRequest",
    "TemplateResponse",
]
