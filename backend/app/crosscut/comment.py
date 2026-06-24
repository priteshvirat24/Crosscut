"""MR comment rendering — deterministic markdown, no LLM.

The comment is the UX. It leads with one number anyone understands, then the per-test
rationale, then a one-click full-suite escape hatch. Every number is passed in from a real
measurement or the real selection — nothing is invented here.
"""

from __future__ import annotations

from app.crosscut.models import Mode, SelectionResult, TimingResult

MAX_LISTED = 15
FULL_SUITE_LABEL = "crosscut:full"
FULL_SUITE_COMMAND = "/crosscut full"


def render_comment(
    result: SelectionResult,
    *,
    timing: TimingResult | None = None,
    changed_symbols: list[str] | None = None,
) -> str:
    m = result.metrics
    mode_label = (
        "Orbit Remote (cross-repo)"
        if result.mode is Mode.REMOTE
        else "Orbit Local (single-repo)"
    )

    lines: list[str] = []
    lines.append("## ✂️ Crosscut — targeted test selection")
    lines.append("")

    # ── headline number ──────────────────────────────────────────────────────────
    if result.run_full_suite:
        lines.append(
            f"**Running the full suite ({m.total_tests} tests)** — conservative fallback."
        )
    else:
        headline = (
            f"**Running {m.selected_tests} of {m.total_tests} tests "
            f"({m.percentage_reduction:.0f}% fewer).**"
        )
        if timing and timing.measured:
            headline += (
                f"  Measured: {_fmt(timing.full_suite_seconds)} → "
                f"{_fmt(timing.selected_seconds)} "
                f"(**{_fmt(timing.seconds_saved)} saved**)."
            )
        lines.append(headline)
    lines.append("")

    if changed_symbols:
        shown = ", ".join(f"`{s}`" for s in changed_symbols[:10])
        more = "" if len(changed_symbols) <= 10 else f" (+{len(changed_symbols) - 10} more)"
        lines.append(f"**Changed symbols:** {shown}{more}")
        lines.append("")

    # ── per-test rationale ───────────────────────────────────────────────────────
    if not result.run_full_suite and result.selected:
        lines.append("<details><summary>Why these tests?</summary>")
        lines.append("")
        lines.append("| Test | Reason |")
        lines.append("|------|--------|")
        for t in result.selected[:MAX_LISTED]:
            label = (
                f"`{t.file_path}::{t.name}`"
                if t.name != "*"
                else f"`{t.file_path}` (whole file)"
            )
            lines.append(f"| {label} | {t.reason} |")
        if len(result.selected) > MAX_LISTED:
            lines.append(f"| … | +{len(result.selected) - MAX_LISTED} more selected |")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    # ── notes (e.g. fallback reasons) ────────────────────────────────────────────
    for note in result.notes:
        lines.append(f"> ℹ️ {note}")
    if result.notes:
        lines.append("")

    # ── escape hatch ─────────────────────────────────────────────────────────────
    lines.append("---")
    lines.append(
        f"Not confident in the selection? Add the **`{FULL_SUITE_LABEL}`** label "
        f"or comment **`{FULL_SUITE_COMMAND}`** to run the entire suite."
    )
    lines.append("")
    lines.append(
        f"<sub>Selection computed from {mode_label}'s call graph. "
        f"Deterministic graph traversal — no LLM in the selection path.</sub>"
    )

    return "\n".join(lines)


def _fmt(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    rem = int(seconds % 60)
    return f"{minutes}m{rem:02d}s"
