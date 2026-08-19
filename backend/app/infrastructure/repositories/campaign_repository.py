"""Repository for campaign persistence and lookup."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import Campaign

from .base import BaseRepository


class CampaignRepository(BaseRepository[Campaign]):
    """Database access for campaigns."""

    model = Campaign

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_user_and_name(self, user_id: str, name: str) -> Campaign | None:
        """Return a campaign by name for a user."""
        stmt = select(Campaign).where(Campaign.user_id == user_id, Campaign.name == name)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_for_user(self, user_id: str) -> list[Campaign]:
        """Return all campaigns belonging to a user."""
        stmt = select(Campaign).where(Campaign.user_id == user_id).order_by(Campaign.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
