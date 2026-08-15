"""Business logic for suppression list management."""

from app.application.services.base_service import BaseService
from app.infrastructure.repositories.suppression_repository import SuppressionRepository


class SuppressionService(BaseService[SuppressionRepository]):
    """Handle suppression list operations."""

    async def list_suppressions(self, user_id: str) -> list[dict]:
        """Return all suppressed emails for a user."""
        suppressions = await self.repository.list_for_user(user_id)
        return [self._serialize(suppression) for suppression in suppressions]

    async def is_suppressed(self, user_id: str, email: str) -> bool:
        """Check if an email is suppressed."""
        return await self.repository.is_suppressed(user_id, email)

    async def suppress_email(self, user_id: str, email: str, reason: str = "", source: str = "manual"):
        """Add an email to the suppression list."""
        suppression = await self.repository.suppress(user_id, email, reason, source)
        return self._serialize(suppression)

    async def unsuppress_email(self, user_id: str, email: str) -> bool:
        """Remove an email from the suppression list."""
        return await self.repository.unsuppress(user_id, email)

    async def suppress_multiple(self, user_id: str, emails: list[str], reason: str = "", source: str = "manual"):
        """Add multiple emails to the suppression list."""
        results = []
        for email in emails:
            suppression = await self.repository.suppress(user_id, email, reason, source)
            results.append(self._serialize(suppression))
        return results

    @staticmethod
    def _serialize(suppression) -> dict:
        return {
            "id": suppression.id,
            "user_id": suppression.user_id,
            "email": suppression.email,
            "reason": suppression.reason,
            "source": suppression.source,
            "created_at": suppression.created_at.isoformat() if suppression.created_at else None,
        }
