"""Template request and response schemas."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TemplateCreateRequest(BaseModel):
    """Schema for creating an email template."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=255)
    subject: str = Field(..., min_length=1, max_length=255)
    html_content: str = Field(default="", max_length=500000)
    plain_text_content: str = Field(default="", max_length=500000)
    preview_text: str = Field(default="", max_length=500)
    template_type: str = Field(default="standard", max_length=30)
    template_variables: list[str] = Field(default_factory=list)
    is_active: bool = True


class TemplateUpdateRequest(BaseModel):
    """Schema for updating a template."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=255)
    subject: str | None = Field(default=None, min_length=1, max_length=255)
    html_content: str | None = Field(default=None, max_length=500000)
    plain_text_content: str | None = Field(default=None, max_length=500000)
    preview_text: str | None = Field(default=None, max_length=500)
    template_type: str | None = Field(default=None, max_length=30)
    template_variables: list[str] | None = None
    is_active: bool | None = None


class TemplateResponse(BaseModel):
    """Public payload for a template."""

    id: str
    user_id: str
    name: str
    subject: str
    html_content: str = ""
    plain_text_content: str = ""
    preview_text: str = ""
    template_type: str
    template_variables: list[str] = Field(default_factory=list)
    is_active: bool = True
    usage_count: int = 0
    created_at: str
    updated_at: str
