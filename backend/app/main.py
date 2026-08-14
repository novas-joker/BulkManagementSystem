"""
MailForge - Bulk Email Management System
FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ─── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

logger = logging.getLogger("mailforge")


# ─── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("MailForge starting up")
    yield
    logger.info("MailForge shut down")


# ─── App factory ──────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="MailForge API",
        description="MailForge — Bulk Email Campaign Management System",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Health Check Route ────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "ok",
            "version": "1.0.0",
            "service": "MailForge API"
        }

    return app


# ─── ASGI Application ─────────────────────────────────────────────────────────

app = create_app()
