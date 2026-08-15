"""
MailForge - Bulk Email Management System
FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.contacts import router as contacts_router
from app.api.routes.templates import router as templates_router
from app.api.routes.lists import router as lists_router
from app.api.routes.tags import router as tags_router
from app.api.routes.segments import router as segments_router
from app.api.routes.suppressions import router as suppressions_router

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

    app.include_router(auth_router)
    app.include_router(contacts_router)
    app.include_router(templates_router)
    app.include_router(lists_router)
    app.include_router(tags_router)
    app.include_router(segments_router)
    app.include_router(suppressions_router)
    return app


# ─── ASGI Application ─────────────────────────────────────────────────────────

app = create_app()
