"""Unit tests for Agent 1: Diff Intelligence."""

from __future__ import annotations

import pytest
from app.agents.diff_intelligence import (
    parse_diff_hunks,
    extract_function_changes,
    diff_intelligence_agent,
)


class TestParseDiffHunks:
    """Test diff parsing utilities."""

    def test_parses_basic_diff(self, sample_diff: str):
        hunks = parse_diff_hunks(sample_diff)
        assert len(hunks) > 0
        assert hunks[0]["file"] == "src/payment/validator.py"

    def test_identifies_added_lines(self, sample_diff: str):
        hunks = parse_diff_hunks(sample_diff)
        added = hunks[0]["added_lines"]
        assert any("validatePayment" in line for line in added)

    def test_identifies_removed_lines(self, sample_diff: str):
        hunks = parse_diff_hunks(sample_diff)
        removed = hunks[0]["removed_lines"]
        assert any("getPaymentStatus" in line for line in removed)

    def test_handles_empty_diff(self):
        hunks = parse_diff_hunks("")
        assert hunks == []


class TestExtractFunctionChanges:
    """Test function change extraction."""

    def test_extracts_deleted_function(self, sample_diff: str):
        hunks = parse_diff_hunks(sample_diff)
        changes = extract_function_changes(hunks)
        deleted = [c for c in changes if c["change_type"] == "deleted"]
        assert len(deleted) >= 1
        assert any(c["symbol_name"] == "getPaymentStatus" for c in deleted)

    def test_extracts_modified_function(self, sample_diff: str):
        hunks = parse_diff_hunks(sample_diff)
        changes = extract_function_changes(hunks)
        modified = [c for c in changes if c["change_type"] == "modified"]
        # validatePayment signature changed
        assert any(c["symbol_name"] == "validatePayment" for c in modified)

    def test_extracts_added_function(self, sample_diff: str):
        hunks = parse_diff_hunks(sample_diff)
        changes = extract_function_changes(hunks)
        added = [c for c in changes if c["change_type"] == "added"]
        assert any(c["symbol_name"] == "calculateProcessingFee" for c in added)


class TestDiffIntelligenceAgent:
    """Test the full agent node."""

    @pytest.mark.asyncio
    async def test_produces_change_report(self, sample_diff: str):
        state = {
            "analysis_id": "test-1",
            "diff_content": sample_diff,
            "execution_log": [],
        }
        result = await diff_intelligence_agent(state)
        assert "change_report" in result
        report = result["change_report"]
        assert report["total_changes"] > 0
        assert len(report["files_changed"]) > 0

    @pytest.mark.asyncio
    async def test_handles_empty_diff(self):
        state = {
            "analysis_id": "test-2",
            "diff_content": "",
            "execution_log": [],
        }
        result = await diff_intelligence_agent(state)
        assert result["change_report"]["total_changes"] == 0

    @pytest.mark.asyncio
    async def test_updates_execution_log(self, sample_diff: str):
        state = {
            "analysis_id": "test-3",
            "diff_content": sample_diff,
            "execution_log": [],
        }
        result = await diff_intelligence_agent(state)
        assert len(result["execution_log"]) > 0
