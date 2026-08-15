"""Authentication request and response schemas."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Schema for registering a new user."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)


class UserLoginRequest(BaseModel):
    """Schema for logging in a user."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserSummary(BaseModel):
    """Public user data returned in auth responses."""

    id: str
    email: EmailStr
    full_name: str
    role: str


class TokenResponse(BaseModel):
    """JWT response returned from auth endpoints."""

    access_token: str
    token_type: str = "bearer"
    user: UserSummary


class UserProfileResponse(BaseModel):
    """Authenticated user profile returned from protected endpoints."""

    id: str
    email: EmailStr
    full_name: str
    role: str
    status: str
