"""
Dependency Injection for Routes
Common dependencies like current user, database session
"""
import logging
from typing import Any, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token

logger = logging.getLogger(__name__)

# ─── Security Scheme ─────────────────────────────────────────────────────────

bearer_scheme = HTTPBearer(auto_error=False)


# ─── Token Verification ──────────────────────────────────────────────────────

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """Extract user ID from JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get("sub")
        
        if not user_id:
            raise ValueError("Missing subject in token")
        
        return user_id
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─── Current User ──────────────────────────────────────────────────────────

async def get_current_user(
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Get current user from token."""
    # Placeholder - in real implementation, fetch from database
    return {"id": user_id, "active": True}


# ─── Type Aliases ────────────────────────────────────────────────────────────

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
CurrentUser = Annotated[dict[str, Any], Depends(get_current_user)]
