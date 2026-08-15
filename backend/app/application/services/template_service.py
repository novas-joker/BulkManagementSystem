"""Business logic for email template management."""

from datetime import datetime

from app.application.services.base_service import BaseService
from app.infrastructure.repositories.template_repository import TemplateRepository


class TemplateService(BaseService[TemplateRepository]):
    """Handle template CRUD and user-scoped queries."""

    async def list_templates(self, user_id: str) -> list[dict]:
        """Return all templates for a user."""
        templates = await self.repository.list_for_user(user_id)
        return [self._serialize(template) for template in templates]

    async def get_template(self, user_id: str, template_id: str):
        """Fetch one template if it belongs to the user."""
        template = await self.repository.get_by_id(template_id)
        if not template or template.user_id != user_id:
            return None
        return self._serialize(template)

    async def create_template(self, user_id: str, payload: dict):
        """Create a template for the user."""
        from app.infrastructure.database.models import EmailTemplate

        existing = await self.repository.get_by_user_and_name(user_id, payload["name"])
        if existing:
            raise ValueError("Template with this name already exists")

        template = EmailTemplate(
            user_id=user_id,
            name=payload["name"],
            subject=payload.get("subject", ""),
            html_content=payload.get("html_content", ""),
            plain_text_content=payload.get("plain_text_content", ""),
            preview_text=payload.get("preview_text", ""),
            template_type=payload.get("template_type", "standard"),
            template_variables=payload.get("template_variables", []),
            is_active=payload.get("is_active", True),
        )

        created = await self.repository.create(template)
        return self._serialize(created)

    async def update_template(self, user_id: str, template_id: str, payload: dict):
        """Update a template."""
        template = await self.repository.get_by_id(template_id)
        if not template or template.user_id != user_id:
            return None

        for field in [
            "name",
            "subject",
            "html_content",
            "plain_text_content",
            "preview_text",
            "template_type",
            "template_variables",
            "is_active",
        ]:
            if field in payload and payload[field] is not None:
                setattr(template, field, payload[field])

        template.updated_at = datetime.utcnow()
        updated = await self.repository.update(template)
        return self._serialize(updated)

    async def delete_template(self, user_id: str, template_id: str) -> bool:
        """Delete a template if owned by the user."""
        template = await self.repository.get_by_id(template_id)
        if not template or template.user_id != user_id:
            return False
        await self.repository.delete(template)
        return True

    @staticmethod
    def _serialize(template) -> dict:
        return {
            "id": template.id,
            "user_id": template.user_id,
            "name": template.name,
            "subject": template.subject,
            "html_content": template.html_content,
            "plain_text_content": template.plain_text_content,
            "preview_text": template.preview_text,
            "template_type": template.template_type,
            "template_variables": template.template_variables or [],
            "is_active": template.is_active,
            "usage_count": template.usage_count,
            "created_at": template.created_at.isoformat() if template.created_at else None,
            "updated_at": template.updated_at.isoformat() if template.updated_at else None,
        }
