"""Tests for child-pipeline generation and MR comment rendering."""

from __future__ import annotations

import yaml

from app.crosscut.comment import FULL_SUITE_COMMAND, FULL_SUITE_LABEL, render_comment
from app.crosscut.models import (
    Mode,
    SelectedTest,
    SelectionMetrics,
    SelectionResult,
    TimingResult,
)
from app.crosscut.pipeline import generate_pipeline, selected_files, to_yaml


def _result(selected, total, full=False, notes=()):
    return SelectionResult(
        selected=tuple(selected),
        metrics=SelectionMetrics(total_tests=total, selected_tests=len(selected)),
        mode=Mode.LOCAL,
        run_full_suite=full,
        notes=tuple(notes),
    )


def _t(file_path, name, reason="calls changed fn"):
    return SelectedTest(name=name, file_path=file_path, reason=reason, depth=1)


# ── pipeline ────────────────────────────────────────────────────────────────────


def test_pipeline_targeted_runs_only_selected_files():
    r = _result([_t("tests/test_a.py", "test_1"), _t("tests/test_b.py", "test_2")], 10)
    p = generate_pipeline(r)
    assert "crosscut:targeted" in p
    script = " ".join(p["crosscut:targeted"]["script"])
    assert "tests/test_a.py" in script
    assert "tests/test_b.py" in script


def test_pipeline_is_valid_yaml():
    r = _result([_t("tests/test_a.py", "test_1")], 10)
    text = to_yaml(generate_pipeline(r))
    parsed = yaml.safe_load(text)
    assert "stages" in parsed
    assert parsed["stages"] == ["test"]


def test_pipeline_injects_image_and_before_script():
    r = _result([_t("tests/test_a.py", "test_1")], 10)
    p = generate_pipeline(
        r, image="python:3.12-slim", before_script=["pip install -e .[dev]"]
    )
    job = p["crosscut:targeted"]
    assert job["image"] == "python:3.12-slim"
    assert job["before_script"] == ["pip install -e .[dev]"]


def test_pipeline_omits_image_when_not_set():
    r = _result([_t("tests/test_a.py", "test_1")], 10)
    job = generate_pipeline(r)["crosscut:targeted"]
    assert "image" not in job
    assert "before_script" not in job


def test_pipeline_full_suite():
    r = _result([_t("tests/test_a.py", "test_1")], 10, full=True)
    p = generate_pipeline(r)
    assert "crosscut:full-suite" in p
    assert "pytest" in " ".join(p["crosscut:full-suite"]["script"])


def test_pipeline_zero_selected_is_explicit_not_silent():
    r = _result([], 10)
    p = generate_pipeline(r)
    assert "crosscut:no-impacted-tests" in p
    script = " ".join(p["crosscut:no-impacted-tests"]["script"])
    assert "no code-impacting changes" in script


def test_pipeline_no_hardcoded_reduction_numbers():
    r = _result([_t("tests/test_a.py", "test_1")], 10)
    text = to_yaml(generate_pipeline(r))
    for forbidden in ("418", "406", "TESTS_REDUCED", "36 min"):
        assert forbidden not in text


def test_pipeline_respects_custom_test_command():
    r = _result([_t("spec/foo_spec.rb", "x")], 5)
    p = generate_pipeline(r, test_command="bundle exec rspec")
    assert "bundle exec rspec" in " ".join(p["crosscut:targeted"]["script"])


def test_selected_files_dedup():
    r = _result(
        [_t("tests/test_a.py", "t1"), _t("tests/test_a.py", "t2"), _t("tests/test_b.py", "t3")],
        10,
    )
    assert selected_files(r) == ["tests/test_a.py", "tests/test_b.py"]


def test_pipeline_quotes_paths_with_spaces():
    r = _result([_t("tests/weird path.py", "t1")], 5)
    script = " ".join(generate_pipeline(r)["crosscut:targeted"]["script"])
    assert "'tests/weird path.py'" in script


# ── comment ──────────────────────────────────────────────────────────────────────


def test_comment_leads_with_headline_number():
    r = _result([_t("tests/test_a.py", "test_1")], 10)
    text = render_comment(r)
    assert "Running 1 of 10 tests" in text
    assert "90% fewer" in text


def test_comment_includes_measured_timing_when_present():
    r = _result([_t("tests/test_a.py", "test_1")], 10)
    timing = TimingResult(full_suite_seconds=120.0, selected_seconds=12.0, measured=True)
    text = render_comment(r, timing=timing)
    assert "saved" in text
    assert "2m00s" in text  # 120s formatted


def test_comment_omits_timing_when_not_measured():
    r = _result([_t("tests/test_a.py", "test_1")], 10)
    timing = TimingResult(full_suite_seconds=0.0, selected_seconds=0.0, measured=False)
    text = render_comment(r, timing=timing)
    assert "saved" not in text


def test_comment_has_escape_hatch():
    r = _result([_t("tests/test_a.py", "test_1")], 10)
    text = render_comment(r)
    assert FULL_SUITE_LABEL in text
    assert FULL_SUITE_COMMAND in text


def test_comment_shows_per_test_rationale():
    r = _result([_t("tests/test_a.py", "test_1", reason="calls changed validate")], 10)
    text = render_comment(r)
    assert "Why these tests?" in text
    assert "calls changed validate" in text


def test_comment_states_mode():
    r = SelectionResult(
        selected=(_t("tests/test_a.py", "t"),),
        metrics=SelectionMetrics(total_tests=5, selected_tests=1),
        mode=Mode.REMOTE,
        run_full_suite=False,
    )
    assert "Remote" in render_comment(r)
    local = _result([_t("tests/test_a.py", "t")], 5)
    assert "Local" in render_comment(local)


def test_comment_full_suite_message():
    r = _result([_t("tests/test_a.py", "t")], 10, full=True, notes=["unknown blast radius"])
    text = render_comment(r)
    assert "full suite" in text.lower()
    assert "unknown blast radius" in text


def test_comment_no_llm_claim_present():
    r = _result([_t("tests/test_a.py", "t")], 10)
    assert "no LLM" in render_comment(r)
