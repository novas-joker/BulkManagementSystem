"""Onboarding routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.infrastructure.database.models import User
from app.schemas.auth import OnboardingPhaseOneRequest, OnboardingPhaseOneResponse

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.get("/phase-one", response_model=OnboardingPhaseOneResponse)
async def get_phase_one(
    current_user: User = Depends(get_current_user),
):
    """Return the saved audience-size onboarding answers."""
    return OnboardingPhaseOneResponse(
        subscriber_count_bracket=current_user.subscriber_count_bracket,
        previous_tool=current_user.previous_tool,
        business_industry=current_user.business_industry,
        business_website=current_user.business_website,
        compliance_address=current_user.compliance_address,
        user_primary_goal=current_user.user_primary_goal,
        product_updates_consent=current_user.product_updates_consent,
        onboarding_phase=current_user.onboarding_phase,
        onboarding_completed=current_user.onboarding_completed,
    )


@router.put("/phase-one", response_model=OnboardingPhaseOneResponse)
async def save_phase_one(
    payload: OnboardingPhaseOneRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save audience-size onboarding answers for the authenticated user."""
    fields = (
        "subscriber_count_bracket",
        "previous_tool",
        "business_industry",
        "business_website",
        "compliance_address",
        "user_primary_goal",
        "product_updates_consent",
    )
    for field_name in fields:
        value = getattr(payload, field_name)
        if value is not None:
            setattr(current_user, field_name, value or None)
    current_user.onboarding_phase = payload.onboarding_phase
    current_user.onboarding_completed = payload.onboarding_completed
    await db.commit()
    await db.refresh(current_user)
    return OnboardingPhaseOneResponse(
        subscriber_count_bracket=current_user.subscriber_count_bracket,
        previous_tool=current_user.previous_tool,
        business_industry=current_user.business_industry,
        business_website=current_user.business_website,
        compliance_address=current_user.compliance_address,
        user_primary_goal=current_user.user_primary_goal,
        product_updates_consent=current_user.product_updates_consent,
        onboarding_phase=current_user.onboarding_phase,
        onboarding_completed=current_user.onboarding_completed,
    )