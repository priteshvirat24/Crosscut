"""Shared state definition for the LangGraph agent pipeline for Crosscut.

This TypedDict flows through every agent node, accumulating results.
Each agent reads upstream data and writes its own output fields.
"""

from __future__ import annotations

from typing import TypedDict, Optional, Any


# ═══════════════════════════════════════════════════════════════════════════════
# Sub-structures used within the state
# ═══════════════════════════════════════════════════════════════════════════════


class ChangeItem(TypedDict):
    """A single detected code change."""

    change_type: str  # modified, deleted, renamed, added
    symbol_name: str
    symbol_type: str  # function, class, method, constant, api_endpoint
    file_path: str
    line_number: int
    description: str
    before_signature: str
    after_signature: str
    parameters_changed: bool
    return_type_changed: bool


class ChangeReport(TypedDict):
    """Output of the Diff Analyzer Agent."""

    total_changes: int
    files_changed: list[str]
    changes: list[ChangeItem]
    summary: str


class OrbitDependencyNode(TypedDict):
    """A node discovered through Orbit."""

    id: str
    type: str  # repository, file, function, class
    name: str
    repository: str
    file_path: str
    line_number: int
    metadata: dict[str, Any]


class OrbitDependencyEdge(TypedDict):
    """An edge in the Orbit dependency graph."""

    source: str
    target: str
    relationship: str  # calls, imports, depends_on
    weight: float
    metadata: dict[str, Any]


class OrbitDependencyGraph(TypedDict):
    """Output of the Orbit Traversal Agent."""

    nodes: list[OrbitDependencyNode]
    edges: list[OrbitDependencyEdge]
    total_callers: int
    total_repos: int
    query_results_raw: dict[str, Any]


class ImpactedTestItem(TypedDict):
    """A specific test impacted by the change."""

    repository: str
    file_path: str
    test_name: str
    dependency_depth: int
    changed_symbol_name: str | None
    reasoning: str


class TestSelectionMetrics(TypedDict):
    """Test optimization metrics."""

    total_tests_available: int
    selected_tests_count: int
    ci_minutes_saved: float
    percentage_reduction: float
    estimated_original_runtime: str
    estimated_optimized_runtime: str


class TestSelectionResult(TypedDict):
    """Output of the Test Selection Agent."""

    impacted_tests: list[ImpactedTestItem]
    metrics: TestSelectionMetrics
    summary: str


class PipelineReport(TypedDict):
    """Output of the Pipeline Agent."""

    pipeline_id: str
    status: str
    tests_run: int
    tests_passed: int
    tests_failed: int
    runtime_seconds: int
    log_url: str | None
    summary: str


class CommunicationArtifacts(TypedDict):
    """Output of the Communication Agent."""

    mr_comment: str
    executive_summary: str


# ═══════════════════════════════════════════════════════════════════════════════
# Main Pipeline State
# ═══════════════════════════════════════════════════════════════════════════════


class CrosscutState(TypedDict, total=False):
    """The shared state flowing through the entire LangGraph pipeline.

    Each agent reads upstream fields and writes its own output fields.
    `total=False` makes all fields optional so partial state is valid.
    """

    # ── Input ─────────────────────────────────────────────────────────────
    analysis_id: str
    mr_id: int
    mr_iid: int
    project_id: int
    project_name: str
    mr_title: str
    mr_url: str
    source_branch: str
    target_branch: str
    diff_content: str

    # ── Agent 1: Diff Analyzer ────────────────────────────────────────
    change_report: ChangeReport

    # ── Agent 2: Orbit Traversal Agent ─────────────────────────────────
    dependency_graph: OrbitDependencyGraph

    # ── Agent 3: Test Selection Agent ──────────────────────────────────
    test_selection: TestSelectionResult

    # ── Agent 4: Pipeline Agent ──────────────────────────────────────────
    pipeline_report: PipelineReport

    # ── Agent 5: Communication Agent ──────────────────────────────────────────
    communications: CommunicationArtifacts

    # ── Metadata ──────────────────────────────────────────────────────────
    confidence_scores: dict[str, float]
    execution_log: list[str]
    errors: list[str]
    current_step: str
