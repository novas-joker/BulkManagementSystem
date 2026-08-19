"""Campaign request and response schemas."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CampaignCreateRequest(BaseModel):
    """Schema for creating a campaign."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=255)
    subject: str = Field(..., min_length=1, max_length=255)
    template_id: str | None = None
    campaign_type: str = Field(default="bulk", max_length=30)
    audience_criteria: dict[str, Any] = Field(default_factory=dict)
    scheduled_at: str | None = None
    is_test: bool = False


class CampaignUpdateRequest(BaseModel):
    """Schema for updating a campaign."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=255)
    subject: str | None = Field(default=None, min_length=1, max_length=255)
    template_id: str | None = None
    status: str | None = Field(default=None, max_length=30)
    campaign_type: str | None = Field(default=None, max_length=30)
    audience_criteria: dict[str, Any] | None = None
    scheduled_at: str | None = None
    is_test: bool | None = None


class CampaignResponse(BaseModel):
    """Public payload for a campaign."""

    id: str
    user_id: str
    template_id: str | None = None
    name: str
    subject: str
    status: str
    campaign_type: str
    audience_criteria: dict[str, Any] = Field(default_factory=dict)
    scheduled_at: str | None = None
    sent_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    total_recipients: int = 0
    delivered_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    bounced_count: int = 0
    failed_count: int = 0
    is_test: bool = False
