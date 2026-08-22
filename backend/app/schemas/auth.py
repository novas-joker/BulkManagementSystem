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
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: UserSummary


class RefreshTokenRequest(BaseModel):
    """Schema for refreshing an access token."""

    refresh_token: str


class UserProfileResponse(BaseModel):
    """Authenticated user profile returned from protected endpoints."""

    id: str
    email: EmailStr
    full_name: str
    role: str
    status: str
    status: str


class ForgotPasswordRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    token: str = Field(..., min_length=20, max_length=200)
    new_password: str = Field(..., min_length=8, max_length=128)


class OnboardingPhaseOneResponse(BaseModel):
    """Saved onboarding data for the authenticated user."""

    subscriber_count_bracket: Optional[str] = None
    previous_tool: Optional[str] = None
    business_industry: Optional[str] = None
    business_website: Optional[str] = None
    compliance_address: Optional[dict[str, str]] = None
    user_primary_goal: Optional[str] = None
    product_updates_consent: Optional[bool] = None
    onboarding_phase: int = 1
    onboarding_completed: bool = False


class OnboardingPhaseOneRequest(BaseModel):
    """Payload for saving onboarding progress."""

    model_config = ConfigDict(str_strip_whitespace=True)

    subscriber_count_bracket: Optional[str] = Field(default=None, min_length=1, max_length=40)
    previous_tool: Optional[str] = Field(default=None, max_length=120)
    business_industry: Optional[str] = Field(default=None, min_length=1, max_length=80)
    business_website: Optional[str] = Field(default=None, max_length=500)
    compliance_address: Optional[dict[str, str]] = None
    user_primary_goal: Optional[str] = Field(default=None, min_length=1, max_length=80)
    product_updates_consent: Optional[bool] = None
    onboarding_phase: int = Field(default=1, ge=1, le=5)
    onboarding_completed: bool = False
