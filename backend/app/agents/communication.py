"""Agent 5: Communication Agent.

Generates MR comments explaining test selection reasoning and savings.
"""

from __future__ import annotations

import logging
from typing import Any

from app.agents.state import CrosscutState, CommunicationArtifacts

logger = logging.getLogger(__name__)

def generate_mr_comment(state: CrosscutState) -> str:
    """Generate the MR comment detailing test execution savings."""
    changes = state.get("change_report", {}).get("changes", [])
    symbol_names = ", ".join([c["symbol_name"] for c in changes]) if changes else "Unknown"

    test_metrics = state.get("test_selection", {}).get("metrics", {})
    selected = test_metrics.get("selected_tests_count", 0)
    total = test_metrics.get("total_tests_available", 0)
    reduction = test_metrics.get("percentage_reduction", 0.0)
    est_orig = test_metrics.get("estimated_original_runtime", "N/A")
    est_opt = test_metrics.get("estimated_optimized_runtime", "N/A")
    
    pipeline = state.get("pipeline_report", {})
    status = pipeline.get("status", "unknown")

    if status == "passed":
        status_text = "✅ All impacted tests passed"
    else:
        status_text = f"❌ Pipeline failed ({pipeline.get('tests_failed', 0)} tests failed)"

    return f"""### ✂️ Crosscut Analysis Complete

**Changed Symbol(s):**
`{symbol_names}`

**Selected Tests:**
{selected}

**Total Available Tests:**
{total}

**Reduction:**
{reduction:.1f}%

**Estimated Runtime:**
{est_orig} → {est_opt}

**Status:**
{status_text}

---
*Run Full Suite:* [Click here](https://gitlab.com) if additional validation is required.
"""

async def communication_agent(state: CrosscutState) -> dict[str, Any]:
    """Generate communication artifacts for the Crosscut test optimization."""
    logger.info("Starting Communication Agent")
    
    if "execution_log" not in state:
        state["execution_log"] = []

    comment = generate_mr_comment(state)
    
    test_metrics = state.get("test_selection", {}).get("metrics", {})
    exec_summary = f"Crosscut selected {test_metrics.get('selected_tests_count', 0)} tests out of {test_metrics.get('total_tests_available', 0)} available, reducing execution by {test_metrics.get('percentage_reduction', 0.0):.1f}%."

    artifacts: CommunicationArtifacts = {
        "mr_comment": comment,
        "executive_summary": exec_summary,
    }

    state["execution_log"].append("Communication Agent generated MR comment and executive summary.")
    logger.info("Communication Agent completed")

    return {"communications": artifacts}
