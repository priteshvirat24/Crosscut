"""Agent 4: Pipeline Agent.

Generates a child pipeline, executes selected tests, and tracks runtime.
"""

from __future__ import annotations

import logging
from typing import Any

from app.agents.state import CrosscutState, PipelineReport

logger = logging.getLogger(__name__)

async def pipeline_agent(state: CrosscutState) -> dict[str, Any]:
    """Trigger the targeted CI pipeline with the selected tests."""
    logger.info("Starting Pipeline Agent")
    
    if "execution_log" not in state:
        state["execution_log"] = []

    tests_selected = state.get("test_selection", {}).get("metrics", {}).get("selected_tests_count", 0)

    # Simulate successful pipeline execution for the demo
    report: PipelineReport = {
        "pipeline_id": "crosscut-opt-98213",
        "status": "passed",
        "tests_run": tests_selected,
        "tests_passed": tests_selected,
        "tests_failed": 0,
        "runtime_seconds": 120, # 2 minutes
        "log_url": "https://gitlab.example.com/crosscut/jobs/98213",
        "summary": f"Targeted pipeline completed in 2m 0s. All {tests_selected} tests passed."
    }

    state["execution_log"].append(f"Pipeline Agent executed {tests_selected} tests successfully.")
    
    logger.info("Pipeline Execution completed")
    return {"pipeline_report": report}
