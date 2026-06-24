"""FastAPI application factory and entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.config import get_settings
from app.api.routes import analyses, dashboard, health, settings as settings_routes, webhooks
from app.storage.database import engine, create_tables


logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan — startup and shutdown."""
    settings = get_settings()
    logger.info(
        "orbit_sentinel.starting",
        env=settings.app_env.value,
        debug=settings.app_debug,
    )

    # Create tables on startup (dev mode — use Alembic in production)
    if settings.is_development:
        await create_tables()

    yield

    # Cleanup
    await engine.dispose()
    logger.info("orbit_sentinel.shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Orbit Sentinel",
        description=(
            "AI-powered Cross-Repository Change Intelligence Agent. "
            "Know every repository you'll break before you merge."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routes ────────────────────────────────────────────────────────────
    app.include_router(health.router, tags=["Health"])
    app.include_router(webhooks.router, prefix="/api/v1", tags=["Webhooks"])
    app.include_router(analyses.router, prefix="/api/v1", tags=["Analyses"])
    app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
    app.include_router(settings_routes.router, prefix="/api/v1", tags=["Settings"])

    return app


app = create_app()
