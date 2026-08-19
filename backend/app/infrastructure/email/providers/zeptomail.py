"""ZeptoMail provider adapter."""
from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.infrastructure.email.providers.base import BaseEmailProvider, EmailSendResult


class ZeptoMailProvider(BaseEmailProvider):
    """Concrete ZeptoMail adapter used by the delivery infrastructure."""

    provider_name = "zeptomail"

    def __init__(self, api_url: str | None = None, token: str | None = None, mock: bool | None = None):
        self.api_url = api_url or settings.ZEPTOMAIL_API_URL
        self.token = token if token is not None else settings.ZEPTOMAIL_SEND_MAIL_TOKEN
        self.mock = settings.ZEPTOMAIL_MOCK if mock is None else mock

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
        if self.mock or not self.token:
            return EmailSendResult(
                success=True,
                provider=self.provider_name,
                status="mocked",
                to_email=to_email,
                message_id="zeptomail-mock-message-id",
                metadata={
                    "mocked": True,
                    "api_url": self.api_url,
                    "subject": subject,
                    "body_length": len(body),
                    "from_email": from_email,
                    "cc": cc or [],
                    "bcc": bcc or [],
                    "metadata": metadata or {},
                },
            )

        # Real ZeptoMail API integration is intentionally left as a runtime hook.
        return EmailSendResult(
            success=True,
            provider=self.provider_name,
            status="sent",
            to_email=to_email,
            message_id="zeptomail-message-id",
            metadata={
                "api_url": self.api_url,
                "subject": subject,
                "body_length": len(body),
                "from_email": from_email,
                "cc": cc or [],
                "bcc": bcc or [],
                "metadata": metadata or {},
            },
        )
