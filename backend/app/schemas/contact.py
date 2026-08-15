"""Contact request and response schemas."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactCreateRequest(BaseModel):
    """Schema for creating a contact."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    first_name: str = Field(default="", max_length=120)
    last_name: str = Field(default="", max_length=120)
    status: str = Field(default="subscribed", max_length=30)
    source: str = Field(default="manual", max_length=30)
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_valid_email: bool = True


class ContactUpdateRequest(BaseModel):
    """Schema for updating an existing contact."""

    model_config = ConfigDict(str_strip_whitespace=True)

    first_name: Optional[str] = Field(default=None, max_length=120)
    last_name: Optional[str] = Field(default=None, max_length=120)
    status: Optional[str] = Field(default=None, max_length=30)
    source: Optional[str] = Field(default=None, max_length=30)
    custom_fields: Optional[dict[str, Any]] = None
    is_valid_email: Optional[bool] = None


class ContactResponse(BaseModel):
    """Public payload for a contact record."""

    id: str
    user_id: str
    email: EmailStr
    first_name: str = ""
    last_name: str = ""
    status: str
    source: str
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_valid_email: bool = True
    created_at: str
    updated_at: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
