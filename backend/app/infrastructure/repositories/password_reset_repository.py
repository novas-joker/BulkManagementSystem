"""Repository for password reset tokens."""

from datetime import datetime

from sqlalchemy import delete, select

from app.infrastructure.database.models import PasswordResetToken
from app.infrastructure.repositories.base import BaseRepository


class PasswordResetTokenRepository(BaseRepository[PasswordResetToken]):
    model = PasswordResetToken

    async def delete_for_user(self, user_id: str) -> None:
        await self.session.execute(delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id))
        await self.session.commit()

    async def get_valid(self, token_hash: str) -> PasswordResetToken | None:
        result = await self.session.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > datetime.utcnow(),
            )
        )
        return result.scalars().first()
