"""Segment request and response schemas."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class SegmentCreateRequest(BaseModel):
    """Schema for creating a segment."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=1000)
    filter_criteria: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class SegmentUpdateRequest(BaseModel):
    """Schema for updating a segment."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    filter_criteria: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class SegmentResponse(BaseModel):
    """Public payload for a segment."""

    id: str
    user_id: str
    name: str
    description: str = ""
    filter_criteria: dict[str, Any] = Field(default_factory=dict)
    contact_count: int = 0
    is_active: bool = True
    created_at: str
    updated_at: str


class SegmentPreviewResponse(BaseModel):
    """Preview of contacts matching a segment."""

    segment_id: str
    segment_name: str
    total_contacts: int
    contacts: list[dict] = Field(default_factory=list)
