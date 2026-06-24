"""Targeted child-pipeline generation.

Turns a :class:`SelectionResult` into a valid GitLab CI child pipeline that runs only
the selected tests' files. No hardcoded reductions — the jobs are derived entirely from
the selection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from app.crosscut.models import SelectionResult


def selected_files(result: SelectionResult) -> list[str]:
    """Distinct files to run, preserving deterministic order."""
    return result.selected_files


def generate_pipeline(
    result: SelectionResult,
    *,
    test_command: str = "pytest",
    image: str | None = None,
    before_script: list[str] | None = None,
) -> dict:
    """Build the child-pipeline definition as a plain dict (serialize with :func:`to_yaml`).

    Policy:
      * full suite      -> a single job running the whole suite.
      * selected files  -> a single job running exactly those files.
      * nothing to run  -> an explicit, visible no-op job (never a silent skip).

    ``image`` and ``before_script`` make the child pipeline self-contained when the parent
    needs the test environment set up (deps installed, etc.).
    """
    if result.run_full_suite:
        script = [
            'echo "Crosscut: running full suite (conservative fallback)"',
            test_command,
        ]
        return _wrap("crosscut:full-suite", script, image, before_script)

    files = selected_files(result)
    if not files:
        # No impacted tests and no fallback -> explicit pass job, not a silent skip.
        script = [
            'echo "Crosscut: no code-impacting changes detected; no tests to run."',
            "true",
        ]
        return _wrap("crosscut:no-impacted-tests", script, image, before_script)

    n_tests = result.metrics.selected_tests
    quoted = " ".join(_shell_quote(f) for f in files)
    script = [
        f'echo "Crosscut: running {n_tests} selected test(s) across {len(files)} file(s)"',
        f"{test_command} {quoted}",
    ]
    return _wrap("crosscut:targeted", script, image, before_script)


def to_yaml(pipeline: dict) -> str:
    return yaml.safe_dump(pipeline, sort_keys=False, default_flow_style=False)


# ── internals ─────────────────────────────────────────────────────────────────────


def _wrap(
    job_name: str,
    script: list[str],
    image: str | None = None,
    before_script: list[str] | None = None,
) -> dict:
    job: dict = {"stage": "test", "script": script}
    if image:
        job["image"] = image
    if before_script:
        job["before_script"] = before_script
    return {"stages": ["test"], job_name: job}


def _shell_quote(path: str) -> str:
    if all(ch.isalnum() or ch in "._/-" for ch in path):
        return path
    return "'" + path.replace("'", "'\\''") + "'"
