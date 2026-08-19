"""Repository for campaign persistence and lookup."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import Campaign as CampaignModel

from .base import BaseRepository


class CampaignRepository(BaseRepository[CampaignModel]):
    """Database access for campaigns."""

    model = CampaignModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create(self, campaign) -> CampaignModel:
        """Map the domain campaign to its SQLAlchemy model before persistence."""
        model = CampaignModel(
            id=campaign.id,
            user_id=campaign.user_id,
            template_id=campaign.template_id,
            name=campaign.name,
            subject=campaign.subject,
            status=campaign.status.value if hasattr(campaign.status, "value") else campaign.status,
            campaign_type=(
                campaign.campaign_type.value
                if hasattr(campaign.campaign_type, "value")
                else campaign.campaign_type
            ),
            audience_criteria=campaign.audience_criteria,
            scheduled_at=campaign.scheduled_at,
            sent_at=campaign.sent_at,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            total_recipients=campaign.total_recipients,
            delivered_count=campaign.delivered_count,
            opened_count=campaign.opened_count,
            clicked_count=campaign.clicked_count,
            bounced_count=campaign.bounced_count,
            failed_count=campaign.failed_count,
            is_test=campaign.is_test,
        )
        return await super().create(model)

    async def get_by_user_and_name(self, user_id: str, name: str) -> CampaignModel | None:
        """Return a campaign by name for a user."""
        stmt = select(CampaignModel).where(CampaignModel.user_id == user_id, CampaignModel.name == name)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_for_user(self, user_id: str) -> list[CampaignModel]:
        """Return all campaigns belonging to a user."""
        stmt = select(CampaignModel).where(CampaignModel.user_id == user_id).order_by(CampaignModel.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
