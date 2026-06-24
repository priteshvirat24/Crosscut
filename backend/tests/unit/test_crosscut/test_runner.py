"""Tests for the real timing runner (uses trivial fast commands, but genuinely runs them)."""

from __future__ import annotations

import sys

from app.crosscut.models import (
    Mode,
    SelectedTest,
    SelectionMetrics,
    SelectionResult,
)
from app.crosscut.runner import measure


def _result(selected, total, full=False):
    return SelectionResult(
        selected=tuple(selected),
        metrics=SelectionMetrics(total_tests=total, selected_tests=len(selected)),
        mode=Mode.LOCAL,
        run_full_suite=full,
    )


def test_measure_returns_real_measured_timing(tmp_path):
    # Create two trivial "test" files the command will accept as args.
    (tmp_path / "a.py").write_text("")
    (tmp_path / "b.py").write_text("")
    r = _result([SelectedTest("t", "a.py", "reason")], total=10)
    cmd = f'"{sys.executable}" -c pass'
    timing = measure(r, test_command=cmd, cwd=str(tmp_path))
    assert timing.measured is True
    assert timing.full_suite_seconds >= 0.0
    assert timing.selected_seconds >= 0.0
    assert timing.seconds_saved >= 0.0


def test_measure_full_suite_runs_once(tmp_path):
    r = _result([SelectedTest("t", "a.py", "reason")], total=10, full=True)
    cmd = f'"{sys.executable}" -c pass'
    timing = measure(r, test_command=cmd, cwd=str(tmp_path))
    # full-suite mode -> selected == full (no separate subset run)
    assert timing.full_suite_seconds == timing.selected_seconds
