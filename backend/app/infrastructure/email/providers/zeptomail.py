"""ZeptoMail provider adapter."""
from __future__ import annotations

import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import Any

from app.core.config import settings
from app.infrastructure.email.providers.base import BaseEmailProvider, EmailSendResult

logger = logging.getLogger(__name__)


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

        payload = {
            "from": {"address": from_email},
            "to": [{"email_address": {"address": to_email}}],
            "subject": subject,
            "htmlbody": body,
        }
        request = Request(
            self.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Zoho-enczapikey {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=15) as response:
                response_body = json.loads(response.read().decode("utf-8") or "{}")
            return EmailSendResult(
                success=True,
                provider=self.provider_name,
                status="sent",
                to_email=to_email,
                message_id=response_body.get("request_id") or response_body.get("message_id"),
                metadata={"api_url": self.api_url, "subject": subject, "metadata": metadata or {}},
            )
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            logger.error("ZeptoMail password reset delivery failed: %s", type(exc).__name__)
            return EmailSendResult(
                success=False,
                provider=self.provider_name,
                status="failed",
                to_email=to_email,
                error="Email provider request failed.",
                metadata={"api_url": self.api_url, "subject": subject, "metadata": metadata or {}},
            )
