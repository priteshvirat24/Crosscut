"""Settings management endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import SettingsDep
from app.schemas import AppSettings

router = APIRouter()


@router.get("/settings", response_model=AppSettings)
async def get_settings(settings: SettingsDep) -> AppSettings:
    """Get current application settings."""
    return AppSettings(
        gitlab_url=settings.gitlab_url,
        orbit_mode=settings.orbit_mode.value,
        llm_provider=settings.llm_provider.value,
        severity_threshold=settings.severity_threshold,
        auto_create_issues=settings.auto_create_issues,
        notify_owners=settings.notify_owners,
        max_dependency_depth=settings.max_dependency_depth,
        confidence_threshold=settings.confidence_threshold,
    )
