"""Authentication service for user login and token issuance."""

from datetime import timedelta

from app.application.services.base_service import BaseService
from app.core.security import create_access_token, hash_password, verify_password
from app.infrastructure.repositories.user_repository import UserRepository


class AuthService(BaseService[UserRepository]):
    """Business logic for authentication and user identity."""

    async def authenticate(self, email: str, password: str) -> dict:
        """Authenticate a user and issue an access token."""
        user = await self.repository.get_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        access_token = create_access_token(
            {"sub": user.id, "email": user.email, "role": user.role},
            expires_delta=timedelta(minutes=30),
        )

        return {
            "access_token": access_token,
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
            expires_delta=timedelta(minutes=30),
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": created.id,
                "email": created.email,
                "full_name": created.full_name,
                "role": created.role,
            },
        }
