"""Email provider implementations."""

from app.infrastructure.email.providers.base import BaseEmailProvider, EmailProvider, EmailSendResult
from app.infrastructure.email.providers.factory import EmailProviderFactory
from app.infrastructure.email.providers.mock import MockEmailProvider
from app.infrastructure.email.providers.smtp import SMTPProvider
from app.infrastructure.email.providers.zeptomail import ZeptoMailProvider

__all__ = [
    "BaseEmailProvider",
    "EmailProvider",
    "EmailSendResult",
    "EmailProviderFactory",
    "MockEmailProvider",
    "SMTPProvider",
    "ZeptoMailProvider",
]
