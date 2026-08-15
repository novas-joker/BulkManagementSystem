"""Repository for refresh token operations."""

from datetime import datetime, timedelta

from sqlalchemy import and_, select, update

from app.infrastructure.database.models import RefreshToken
from app.infrastructure.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Data access layer for RefreshToken entities."""

    async def create_for_user(self, user_id: str, token: str, expires_delta: timedelta | None = None) -> dict:
        """Create a new refresh token for a user."""
        expires_at = None
        if expires_delta:
            expires_at = datetime.utcnow() + expires_delta

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=False,
        )
        created = await self.create(refresh_token)
        return self._serialize(created)

    async def get_by_token(self, token: str) -> RefreshToken | None:
        """Retrieve a refresh token by its token value."""
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def is_valid(self, token: str) -> bool:
        """Check if a refresh token is valid (not revoked and not expired)."""
        refresh_token = await self.get_by_token(token)
        if not refresh_token:
            return False

        if refresh_token.revoked:
            return False

        if refresh_token.expires_at and datetime.utcnow() > refresh_token.expires_at:
            return False

        return True

    async def revoke(self, token_id: str, user_id: str) -> bool:
        """Revoke a refresh token."""
        stmt = (
            update(RefreshToken)
            .where(and_(RefreshToken.id == token_id, RefreshToken.user_id == user_id))
            .values(revoked=True)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def revoke_all_for_user(self, user_id: str) -> bool:
        """Revoke all refresh tokens for a user (logout all sessions)."""
        stmt = update(RefreshToken).where(RefreshToken.user_id == user_id).values(revoked=True)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def list_for_user(self, user_id: str) -> list[dict]:
        """List all active refresh tokens for a user."""
        stmt = (
            select(RefreshToken)
            .where(and_(RefreshToken.user_id == user_id, RefreshToken.revoked == False))
            .order_by(RefreshToken.created_at.desc())
        )
        result = await self.db.execute(stmt)
        tokens = result.scalars().all()
        return [self._serialize(token) for token in tokens]

    @staticmethod
    def _serialize(token: RefreshToken) -> dict:
        """Serialize refresh token to dict."""
        return {
            "id": token.id,
            "user_id": token.user_id,
            "token": token.token,
            "expires_at": token.expires_at.isoformat() if token.expires_at else None,
            "revoked": token.revoked,
            "created_at": token.created_at.isoformat() if token.created_at else None,
        }
