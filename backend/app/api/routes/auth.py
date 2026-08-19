"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services import AuthService
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.infrastructure.repositories import UserRepository
from app.schemas import TokenResponse, UserLoginRequest, UserProfileResponse, UserRegisterRequest, RefreshTokenRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register_user(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a user and return a JWT token."""
    user_repository = UserRepository(db)
    service = AuthService(user_repository)
    try:
        result = await service.register_user(payload.email, payload.password, payload.full_name)
        return TokenResponse(**result)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=TokenResponse)
async def login_user(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Login a user and return a JWT token."""
    user_repository = UserRepository(db)
    service = AuthService(user_repository)
    try:
        result = await service.authenticate(payload.email, payload.password)
        return TokenResponse(**result)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh an access token using a refresh token."""
    user_repository = UserRepository(db)
    service = AuthService(user_repository)
    try:
        result = await service.refresh_access_token(payload.refresh_token, db)
        return TokenResponse(**result)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Logout a user by revoking their refresh tokens."""
    user_repository = UserRepository(db)
    service = AuthService(user_repository)
    await service.logout(current_user.id, db)
    return None


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user=Depends(get_current_user),
):
    """Return the authenticated user's profile."""
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        status=current_user.status,
    )
