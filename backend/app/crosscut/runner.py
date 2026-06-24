"""Real test-suite timing — measures full suite vs selected subset by actually running them.

No estimates are invented. If measurement is not requested or the runner is unavailable,
the caller passes ``measured=False`` downstream and the comment omits timing entirely.
"""

from __future__ import annotations

import shlex
import subprocess
import time

from app.crosscut.models import SelectionResult, TimingResult


def measure(
    result: SelectionResult,
    *,
    test_command: str = "pytest",
    cwd: str | None = None,
    timeout: int = 1800,
) -> TimingResult:
    """Run the full suite, then only the selected files, returning real wall-clock times."""
    full = _time_run(test_command, cwd, timeout)

    files = result.selected_files
    if result.run_full_suite or not files:
        # Selected == full (or nothing selected); a second run is not meaningful.
        return TimingResult(full_suite_seconds=full, selected_seconds=full, measured=True)

    sel_cmd = f"{test_command} {' '.join(shlex.quote(f) for f in files)}"
    selected = _time_run(sel_cmd, cwd, timeout)
    return TimingResult(full_suite_seconds=full, selected_seconds=selected, measured=True)


def _time_run(command: str, cwd: str | None, timeout: int) -> float:
    start = time.perf_counter()
    subprocess.run(
        shlex.split(command),
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return round(time.perf_counter() - start, 3)
