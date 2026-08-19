"""Campaign orchestration service."""
from __future__ import annotations

from datetime import datetime

from app.domain.entities.campaign import Campaign, CampaignStatus, CampaignType
from app.infrastructure.email.providers.factory import EmailProviderFactory


class CampaignService:
    """Service for campaign lifecycle and validation rules."""

    VALID_STATUS_TRANSITIONS = {
        CampaignStatus.DRAFT: {CampaignStatus.SCHEDULED, CampaignStatus.QUEUED, CampaignStatus.SENDING},
        CampaignStatus.SCHEDULED: {CampaignStatus.DRAFT, CampaignStatus.QUEUED, CampaignStatus.SENDING, CampaignStatus.CANCELLED},
        CampaignStatus.QUEUED: {CampaignStatus.SENDING, CampaignStatus.CANCELLED},
        CampaignStatus.SENDING: {CampaignStatus.SENT, CampaignStatus.PAUSED, CampaignStatus.FAILED, CampaignStatus.CANCELLED},
        CampaignStatus.PAUSED: {CampaignStatus.SENDING, CampaignStatus.CANCELLED},
        CampaignStatus.SENT: set(),
        CampaignStatus.CANCELLED: set(),
        CampaignStatus.FAILED: set(),
    }

    def __init__(self, repository, template_repository=None):
        self.repository = repository
        self.template_repository = template_repository

    async def create_campaign(self, user_id: str, payload: dict) -> dict:
        """Create a campaign after validating user ownership of the template and payload."""
        name = (payload.get("name") or "").strip()
        subject = (payload.get("subject") or "").strip()
        template_id = payload.get("template_id")

        if not name:
            raise ValueError("Campaign name is required")
        if not subject:
            raise ValueError("Campaign subject is required")

        existing = await self.repository.get_by_user_and_name(user_id, name)
        if existing:
            raise ValueError("Campaign with this name already exists")

        if template_id and self.template_repository is not None:
            template = await self.template_repository.get_by_id(template_id)
            if not template or template.user_id != user_id:
                raise ValueError("Template not found or not owned by this user")

        campaign = Campaign(
            user_id=user_id,
            template_id=template_id,
            name=name,
            subject=subject,
            status=CampaignStatus.DRAFT,
            campaign_type=CampaignType(payload.get("campaign_type", CampaignType.BULK.value)),
            audience_criteria=payload.get("audience_criteria", {}),
            scheduled_at=payload.get("scheduled_at"),
            is_test=bool(payload.get("is_test", False)),
        )

        created = await self.repository.create(campaign)
        return self._serialize(created)

    async def get_campaign(self, user_id: str, campaign_id: str):
        """Fetch a campaign for a user."""
        campaign = await self.repository.get_by_id(campaign_id)
        if not campaign or campaign.user_id != user_id:
            return None
        return self._serialize(campaign)

    async def list_campaigns(self, user_id: str) -> list[dict]:
        """List campaigns for a user."""
        campaigns = await self.repository.list_for_user(user_id)
        return [self._serialize(campaign) for campaign in campaigns]

    async def update_campaign(self, user_id: str, campaign_id: str, payload: dict):
        """Update a campaign and enforce valid state transitions."""
        campaign = await self.repository.get_by_id(campaign_id)
        if not campaign or campaign.user_id != user_id:
            return None

        if "status" in payload and payload["status"] is not None:
            desired_status = CampaignStatus(payload["status"])
            allowed = self.VALID_STATUS_TRANSITIONS.get(campaign.status, set())
            if desired_status not in allowed:
                raise ValueError("Invalid campaign status transition")
            campaign.status = desired_status

        for field in ["name", "subject", "template_id", "campaign_type", "audience_criteria", "scheduled_at", "is_test"]:
            if field in payload and payload[field] is not None:
                setattr(campaign, field, payload[field])

        campaign.updated_at = datetime.utcnow()
        updated = await self.repository.update(campaign)
        return self._serialize(updated)

    async def delete_campaign(self, user_id: str, campaign_id: str) -> bool:
        """Delete a campaign if it belongs to the user."""
        campaign = await self.repository.get_by_id(campaign_id)
        if not campaign or campaign.user_id != user_id:
            return False
        await self.repository.delete(campaign)
        return True

    async def send_test_email(self, user_id: str, campaign_id: str, recipient_email: str) -> dict:
        """Send a test email using the campaign template to a single recipient."""
        campaign = await self.repository.get_by_id(campaign_id)
        if not campaign or campaign.user_id != user_id:
            raise ValueError("Campaign not found or not owned by this user")

        if not campaign.template_id and self.template_repository is None:
            raise ValueError("Campaign template is required for a test send")

        template = None
        if self.template_repository is not None:
            template = await self.template_repository.get_by_id(campaign.template_id)
            if not template or template.user_id != user_id:
                raise ValueError("Template not found or not owned by this user")
        elif hasattr(campaign, "template"):
            template = campaign.template

        if template is None:
            raise ValueError("Campaign template is required for a test send")

        provider = EmailProviderFactory.get_provider("smtp")
        subject = (template.subject or campaign.subject or "Test email").strip() or "Test email"
        result = provider.send(
            to_email=recipient_email,
            subject=subject,
            body=template.html_content or template.text_content or template.plain_text_content or "",
            from_email=getattr(provider, "username", "noreply@example.com"),
            metadata={
                "campaign_id": campaign_id,
                "template_id": campaign.template_id,
                "user_id": user_id,
            },
        )

        return {
            "status": result.status,
            "provider": result.provider,
            "message": f"Test email sent to {recipient_email}" if result.success else (result.error or "Email delivery failed"),
            "success": bool(result.success),
        }

    @staticmethod
    def _serialize(campaign) -> dict:
        return {
            "id": campaign.id,
            "user_id": campaign.user_id,
            "template_id": campaign.template_id,
            "name": campaign.name,
            "subject": campaign.subject,
            "status": campaign.status.value if hasattr(campaign.status, "value") else campaign.status,
            "campaign_type": campaign.campaign_type.value if hasattr(campaign.campaign_type, "value") else campaign.campaign_type,
            "audience_criteria": campaign.audience_criteria or {},
            "scheduled_at": campaign.scheduled_at.isoformat() if campaign.scheduled_at else None,
            "sent_at": campaign.sent_at.isoformat() if campaign.sent_at else None,
            "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
            "updated_at": campaign.updated_at.isoformat() if campaign.updated_at else None,
            "total_recipients": campaign.total_recipients,
            "delivered_count": campaign.delivered_count,
            "opened_count": campaign.opened_count,
            "clicked_count": campaign.clicked_count,
            "bounced_count": campaign.bounced_count,
            "failed_count": campaign.failed_count,
            "is_test": campaign.is_test,
        }
