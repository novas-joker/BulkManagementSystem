"""Base email provider abstractions used by MailForge."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class EmailSendResult:
    """Standardized result for all provider attempts."""
    success: bool
    provider: str
    status: str
    to_email: str
    message_id: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class EmailProvider(Protocol):
    """Contract for all email-delivery providers."""

    provider_name: str

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
        """Send an email message."""
        ...


class BaseEmailProvider:
    """Shared behavior for concrete email providers."""

    provider_name = "base"

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
        raise NotImplementedError("Concrete provider must implement send().")
