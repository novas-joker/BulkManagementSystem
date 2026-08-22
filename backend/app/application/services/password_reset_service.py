"""Password reset business logic."""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.security import hash_password
from app.infrastructure.database.models import PasswordResetToken
from app.infrastructure.email.providers.factory import EmailProviderFactory
from app.infrastructure.repositories.password_reset_repository import PasswordResetTokenRepository
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class PasswordResetService:
    def __init__(self, db):
        self.db = db
        self.users = UserRepository(db)
        self.tokens = PasswordResetTokenRepository(db)

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def request_reset(self, email: str) -> None:
        logger.info("Password reset requested for %s", email)
        user = await self.users.get_by_email(email)
        if not user:
            logger.info("Password reset skipped: no account found for %s", email)
            return

        await self.tokens.delete_for_user(user.id)
        raw_token = secrets.token_urlsafe(48)
        self.db.add(PasswordResetToken(
            user_id=user.id,
            token_hash=self._hash_token(raw_token),
            expires_at=datetime.utcnow() + timedelta(minutes=30),
        ))
        await self.db.commit()

        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
        provider = EmailProviderFactory.get_provider("smtp")
        logger.info("Sending password reset email via SMTP to %s", user.email)
        result = provider.send(
            to_email=user.email,
            subject="Reset your MailForge password",
            from_email=settings.SMTP_USERNAME,
            body=(
                f"<p>Hello {user.full_name},</p>"
                f"<p>Reset your MailForge password within 30 minutes:</p>"
                f"<p><a href=\"{reset_url}\">Reset password</a></p>"
                f"<p>If you did not request this, you can ignore this email.</p>"
            ),
            metadata={"purpose": "password_reset"},
        )
        logger.info(
            "Password reset email result: provider=%s status=%s success=%s recipient=%s",
            result.provider,
            result.status,
            result.success,
            user.email,
        )
        if not result.success:
            logger.error("Password reset email failed for %s: %s", user.email, result.error or result.status)
            raise RuntimeError(f"Unable to send password reset email: {result.error or result.status}")

    async def validate_token(self, raw_token: str) -> bool:
        return await self.tokens.get_valid(self._hash_token(raw_token)) is not None

    async def reset_password(self, raw_token: str, new_password: str) -> None:
        token = await self.tokens.get_valid(self._hash_token(raw_token))
        if not token:
            raise ValueError("This password reset link is invalid or expired.")

        user = await self.users.get_by_id(token.user_id)
        if not user:
            raise ValueError("This password reset link is invalid or expired.")

        user.password_hash = hash_password(new_password)
        token.used_at = datetime.utcnow()
        await RefreshTokenRepository(self.db).revoke_all_for_user(user.id)
        await self.db.commit()
