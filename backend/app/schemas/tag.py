"""Tag request and response schemas."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TagCreateRequest(BaseModel):
    """Schema for creating a tag."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)


class TagUpdateRequest(BaseModel):
    """Schema for updating a tag."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)


class TagResponse(BaseModel):
    """Public payload for a tag."""

    id: str
    user_id: str
    name: str
    description: str = ""
    contact_count: int = 0
    created_at: str
