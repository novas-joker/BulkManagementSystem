"""Mailing list request and response schemas."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MailingListCreateRequest(BaseModel):
    """Schema for creating a mailing list."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=1000)
    is_active: bool = True


class MailingListUpdateRequest(BaseModel):
    """Schema for updating a mailing list."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_active: Optional[bool] = None


class MailingListResponse(BaseModel):
    """Public payload for a mailing list."""

    id: str
    user_id: str
    name: str
    description: str = ""
    contact_count: int = 0
    is_active: bool = True
    created_at: str
    updated_at: str


class ListContactResponse(BaseModel):
    """Contact in a mailing list."""

    id: str
    email: str
    first_name: str = ""
    last_name: str = ""
    status: str
    added_at: str
