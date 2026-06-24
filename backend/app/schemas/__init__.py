"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ── Analysis Creation ─────────────────────────────────────────────────────────

class AnalysisCreate(BaseModel):
    """Payload to create a new analysis manually."""

    project_id: int
    mr_iid: int
    project_name: str | None = None


# ── Impacted Test ─────────────────────────────────────────────────────────────

class ImpactedTestResponse(BaseModel):
    """Response schema for an impacted test."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    repository: str
    file_path: str
    test_name: str
    dependency_depth: int
    changed_symbol_name: str | None
    reasoning: str | None


# ── Pipeline Execution ────────────────────────────────────────────────────────

class PipelineExecutionResponse(BaseModel):
    """Response schema for a pipeline execution."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    pipeline_id: str
    status: str
    tests_run: int
    tests_passed: int
    tests_failed: int
    runtime_seconds: int
    log_url: str | None


# ── Analysis Responses ────────────────────────────────────────────────────────

class AnalysisResponse(BaseModel):
    """Base response schema for an analysis listing."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_name: str
    mr_iid: int
    mr_title: str
    mr_url: str
    status: str
    total_tests_available: int
    selected_tests_count: int
    ci_minutes_saved: float | None
    percentage_reduction: float | None
    estimated_original_runtime: str | None
    estimated_optimized_runtime: str | None
    created_at: datetime
    updated_at: datetime


class AnalysisDetailResponse(AnalysisResponse):
    """Detailed response schema for a single analysis."""

    source_branch: str
    target_branch: str
    change_report: dict[str, Any] | None
    dependency_graph: dict[str, Any] | None
    pipeline_report: dict[str, Any] | None
    executive_summary: str | None
    execution_log: list[str] | None
    impacted_tests: list[ImpactedTestResponse] = Field(default_factory=list)
    pipeline_executions: list[PipelineExecutionResponse] = Field(default_factory=list)


# ── Dashboard Statistics ──────────────────────────────────────────────────────

class OverviewStats(BaseModel):
    total_analyses: int
    active_analyses: int
    ci_minutes_saved: float
    tests_skipped: int
    avg_reduction_percentage: float
    repositories_covered: int

class SavingsDistribution(BaseModel):
    high_savings: int
    medium_savings: int
    low_savings: int
    zero_savings: int

class DashboardOverviewResponse(BaseModel):
    stats: OverviewStats
    savings_distribution: SavingsDistribution
    recent_analyses: list[AnalysisResponse]
