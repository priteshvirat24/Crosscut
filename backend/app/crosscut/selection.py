"""The selection core — pure, deterministic, no I/O, no LLM.

Input:  changed symbols (from the diff) + a resolved Orbit CodeGraph + the repo test
        inventory.
Output: the selected tests, each with a one-line rationale, plus a metrics object.

This is the testable heart of Crosscut. It is *conservative by construction*: it never
silently drops a test that could be affected. The rules are:

  1. Any test that transitively reaches a changed symbol (via the reverse call/extends
     graph) is selected.
  2. A changed test file, a new test file, or any test file Orbit could not map is
     always selected.
  3. A deleted symbol still exists in the pre-change graph Orbit indexed, so its prior
     callers — and their tests — are reached by rule 1.
  4. A changed symbol with no callers selects its own file's conventional tests; if that
     yields nothing, Crosscut falls back to the full suite rather than an empty set.
  5. A changed *source* symbol that Orbit could not map (unknown blast radius) falls
     back to the full suite.

Determinism: results are sorted; sets are only used internally for traversal.
"""

from __future__ import annotations

from collections import deque

from app.crosscut import conventions
from app.crosscut.models import (
    ChangedSymbol,
    ChangeType,
    CodeGraph,
    Mode,
    SelectedTest,
    SelectionMetrics,
    SelectionResult,
    TestCase,
    TestInventory,
)

# Safety cap on reverse-traversal depth. Deep call chains still get selected; this only
# bounds pathological graphs. Tests that reach a change within this many hops are kept.
DEFAULT_MAX_DEPTH = 50


def select_tests(
    changed_symbols: list[ChangedSymbol],
    graph: CodeGraph,
    inventory: TestInventory,
    *,
    mode: Mode = Mode.LOCAL,
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> SelectionResult:
    """Compute the minimal conservative set of tests for the given change."""
    notes: list[str] = []
    total = inventory.total

    # No changes at all -> nothing to test. (The pipeline layer decides smoke vs none.)
    if not changed_symbols:
        return SelectionResult(
            selected=(),
            metrics=SelectionMetrics(total_tests=total, selected_tests=0),
            mode=mode,
            run_full_suite=False,
            notes=("No code changes detected.",),
        )

    # Index the inventory for fast lookup.
    tests_by_defid: dict[int, TestCase] = {
        t.definition_id: t for t in inventory.tests if t.definition_id is not None
    }
    tests_by_file: dict[str, list[TestCase]] = {}
    for t in inventory.tests:
        tests_by_file.setdefault(t.file_path, []).append(t)

    # selected[(file, name)] -> SelectedTest, keeping the shallowest (most direct) reason.
    selected: dict[tuple[str, str], SelectedTest] = {}

    def _add(test: SelectedTest) -> None:
        key = (test.file_path, test.name)
        existing = selected.get(key)
        if existing is None or test.depth < existing.depth:
            selected[key] = test

    run_full_suite = False

    # ── Rule 2: changed / new / unmapped test files are always included ──────────────
    for sym in changed_symbols:
        if conventions.is_test_file(sym.file_path):
            file_tests = tests_by_file.get(sym.file_path)
            if file_tests:
                for tc in file_tests:
                    _add(
                        SelectedTest(
                            name=tc.name,
                            file_path=tc.file_path,
                            reason=f"Test file changed ({sym.file_path})",
                            changed_symbol=sym.name,
                            depth=0,
                        )
                    )
            else:
                # New or not-yet-mapped test file: select the whole file conservatively.
                _add(
                    SelectedTest(
                        name="*",
                        file_path=sym.file_path,
                        reason=f"New/changed test file ({sym.change_type.value})",
                        changed_symbol=sym.name,
                        depth=0,
                    )
                )

    for path in sorted(inventory.unmapped_test_files):
        _add(
            SelectedTest(
                name="*",
                file_path=path,
                reason="Test file present but Orbit could not map it; included for safety",
                changed_symbol=None,
                depth=0,
            )
        )

    # ── Resolve changed source symbols to graph definitions ─────────────────────────
    source_symbols = [s for s in changed_symbols if not conventions.is_test_file(s.file_path)]
    seed_ids: dict[int, ChangedSymbol] = {}  # def id -> the change that seeded it
    unmapped_sources: list[ChangedSymbol] = []

    for sym in source_symbols:
        if sym.change_type == ChangeType.ADDED:
            # A purely-added symbol has no prior callers; covered by own-file fallback below.
            matches = graph.find(sym.file_path, sym.name)
        else:
            matches = graph.find(sym.file_path, sym.name)
            if not matches:
                # Could not resolve a modified/deleted symbol -> unknown blast radius.
                unmapped_sources.append(sym)
        for d in matches:
            seed_ids.setdefault(d.id, sym)

    if unmapped_sources:
        run_full_suite = True
        names = ", ".join(sorted({s.name for s in unmapped_sources}))
        notes.append(
            f"Changed symbol(s) not found in Orbit graph ({names}); running full suite "
            f"(unknown blast radius)."
        )

    # Track which changed source symbols contributed at least one test. Any mapped
    # symbol that ends up with zero covering tests triggers the full-suite fallback —
    # Crosscut never leaves a changed symbol silently untested.
    covered: set[ChangedSymbol] = set()

    # ── Rule 1 + 3: reverse BFS over callers, collect tests that reach a change ──────
    if seed_ids:
        depth_of, origin_of = _reverse_reach(graph, seed_ids, max_depth)
        for def_id, depth in depth_of.items():
            test_case = tests_by_defid.get(def_id)
            if test_case is None:
                continue
            origin = origin_of[def_id]
            verb = "calls" if depth == 1 else f"transitively reaches (depth {depth})"
            reason = f"{verb} changed {origin.symbol_type} '{origin.name}' in {origin.file_path}"
            _add(
                SelectedTest(
                    name=test_case.name,
                    file_path=test_case.file_path,
                    reason=reason,
                    changed_symbol=origin.name,
                    depth=depth,
                )
            )
            covered.add(origin)

    # ── Rule 4: changed source symbol with no callers -> its own file's tests ───────
    for sym in source_symbols:
        if sym in unmapped_sources or sym in covered:
            continue
        # Include conventionally-matching tests (e.g. payment.py -> test_payment.py).
        own_file_tests = [
            t
            for t in inventory.tests
            if conventions.test_file_matches_source(t.file_path, sym.file_path)
        ]
        for tc in own_file_tests:
            _add(
                SelectedTest(
                    name=tc.name,
                    file_path=tc.file_path,
                    reason=f"Covers source file of changed '{sym.name}'",
                    changed_symbol=sym.name,
                    depth=1,
                )
            )
        if own_file_tests:
            covered.add(sym)

    # ── Rule 4 fallback: any mapped source symbol left uncovered -> full suite ───────
    uncovered = [s for s in source_symbols if s not in unmapped_sources and s not in covered]
    if uncovered:
        run_full_suite = True
        names = ", ".join(sorted({s.name for s in uncovered}))
        notes.append(
            f"No covering tests found for changed symbol(s): {names}; running full suite "
            f"rather than skipping silently."
        )

    if run_full_suite:
        selected_all = _select_everything(inventory)
        return SelectionResult(
            selected=selected_all,
            metrics=SelectionMetrics(total_tests=total, selected_tests=len(selected_all)),
            mode=mode,
            run_full_suite=True,
            notes=tuple(notes),
        )

    ordered = tuple(
        sorted(selected.values(), key=lambda t: (t.depth, t.file_path, t.name))
    )
    return SelectionResult(
        selected=ordered,
        metrics=SelectionMetrics(total_tests=total, selected_tests=len(ordered)),
        mode=mode,
        run_full_suite=False,
        notes=tuple(notes),
    )


def _reverse_reach(
    graph: CodeGraph,
    seed_ids: dict[int, ChangedSymbol],
    max_depth: int,
) -> tuple[dict[int, int], dict[int, ChangedSymbol]]:
    """BFS up the caller edges from the seed definitions.

    Returns (depth_of, origin_of): for every definition reachable as a (transitive)
    caller of a seed, its shortest hop distance and the originating changed symbol.
    Seeds themselves are recorded at depth 0.
    """
    depth_of: dict[int, int] = {}
    origin_of: dict[int, ChangedSymbol] = {}
    queue: deque[tuple[int, int]] = deque()

    for sid, sym in seed_ids.items():
        depth_of[sid] = 0
        origin_of[sid] = sym
        queue.append((sid, 0))

    while queue:
        node, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for caller in graph.callers_of(node):
            new_depth = depth + 1
            if caller not in depth_of or new_depth < depth_of[caller]:
                depth_of[caller] = new_depth
                origin_of[caller] = origin_of[node]
                queue.append((caller, new_depth))

    return depth_of, origin_of


def _select_everything(inventory: TestInventory) -> tuple[SelectedTest, ...]:
    """Materialize the full suite as selected tests (escape-hatch / safe fallback)."""
    out: list[SelectedTest] = [
        SelectedTest(
            name=tc.name,
            file_path=tc.file_path,
            reason="Full suite (conservative fallback)",
            changed_symbol=None,
            depth=0,
        )
        for tc in inventory.tests
    ]
    out.extend(
        SelectedTest(
            name="*",
            file_path=path,
            reason="Full suite (conservative fallback)",
            changed_symbol=None,
            depth=0,
        )
        for path in sorted(inventory.unmapped_test_files)
    )
    return tuple(sorted(out, key=lambda t: (t.file_path, t.name)))
