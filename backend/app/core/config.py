"""
Application Configuration using Pydantic Settings
Manages all environment variables for MailForge
"""
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    # ─── Application ──────────────────────────────────────────────────────────
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_URL: str = "http://localhost:5000"
    FRONTEND_URL: str = "http://localhost:5173"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    
    # ─── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://mailforge:mailforge_password@localhost:5432/mailforge_db"
    SYNC_DATABASE_URL: str = "postgresql://mailforge:mailforge_password@localhost:5432/mailforge_db"
    
    # ─── Redis (Broker & Cache) ───────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ─── JWT Configuration ───────────────────────────────────────────────────
    JWT_SECRET: str = "local-dev-jwt-secret-change-later"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7

    # ─── Security & Encryption ───────────────────────────────────────────────
    ENCRYPTION_KEY: str = "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
    
    # ─── ZeptoMail Configuration ─────────────────────────────────────────────
    ZEPTOMAIL_API_URL: str = "https://api.zeptomail.com/v1.1/email"
    ZEPTOMAIL_SEND_MAIL_TOKEN: str = ""
    ZEPTOMAIL_MOCK: bool = True
    
    # ─── SMTP Configuration (Fallback) ───────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    
    # ─── Zoho Campaigns Configuration ────────────────────────────────────────
    ZOHO_CLIENT_ID: str = ""
    ZOHO_CLIENT_SECRET: str = ""
    ZOHO_REFRESH_TOKEN: str = ""
    ZOHO_CAMPAIGNS_API_URL: str = "https://campaigns.zoho.com/api/v1.1"
    ZOHO_CAMPAIGNS_MOCK: bool = True
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.APP_ENV == "development"
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.APP_ENV == "production"


# Global settings instance
settings = Settings()
