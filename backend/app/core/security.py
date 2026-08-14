"""
Security Utilities
JWT token management and encryption/decryption
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

logger = logging.getLogger(__name__)

# ─── Password Hashing ────────────────────────────────────────────────────────

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ─── JWT Token Management ────────────────────────────────────────────────────

def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create access token: {e}")
        raise


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode a JWT token.
    Raises JWTError on invalid or expired token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        logger.warning(f"Invalid token: {e}")
        raise


# ─── Encryption for Secrets (Provider Credentials) ──────────────────────────

def encrypt_secret(secret: str) -> str:
    """Encrypt a secret using Fernet."""
    from cryptography.fernet import Fernet
    
    if not settings.ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY not configured")
    
    cipher = Fernet(settings.ENCRYPTION_KEY.encode())
    return cipher.encrypt(secret.encode()).decode()


def decrypt_secret(encrypted_secret: str) -> str:
    """Decrypt a secret using Fernet."""
    from cryptography.fernet import Fernet, InvalidToken
    
    if not settings.ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY not configured")
    
    try:
        cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        return cipher.decrypt(encrypted_secret.encode()).decode()
    except InvalidToken:
        logger.error("Failed to decrypt secret")
        raise
