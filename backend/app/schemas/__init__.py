"""Pydantic schemas for request/response validation."""

from .auth import (
    TokenResponse,
    UserLoginRequest,
    UserProfileResponse,
    UserRegisterRequest,
    UserSummary,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from .campaign import CampaignCreateRequest, CampaignResponse, CampaignUpdateRequest
from .contact import ContactCreateRequest, ContactResponse, ContactUpdateRequest
from .template import TemplateCreateRequest, TemplateResponse, TemplateUpdateRequest
from .list import MailingListCreateRequest, MailingListResponse, MailingListUpdateRequest, ListContactResponse
from .tag import TagCreateRequest, TagResponse, TagUpdateRequest
from .segment import SegmentCreateRequest, SegmentResponse, SegmentUpdateRequest, SegmentPreviewResponse
from .suppression import SuppressionCreateRequest, SuppressionResponse, SuppressionBulkCreateRequest

__all__ = [
    "UserRegisterRequest",
    "UserLoginRequest",
    "TokenResponse",
    "UserSummary",
    "UserProfileResponse",
    "RefreshTokenRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "CampaignCreateRequest",
    "CampaignUpdateRequest",
    "CampaignResponse",
    "ContactCreateRequest",
    "ContactUpdateRequest",
    "ContactResponse",
    "TemplateCreateRequest",
    "TemplateUpdateRequest",
    "TemplateResponse",
    "MailingListCreateRequest",
    "MailingListUpdateRequest",
    "MailingListResponse",
    "ListContactResponse",
    "TagCreateRequest",
    "TagUpdateRequest",
    "TagResponse",
    "SegmentCreateRequest",
    "SegmentUpdateRequest",
    "SegmentResponse",
    "SegmentPreviewResponse",
    "SuppressionCreateRequest",
    "SuppressionBulkCreateRequest",
    "SuppressionResponse",
]
