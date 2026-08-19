"""Suppression list request and response schemas."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SuppressionCreateRequest(BaseModel):
    """Schema for adding an email to suppression list."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    reason: str = Field(default="", max_length=500)
    source: str = Field(default="manual", max_length=50)


class SuppressionBulkCreateRequest(BaseModel):
    """Schema for adding multiple emails to suppression list."""

    model_config = ConfigDict(str_strip_whitespace=True)

    emails: list[EmailStr]
    reason: str = Field(default="", max_length=500)
    source: str = Field(default="manual", max_length=50)


class SuppressionResponse(BaseModel):
    """Public payload for a suppressed email."""

    id: str
    user_id: str
    email: EmailStr
    reason: str = ""
    source: str
    created_at: str
