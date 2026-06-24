"""Agent 3: Test Selection Agent.

Discovers impacted tests, eliminates irrelevant tests, and calculates execution reduction.
"""

from __future__ import annotations

import logging
from typing import Any

from app.agents.state import CrosscutState, TestSelectionResult

logger = logging.getLogger(__name__)

def test_selection_agent(state: CrosscutState) -> dict[str, Any]:
    """Identify exactly which tests need to be run based on the Orbit graph."""
    logger.info("Starting Test Selection Agent")
    
    if "execution_log" not in state:
        state["execution_log"] = []

    # Signature Demo: 418 tests -> 12 tests
    impacted_tests = [
        {"repository": "services/checkout-service", "file_path": "tests/test_flow.py", "test_name": "test_checkout_validates_payment", "dependency_depth": 1, "changed_symbol_name": "validate_payment", "reasoning": "Directly imports and calls changed function"},
        {"repository": "services/checkout-service", "file_path": "tests/test_flow.py", "test_name": "test_checkout_fails_on_invalid_region", "dependency_depth": 1, "changed_symbol_name": "validate_payment", "reasoning": "Directly calls checkout flow that hits changed function"},
        {"repository": "services/billing-service", "file_path": "tests/test_subs.py", "test_name": "test_subscription_validation", "dependency_depth": 2, "changed_symbol_name": "validate_payment", "reasoning": "Transitive dependency via process_subscription"},
        {"repository": "services/fraud-detection", "file_path": "tests/test_eval.py", "test_name": "test_risk_scoring", "dependency_depth": 1, "changed_symbol_name": "validate_payment", "reasoning": "Shares validation payload structure"},
        {"repository": "sdk/payment-sdk-python", "file_path": "tests/test_client.py", "test_name": "test_create_payment_intent", "dependency_depth": 1, "changed_symbol_name": "validate_payment", "reasoning": "SDK method wraps the validation endpoint"},
        {"repository": "sdk/payment-sdk-python", "file_path": "tests/test_client.py", "test_name": "test_regional_compliance", "dependency_depth": 1, "changed_symbol_name": "validate_payment", "reasoning": "Explicit test for new region parameter"},
        {"repository": "services/auth-service", "file_path": "tests/test_tokens.py", "test_name": "test_token_region_claims", "dependency_depth": 3, "changed_symbol_name": "validate_payment", "reasoning": "Token scope validation depends on region"},
        {"repository": "platform/compliance-svc", "file_path": "tests/test_audit.py", "test_name": "test_audit_log_format", "dependency_depth": 2, "changed_symbol_name": "validate_payment", "reasoning": "Audit logs capture validation output"},
        {"repository": "services/checkout-service", "file_path": "tests/test_integration.py", "test_name": "test_full_checkout_lifecycle", "dependency_depth": 2, "changed_symbol_name": "validate_payment", "reasoning": "E2E integration test"},
        {"repository": "services/billing-service", "file_path": "tests/test_integration.py", "test_name": "test_invoice_generation", "dependency_depth": 3, "changed_symbol_name": "validate_payment", "reasoning": "E2E billing test"},
        {"repository": "sdk/payment-sdk-node", "file_path": "tests/client.test.ts", "test_name": "should validate payment with region", "dependency_depth": 1, "changed_symbol_name": "validate_payment", "reasoning": "Node SDK wrapper test"},
        {"repository": "services/reporting-dash", "file_path": "tests/test_metrics.py", "test_name": "test_regional_volume_metrics", "dependency_depth": 4, "changed_symbol_name": "validate_payment", "reasoning": "Metrics pipeline aggregates validation events"},
    ]

    total_available = 418
    selected_count = len(impacted_tests)
    reduction = ((total_available - selected_count) / total_available) * 100
    
    # Simulate a reduction of 38 min -> 2 min
    minutes_saved = 36.0

    state["execution_log"].append(f"Test Selection Agent optimized test suite: {total_available} -> {selected_count} ({reduction:.1f}% reduction).")

    result: TestSelectionResult = {
        "impacted_tests": impacted_tests,
        "metrics": {
            "total_tests_available": total_available,
            "selected_tests_count": selected_count,
            "ci_minutes_saved": minutes_saved,
            "percentage_reduction": reduction,
            "estimated_original_runtime": "38 min",
            "estimated_optimized_runtime": "2 min"
        },
        "summary": f"Selected 12 impacted tests out of 418 available. Saved 36 minutes of CI runtime."
    }
    
    logger.info("Test Selection completed")
    return {"test_selection": result}
