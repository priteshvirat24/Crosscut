"""Prediction history model for tracking accuracy over time."""

from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class PredictionHistory(Base, UUIDMixin, TimestampMixin):
    """Records whether past predictions were accurate — used for learning."""

    __tablename__ = "prediction_history"

    analysis_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    project_name: Mapped[str] = mapped_column(String(500), nullable=False)
    mr_iid: Mapped[int] = mapped_column(Integer, nullable=False)

    # ── Prediction ────────────────────────────────────────────────────────
    predicted_risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_risk_category: Mapped[str] = mapped_column(String(50), nullable=False)
    predicted_blast_radius: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_affected_repos: Mapped[int] = mapped_column(Integer, nullable=False)

    # ── Outcome (filled post-merge) ───────────────────────────────────────
    was_merged: Mapped[bool] = mapped_column(Boolean, default=False)
    caused_failures: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    pipeline_failures: Mapped[int] = mapped_column(Integer, default=0)
    actual_affected_repos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    outcome_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # ── Scoring ───────────────────────────────────────────────────────────
    prediction_accurate: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    accuracy_score: Mapped[float | None] = mapped_column(Float, nullable=True)
