import asyncio

import pytest

from app.application.services.campaign_service import CampaignService
from app.domain.entities.campaign import CampaignStatus, CampaignType


class FakeTemplateRepository:
    def __init__(self, template=None):
        self.template = template

    async def get_by_id(self, template_id):
        return self.template if self.template and self.template.id == template_id else None


class FakeCampaignRepository:
    def __init__(self):
        self.items = {}

    async def get_by_user_and_name(self, user_id, name):
        for campaign in self.items.values():
            if campaign.user_id == user_id and campaign.name == name:
                return campaign
        return None

    async def get_by_id(self, campaign_id):
        return self.items.get(campaign_id)

    async def list_for_user(self, user_id):
        return [campaign for campaign in self.items.values() if campaign.user_id == user_id]

    async def create(self, campaign):
        campaign.id = campaign.id or "campaign-1"
        self.items[campaign.id] = campaign
        return campaign

    async def update(self, campaign):
        self.items[campaign.id] = campaign
        return campaign


def test_create_campaign_requires_valid_template_and_name():
    async def run_test():
        template = type("Template", (), {"id": "tpl-1", "user_id": "user-1"})()
        repo = FakeCampaignRepository()
        template_repo = FakeTemplateRepository(template)
        service = CampaignService(repo, template_repo)

        created = await service.create_campaign(
            "user-1",
            {
                "name": "Launch campaign",
                "subject": "Welcome",
                "template_id": "tpl-1",
                "campaign_type": "bulk",
                "audience_criteria": {"list_ids": ["list-1"]},
            },
        )

        assert created["name"] == "Launch campaign"
        assert created["status"] == CampaignStatus.DRAFT.value
        assert created["campaign_type"] == CampaignType.BULK.value

    asyncio.run(run_test())


def test_invalid_transition_raises_value_error():
    async def run_test():
        repo = FakeCampaignRepository()
        service = CampaignService(repo)

        campaign = type(
            "Campaign",
            (),
            {"id": "camp-1", "user_id": "user-1", "status": CampaignStatus.SENT, "name": "Old"},
        )()
        repo.items["camp-1"] = campaign

        with pytest.raises(ValueError, match="Invalid campaign status transition"):
            await service.update_campaign("user-1", "camp-1", {"status": CampaignStatus.DRAFT.value})

    asyncio.run(run_test())


def test_duplicate_name_rejected():
    async def run_test():
        repo = FakeCampaignRepository()
        repo.items["camp-1"] = type(
            "Campaign",
            (),
            {"id": "camp-1", "user_id": "user-1", "name": "Existing", "subject": "Subject"},
        )()
        service = CampaignService(repo)

        with pytest.raises(ValueError, match="already exists"):
            await service.create_campaign(
                "user-1",
                {"name": "Existing", "subject": "Hello", "template_id": "tpl-1"},
            )

    asyncio.run(run_test())


def test_campaign_send_test_email_uses_smtp_provider():
    async def run_test():
        repo = FakeCampaignRepository()
        template = type(
            "Template",
            (),
            {
                "id": "tpl-1",
                "user_id": "user-1",
                "name": "Welcome",
                "subject": "Hello {{first_name}}",
                "html_content": "<p>Hello {{first_name}}</p>",
                "text_content": "Hello {{first_name}}",
            },
        )()
        repo.items["camp-1"] = type(
            "Campaign",
            (),
            {
                "id": "camp-1",
                "user_id": "user-1",
                "template_id": "tpl-1",
                "name": "Campaign 1",
                "subject": "Campaign subject",
            },
        )()

        service = CampaignService(repo, FakeTemplateRepository(template))

        class FakeProvider:
            provider_name = "smtp"
            username = "sender@gmail.com"

            def send(self, **kwargs):
                self.sent = kwargs
                return type("Result", (), {"success": True, "status": "sent", "provider": "smtp"})()

        captured = {}

        def fake_get_provider(provider_name=None):
            provider = FakeProvider()
            captured["provider"] = provider
            return provider

        import app.application.services.campaign_service as campaign_module

        original = campaign_module.EmailProviderFactory.get_provider
        campaign_module.EmailProviderFactory.get_provider = fake_get_provider
        try:
            response = await service.send_test_email("user-1", "camp-1", "user@example.com")
        finally:
            campaign_module.EmailProviderFactory.get_provider = original

        assert response["status"] == "sent"
        assert captured["provider"].sent["to_email"] == "user@example.com"
        assert captured["provider"].sent["subject"] == "Hello {{first_name}}"

    asyncio.run(run_test())
