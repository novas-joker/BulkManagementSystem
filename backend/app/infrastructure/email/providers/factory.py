"""Factory logic for selecting an email provider."""
from __future__ import annotations

from app.infrastructure.email.providers.mock import MockEmailProvider
from app.infrastructure.email.providers.smtp import SMTPProvider
from app.infrastructure.email.providers.zeptomail import ZeptoMailProvider


class EmailProviderFactory:
    """Create concrete providers for the configured delivery path."""

    @staticmethod
    def get_provider(provider_name: str | None = None):
        provider_name = (provider_name or "zeptomail").lower()

        if provider_name == "mock":
            return MockEmailProvider()
        if provider_name == "smtp":
            return SMTPProvider()
        if provider_name == "zeptomail":
            return ZeptoMailProvider()

        raise ValueError(f"Unsupported provider: {provider_name}")
