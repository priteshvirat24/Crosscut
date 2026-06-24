"""Pytest fixtures shared across the Crosscut test suite."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_diff() -> str:
    """A small unified diff: a signature change plus a deletion."""
    return """diff --git a/src/payment/validator.py b/src/payment/validator.py
--- a/src/payment/validator.py
+++ b/src/payment/validator.py
@@ -15,6 +15,7 @@
-def process_order(amount: float, currency: str) -> ValidationResult:
+def process_order(amount: float, currency: str, region: str) -> ValidationResult:
     if amount <= 0:
         raise OrderValidationError("Amount must be positive")
@@ -30,4 +31,0 @@
-def fetch_order_status(payment_id: str) -> dict:
-    return _fetch_order_status(payment_id)
"""
