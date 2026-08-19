"""Campaign routes for managing campaign lifecycle."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import BaseModel, EmailStr

from app.application.services.campaign_service import CampaignService
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.infrastructure.repositories.campaign_repository import CampaignRepository
from app.infrastructure.repositories.template_repository import TemplateRepository
from app.schemas.campaign import CampaignCreateRequest, CampaignResponse, CampaignUpdateRequest

logger = logging.getLogger("mailforge.campaigns")
router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


class CampaignTestEmailRequest(BaseModel):
    """Request to send a test email for a campaign."""

    recipient_email: EmailStr


@router.get("", response_model=list[CampaignResponse])
async def list_campaigns(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List campaigns for the signed-in user."""
    try:
        repository = CampaignRepository(db)
        service = CampaignService(repository)
        campaigns = await service.list_campaigns(current_user.id)
        return [CampaignResponse(**campaign) for campaign in campaigns]
    except Exception as exc:
        logger.error(f"Error listing campaigns for user {current_user.id}: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("", response_model=CampaignResponse)
async def create_campaign(
    payload: CampaignCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new campaign."""
    campaign_repo = CampaignRepository(db)
    template_repo = TemplateRepository(db)
    service = CampaignService(campaign_repo, template_repo)

    try:
        campaign = await service.create_campaign(current_user.id, payload.model_dump())
        return CampaignResponse(**campaign)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Fetch a single campaign."""
    try:
        repository = CampaignRepository(db)
        service = CampaignService(repository)
        campaign = await service.get_campaign(current_user.id, campaign_id)

        if campaign is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

        return CampaignResponse(**campaign)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error getting campaign {campaign_id} for user {current_user.id}: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    payload: CampaignUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a campaign."""
    try:
        repository = CampaignRepository(db)
        service = CampaignService(repository)

        updated = await service.update_campaign(current_user.id, campaign_id, payload.model_dump(exclude_unset=True))
        
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

        return CampaignResponse(**updated)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error updating campaign {campaign_id} for user {current_user.id}: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a campaign."""
    try:
        repository = CampaignRepository(db)
        service = CampaignService(repository)
        deleted = await service.delete_campaign(current_user.id, campaign_id)

        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error deleting campaign {campaign_id} for user {current_user.id}: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/{campaign_id}/test-email", status_code=status.HTTP_200_OK)
async def send_campaign_test_email(
    campaign_id: str,
    payload: CampaignTestEmailRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Send a real test email for a campaign using its template and SMTP provider."""
    campaign_repo = CampaignRepository(db)
    template_repo = TemplateRepository(db)
    service = CampaignService(campaign_repo, template_repo)

    try:
        result = await service.send_test_email(current_user.id, campaign_id, str(payload.recipient_email))
        return {
            "status": result["status"],
            "provider": result["provider"],
            "message": result["message"],
            "success": result["success"],
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
