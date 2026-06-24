"""Analysis service — orchestrates the full Crosscut test optimization lifecycle.

Handles:
1. Fetching MR diff from GitLab
2. Running the LangGraph test optimization pipeline
3. Storing results in the database
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import structlog

from app.agents.orchestrator import crosscut_graph
from app.agents.state import CrosscutState
from app.config import get_settings
from app.storage.database import async_session_factory
from app.models.analysis import Analysis, ImpactedTest, PipelineExecution

logger = structlog.get_logger()


# ── Demo diff for hackathon ───────────────────────────────────────────────────

DEMO_DIFF = """diff --git a/src/payment/validator.py b/src/payment/validator.py
index 1a2b3c4..5d6e7f8 100644
--- a/src/payment/validator.py
+++ b/src/payment/validator.py
@@ -15,20 +15,35 @@ from typing import Optional
 from .models import PaymentRequest, ValidationResult
 from .exceptions import PaymentValidationError
 
-def validate_payment(amount: float, currency: str) -> ValidationResult:
-    \"\"\"Validate a payment request.
-    
-    Args:
-        amount: Payment amount
-        currency: ISO 4217 currency code
-    \"\"\"
-    if amount <= 0:
-        raise PaymentValidationError("Amount must be positive")
-    if currency not in SUPPORTED_CURRENCIES:
-        raise PaymentValidationError(f"Unsupported currency: {currency}")
-    return ValidationResult(valid=True, amount=amount, currency=currency)
+def validate_payment(amount: float, currency: str, region: str, compliance_level: str = 'standard') -> ValidationResult:
+    \"\"\"Validate a payment request with regional compliance.
+    
+    Args:
+        amount: Payment amount
+        currency: ISO 4217 currency code
+        region: Geographic region code (US, EU, APAC)
+        compliance_level: Compliance tier (standard, enhanced, strict)
+    \"\"\"
+    if amount <= 0:
+        raise PaymentValidationError("Amount must be positive")
+    if currency not in SUPPORTED_CURRENCIES:
+        raise PaymentValidationError(f"Unsupported currency: {currency}")
+    if region not in SUPPORTED_REGIONS:
+        raise PaymentValidationError(f"Unsupported region: {region}")
+    
+    compliance_check = _check_regional_compliance(amount, currency, region, compliance_level)
+    if not compliance_check.passed:
+        raise PaymentValidationError(f"Compliance check failed: {compliance_check.reason}")
+    
+    return ValidationResult(valid=True, amount=amount, currency=currency, region=region)
"""


async def run_analysis_pipeline(analysis_id: str) -> None:
    """Run the full analysis pipeline for a given analysis."""
    logger.info("analysis_service.start", analysis_id=analysis_id)

    async with async_session_factory() as session:
        try:
            from sqlalchemy import select

            result = await session.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            )
            analysis = result.scalar_one_or_none()

            if not analysis:
                logger.error("analysis_service.not_found", analysis_id=analysis_id)
                return

            analysis.status = "running"
            analysis.updated_at = datetime.now(timezone.utc)
            await session.commit()

            diff_content = DEMO_DIFF

            initial_state: CrosscutState = {
                "analysis_id": analysis_id,
                "mr_id": analysis.mr_id,
                "mr_iid": analysis.mr_iid,
                "project_id": analysis.project_id,
                "project_name": analysis.project_name,
                "mr_title": analysis.mr_title or "Payment Validation Enhancement",
                "mr_url": analysis.mr_url,
                "source_branch": analysis.source_branch or "feature/regional-compliance",
                "target_branch": analysis.target_branch,
                "diff_content": diff_content,
                "confidence_scores": {},
                "execution_log": [],
                "errors": [],
                "current_step": "starting",
            }

            logger.info("analysis_service.pipeline.start", analysis_id=analysis_id)
            final_state = await crosscut_graph.ainvoke(initial_state)
            logger.info("analysis_service.pipeline.complete", analysis_id=analysis_id)

            # Store results
            test_selection = final_state.get("test_selection", {})
            metrics = test_selection.get("metrics", {})
            pipeline = final_state.get("pipeline_report", {})
            comms = final_state.get("communications", {})
            dep_graph = final_state.get("dependency_graph", {})

            analysis.status = "completed"
            analysis.total_tests_available = metrics.get("total_tests_available", 0)
            analysis.selected_tests_count = metrics.get("selected_tests_count", 0)
            analysis.ci_minutes_saved = metrics.get("ci_minutes_saved", 0.0)
            analysis.percentage_reduction = metrics.get("percentage_reduction", 0.0)
            analysis.estimated_original_runtime = metrics.get("estimated_original_runtime", "")
            analysis.estimated_optimized_runtime = metrics.get("estimated_optimized_runtime", "")
            
            analysis.change_report = final_state.get("change_report")
            analysis.dependency_graph = {
                "nodes": [dict(n) for n in dep_graph.get("nodes", [])],
                "edges": [dict(e) for e in dep_graph.get("edges", [])],
            }
            analysis.pipeline_report = pipeline
            analysis.executive_summary = comms.get("executive_summary", "")
            analysis.execution_log = final_state.get("execution_log", [])
            analysis.mr_title = initial_state.get("mr_title", "")
            analysis.updated_at = datetime.now(timezone.utc)

            # Store impacted tests
            for test in test_selection.get("impacted_tests", []):
                impacted = ImpactedTest(
                    id=str(uuid.uuid4()),
                    analysis_id=analysis_id,
                    repository=test.get("repository", "unknown"),
                    file_path=test.get("file_path", ""),
                    test_name=test.get("test_name", "unknown"),
                    dependency_depth=test.get("dependency_depth", 1),
                    changed_symbol_name=test.get("changed_symbol_name"),
                    reasoning=test.get("reasoning", ""),
                )
                session.add(impacted)

            # Store pipeline execution
            if pipeline:
                execution = PipelineExecution(
                    id=str(uuid.uuid4()),
                    analysis_id=analysis_id,
                    pipeline_id=pipeline.get("pipeline_id", "unknown"),
                    status=pipeline.get("status", "unknown"),
                    tests_run=pipeline.get("tests_run", 0),
                    tests_passed=pipeline.get("tests_passed", 0),
                    tests_failed=pipeline.get("tests_failed", 0),
                    runtime_seconds=pipeline.get("runtime_seconds", 0),
                    log_url=pipeline.get("log_url"),
                )
                session.add(execution)

            await session.commit()

            logger.info(
                "analysis_service.complete",
                analysis_id=analysis_id,
                reduction=analysis.percentage_reduction,
            )

        except Exception as e:
            logger.error(
                "analysis_service.failed",
                analysis_id=analysis_id,
                error=str(e),
            )
            try:
                analysis.status = "failed"
                analysis.execution_log = (analysis.execution_log or []) + [f"Error: {str(e)}"]
                analysis.updated_at = datetime.now(timezone.utc)
                await session.commit()
            except Exception:
                pass
