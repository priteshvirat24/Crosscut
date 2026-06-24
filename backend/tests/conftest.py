"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_diff() -> str:
    """Sample unified diff for testing."""
    return """diff --git a/src/payment/validator.py b/src/payment/validator.py
index 1a2b3c4..5d6e7f8 100644
--- a/src/payment/validator.py
+++ b/src/payment/validator.py
@@ -15,10 +15,15 @@
-def validatePayment(amount: float, currency: str) -> ValidationResult:
-    if amount <= 0:
-        raise PaymentValidationError("Amount must be positive")
-    return ValidationResult(valid=True, amount=amount, currency=currency)
+def validatePayment(amount: float, currency: str, region: str) -> ValidationResult:
+    if amount <= 0:
+        raise PaymentValidationError("Amount must be positive")
+    if region not in SUPPORTED_REGIONS:
+        raise PaymentValidationError(f"Unsupported region: {region}")
+    return ValidationResult(valid=True, amount=amount, currency=currency, region=region)
 
-def getPaymentStatus(payment_id: str) -> dict:
-    return _fetch_payment_status(payment_id)
+def calculateProcessingFee(amount: float, region: str) -> float:
+    return round(amount * REGIONAL_RATES.get(region, 0.029), 2)
"""


@pytest.fixture
def sample_change_report() -> dict:
    """Sample change report for testing downstream agents."""
    return {
        "total_changes": 3,
        "files_changed": ["src/payment/validator.py"],
        "changes": [
            {
                "change_type": "modified",
                "symbol_name": "validatePayment",
                "symbol_type": "function",
                "file_path": "src/payment/validator.py",
                "line_number": 15,
                "description": "Function 'validatePayment' signature changed",
                "before_signature": "def validatePayment(amount: float, currency: str) -> ValidationResult:",
                "after_signature": "def validatePayment(amount: float, currency: str, region: str) -> ValidationResult:",
                "parameters_changed": True,
                "return_type_changed": False,
            },
            {
                "change_type": "deleted",
                "symbol_name": "getPaymentStatus",
                "symbol_type": "function",
                "file_path": "src/payment/validator.py",
                "line_number": 20,
                "description": "Function 'getPaymentStatus' was deleted",
                "before_signature": "def getPaymentStatus(payment_id: str) -> dict:",
                "after_signature": "",
                "parameters_changed": False,
                "return_type_changed": False,
            },
            {
                "change_type": "added",
                "symbol_name": "calculateProcessingFee",
                "symbol_type": "function",
                "file_path": "src/payment/validator.py",
                "line_number": 25,
                "description": "New function 'calculateProcessingFee' added",
                "before_signature": "",
                "after_signature": "def calculateProcessingFee(amount: float, region: str) -> float:",
                "parameters_changed": False,
                "return_type_changed": False,
            },
        ],
        "summary": "Analyzed 1 diff hunk across 1 file. Found 3 symbol changes.",
    }


@pytest.fixture
def sample_breaking_assessment() -> dict:
    """Sample breaking change assessment."""
    return {
        "is_breaking": True,
        "total_breaking_changes": 2,
        "changes": [
            {
                "change_type": "modified",
                "symbol_name": "validatePayment",
                "file_path": "src/payment/validator.py",
                "severity": "high",
                "description": "New required parameter added",
                "confidence": 0.85,
                "reasoning": "Parameter 'region' added without default value",
                "line_number": 15,
                "before_signature": "def validatePayment(amount: float, currency: str)",
                "after_signature": "def validatePayment(amount: float, currency: str, region: str)",
                "rule_triggered": "parameter_added_required",
            },
            {
                "change_type": "deleted",
                "symbol_name": "getPaymentStatus",
                "file_path": "src/payment/validator.py",
                "severity": "critical",
                "description": "Function deleted — all callers will break",
                "confidence": 0.95,
                "reasoning": "Public function removed entirely",
                "line_number": 20,
                "before_signature": "def getPaymentStatus(payment_id: str) -> dict:",
                "after_signature": "",
                "rule_triggered": "deleted_public_function",
            },
        ],
        "overall_severity": "critical",
        "summary": "Found 2 breaking changes.",
    }
