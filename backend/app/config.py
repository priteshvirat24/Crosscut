"""Application configuration via Pydantic Settings."""

from __future__ import annotations

from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class OrbitMode(str, Enum):
    API = "api"
    CLI = "cli"
    MOCK = "mock"


class Settings(BaseSettings):
    """Central configuration sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────────────────
    app_name: str = "crosscut"
    app_env: Environment = Environment.DEVELOPMENT
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    secret_key: str = "change-me-to-a-random-secret-key"

    # ── GitLab ────────────────────────────────────────────────────────────
    gitlab_url: str = "https://gitlab.com"
    gitlab_token: str = ""
    gitlab_webhook_secret: str = ""

    # ── GitLab Orbit ──────────────────────────────────────────────────────
    orbit_api_url: str = "https://gitlab.com/api/v4/orbit"
    orbit_mode: OrbitMode = OrbitMode.MOCK
    orbit_use_mock: bool = True

    # ── LLM Providers ────────────────────────────────────────────────────
    llm_provider: LLMProvider = LLMProvider.OPENAI

    openai_api_key: str = ""
    openai_model: str = "gpt-4.1"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    google_api_key: str = ""
    google_model: str = "gemini-2.5-pro"

    # ── Database ──────────────────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./crosscut.db"

    # ── Redis ─────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Celery ────────────────────────────────────────────────────────────
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # ── Observability ─────────────────────────────────────────────────────
    log_level: str = "INFO"
    otel_exporter_otlp_endpoint: Optional[str] = None
    otel_service_name: str = "crosscut"

    # ── Analysis ──────────────────────────────────────────────────────────
    severity_threshold: str = "medium"
    auto_create_issues: bool = True
    notify_owners: bool = True
    max_dependency_depth: int = 5
    confidence_threshold: float = 0.7
    analysis_timeout_seconds: int = 120

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"log_level must be one of {valid}")
        return upper

    @property
    def is_development(self) -> bool:
        return self.app_env == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.app_env == Environment.PRODUCTION


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
