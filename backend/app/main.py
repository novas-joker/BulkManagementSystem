"""
MailForge - Bulk Email Management System
FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.campaigns import router as campaigns_router
from app.api.routes.contacts import router as contacts_router
from app.api.routes.templates import router as templates_router
from app.api.routes.lists import router as lists_router
from app.api.routes.tags import router as tags_router
from app.api.routes.segments import router as segments_router
from app.api.routes.suppressions import router as suppressions_router
from app.api.routes.tracking import router as tracking_router

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
        allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
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

    # ── Exception Handlers ─────────────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all uncaught exceptions with proper CORS headers."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "type": type(exc).__name__},
            headers={
                "Access-Control-Allow-Origin": request.headers.get("origin", "http://localhost:5173"),
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError with proper CORS headers."""
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
            headers={
                "Access-Control-Allow-Origin": request.headers.get("origin", "http://localhost:5173"),
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )

    app.include_router(auth_router)
    app.include_router(campaigns_router)
    app.include_router(contacts_router)
    app.include_router(templates_router)
    app.include_router(lists_router)
    app.include_router(tags_router)
    app.include_router(segments_router)
    app.include_router(suppressions_router)
    app.include_router(tracking_router)
    return app


# ─── ASGI Application ─────────────────────────────────────────────────────────

app = create_app()
