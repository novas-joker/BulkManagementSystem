"""Authentication service for user login and token issuance."""

import secrets
from datetime import timedelta

from app.application.services.base_service import BaseService
from app.core.security import create_access_token, decode_token, hash_password, verify_password
from app.core.config import settings
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository


class AuthService(BaseService[UserRepository]):
    """Business logic for authentication and user identity."""

    async def authenticate(self, email: str, password: str) -> dict:
        """Authenticate a user and issue an access token and refresh token."""
        user = await self.repository.get_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        access_token = create_access_token(
            {"sub": user.id, "email": user.email, "role": user.role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        # Generate refresh token
        refresh_token = secrets.token_urlsafe(64)
        from app.core.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            refresh_token_repo = RefreshTokenRepository(db)
            await refresh_token_repo.create_for_user(
                user.id,
                refresh_token,
                timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS),
            )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
            },
        }

    async def register_user(self, email: str, password: str, full_name: str) -> dict:
        """Create a new user account."""
        existing = await self.repository.get_by_email(email)
        if existing:
            raise ValueError("User with this email already exists")

        from app.infrastructure.database.models import User

        user = User(
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
        )

        created = await self.repository.create(user)
        access_token = create_access_token(
            {"sub": created.id, "email": created.email, "role": created.role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        # Generate refresh token
        refresh_token = secrets.token_urlsafe(64)
        from app.core.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            refresh_token_repo = RefreshTokenRepository(db)
            await refresh_token_repo.create_for_user(
                created.id,
                refresh_token,
                timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS),
            )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": created.id,
                "email": created.email,
                "full_name": created.full_name,
                "role": created.role,
            },
        }

    async def refresh_access_token(self, refresh_token: str, db) -> dict:
        """Validate refresh token and issue a new access token."""
        refresh_token_repo = RefreshTokenRepository(db)

        # Validate refresh token
        if not await refresh_token_repo.is_valid(refresh_token):
            raise ValueError("Invalid or expired refresh token")

        token_obj = await refresh_token_repo.get_by_token(refresh_token)
        user = await self.repository.get(token_obj.user_id)

        if not user:
            raise ValueError("User not found")

        # Create new access token
        new_access_token = create_access_token(
            {"sub": user.id, "email": user.email, "role": user.role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
            },
        }

    async def logout(self, user_id: str, db) -> bool:
        """Logout user by revoking all their refresh tokens."""
        refresh_token_repo = RefreshTokenRepository(db)
        return await refresh_token_repo.revoke_all_for_user(user_id)
