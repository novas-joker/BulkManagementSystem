"""SMTP email provider adapter."""
from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Any

from app.core.config import settings
from app.infrastructure.email.providers.base import BaseEmailProvider, EmailSendResult


class SMTPProvider(BaseEmailProvider):
    """Fallback SMTP provider for direct mail delivery."""

    provider_name = "smtp"

    def __init__(self, host: str | None = None, port: int | None = None, username: str | None = None, password: str | None = None):
        self.host = host or settings.SMTP_HOST
        self.port = port if port is not None else settings.SMTP_PORT
        self.username = username if username is not None else settings.SMTP_USERNAME
        self.password = password if password is not None else settings.SMTP_PASSWORD

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
        if not self.host or not self.username or not self.password:
            return EmailSendResult(
                success=False,
                provider=self.provider_name,
                status="not_configured",
                to_email=to_email,
                error="SMTP is not configured.",
                metadata={
                    "host": self.host,
                    "port": self.port,
                    "subject": subject,
                    "from_email": from_email,
                    "metadata": metadata or {},
                },
            )

        try:
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = from_email
            message["To"] = to_email

            if cc:
                message["Cc"] = ", ".join(cc)
            if bcc:
                message["Bcc"] = ", ".join(bcc)

            message.set_content(body if "<" not in body else "This email contains HTML content.")
            if "<" in body and ">" in body:
                message.add_alternative(body, subtype="html")

            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(message)

            return EmailSendResult(
                success=True,
                provider=self.provider_name,
                status="sent",
                to_email=to_email,
                message_id="smtp-message-id",
                metadata={
                    "host": self.host,
                    "port": self.port,
                    "subject": subject,
                    "body_length": len(body),
                    "from_email": from_email,
                    "cc": cc or [],
                    "bcc": bcc or [],
                    "metadata": metadata or {},
                },
            )
        except Exception as exc:  # pragma: no cover - defensive path
            return EmailSendResult(
                success=False,
                provider=self.provider_name,
                status="failed",
                to_email=to_email,
                error=str(exc),
                metadata={
                    "host": self.host,
                    "port": self.port,
                    "subject": subject,
                    "from_email": from_email,
                    "metadata": metadata or {},
                },
            )
