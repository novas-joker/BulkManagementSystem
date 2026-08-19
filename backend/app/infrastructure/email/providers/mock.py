"""Mock provider used for local development and tests."""
from __future__ import annotations

from typing import Any

from app.infrastructure.email.providers.base import BaseEmailProvider, EmailSendResult


class MockEmailProvider(BaseEmailProvider):
    """Deterministic provider useful for local development and unit tests."""

    provider_name = "mock"

    def send(
        self,
        *,
        to_email: str,
        subject: str,
        body: str,
        from_email: str,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> EmailSendResult:
        return EmailSendResult(
            success=True,
            provider=self.provider_name,
            status="sent",
            to_email=to_email,
            message_id="mock-message-id",
            metadata={
                "subject": subject,
                "body_length": len(body),
                "from_email": from_email,
                "cc": cc or [],
                "bcc": bcc or [],
                "metadata": metadata or {},
            },
        )
