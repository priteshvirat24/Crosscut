"""LangGraph Orchestrator for Crosscut.

Defines the flow of agents and executes them.
"""

from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import StateGraph, END

from app.agents.state import CrosscutState
from app.agents.diff_intelligence import diff_intelligence_agent
from app.agents.orbit_traversal import orbit_traversal_agent
from app.agents.test_selection import test_selection_agent
from app.agents.pipeline import pipeline_agent
from app.agents.communication import communication_agent

logger = logging.getLogger(__name__)

def build_graph() -> StateGraph:
    """Build the LangGraph workflow for Crosscut."""
    workflow = StateGraph(CrosscutState)

    # Add nodes
    workflow.add_node("diff_analyzer", diff_intelligence_agent)
    workflow.add_node("orbit_traversal", orbit_traversal_agent)
    workflow.add_node("test_selection", test_selection_agent)
    workflow.add_node("pipeline", pipeline_agent)
    workflow.add_node("communication", communication_agent)

    # Set entry point
    workflow.set_entry_point("diff_analyzer")

    # Define edges
    # Check if there are changes to analyze
    def should_continue(state: CrosscutState) -> str:
        report = state.get("change_report", {})
        if report.get("total_changes", 0) == 0:
            return "communication"
        return "orbit_traversal"

    workflow.add_conditional_edges(
        "diff_analyzer",
        should_continue,
        {
            "orbit_traversal": "orbit_traversal",
            "communication": "communication",
        }
    )

    workflow.add_edge("orbit_traversal", "test_selection")
    workflow.add_edge("test_selection", "pipeline")
    workflow.add_edge("pipeline", "communication")
    workflow.add_edge("communication", END)

    return workflow.compile()

# Singleton graph instance
crosscut_graph = build_graph()

async def run_analysis(initial_state: dict[str, Any]) -> dict[str, Any]:
    """Execute the full Crosscut pipeline."""
    try:
        logger.info("Starting Crosscut pipeline", extra={"analysis_id": initial_state.get("analysis_id")})
        # Execute the graph synchronously, but wrap it in an async-friendly way if the agents are async
        final_state = await crosscut_graph.ainvoke(initial_state)
        return final_state
    except Exception as e:
        logger.exception("Pipeline failed")
        if "errors" not in initial_state:
            initial_state["errors"] = []
        initial_state["errors"].append(str(e))
        return initial_state
