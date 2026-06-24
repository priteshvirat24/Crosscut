"""Analysis database models — core domain entities for Crosscut."""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Analysis(Base, UUIDMixin, TimestampMixin):
    """A single test optimization analysis run triggered by an MR or manual request."""

    __tablename__ = "analyses"

    # ── Source ────────────────────────────────────────────────────────────
    project_id: Mapped[int] = mapped_column(Integer, nullable=False)
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mr_id: Mapped[int] = mapped_column(Integer, nullable=False)
    mr_iid: Mapped[int] = mapped_column(Integer, nullable=False)
    mr_title: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    mr_url: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    source_branch: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    target_branch: Mapped[str] = mapped_column(String(255), nullable=False, default="main")

    # ── Status ────────────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending, running, completed, failed

    # ── Results & Savings ──────────────────────────────────────────────────
    total_tests_available: Mapped[int] = mapped_column(Integer, default=0)
    selected_tests_count: Mapped[int] = mapped_column(Integer, default=0)
    ci_minutes_saved: Mapped[float | None] = mapped_column(Float, nullable=True)
    percentage_reduction: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_original_runtime: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estimated_optimized_runtime: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ── Raw data ──────────────────────────────────────────────────────────
    change_report: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    dependency_graph: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    pipeline_report: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    executive_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_log: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────
    impacted_tests: Mapped[list[ImpactedTest]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )
    pipeline_executions: Mapped[list[PipelineExecution]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )


class ImpactedTest(Base, UUIDMixin, TimestampMixin):
    """A test discovered via Orbit that is impacted by the code changes."""

    __tablename__ = "impacted_tests"

    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analyses.id"), nullable=False
    )

    # ── Test details ────────────────────────────────────────────────────
    repository: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    test_name: Mapped[str] = mapped_column(String(500), nullable=False)
    dependency_depth: Mapped[int] = mapped_column(Integer, default=1)
    
    # ── Source link ─────────────────────────────────────────────────────
    changed_symbol_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reasoning: Mapped[str] = mapped_column(Text, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────
    analysis: Mapped[Analysis] = relationship(back_populates="impacted_tests")


class PipelineExecution(Base, UUIDMixin, TimestampMixin):
    """A record of the targeted test pipeline execution."""

    __tablename__ = "pipeline_executions"

    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analyses.id"), nullable=False
    )

    # ── Pipeline info ───────────────────────────────────────────────────
    pipeline_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="running"
    )  # running, passed, failed

    # ── Execution details ─────────────────────────────────────────────────
    tests_run: Mapped[int] = mapped_column(Integer, default=0)
    tests_passed: Mapped[int] = mapped_column(Integer, default=0)
    tests_failed: Mapped[int] = mapped_column(Integer, default=0)
    runtime_seconds: Mapped[int] = mapped_column(Integer, default=0)
    log_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────
    analysis: Mapped[Analysis] = relationship(back_populates="pipeline_executions")
