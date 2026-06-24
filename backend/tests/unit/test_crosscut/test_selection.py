"""Tests for the deterministic selection core on synthetic graphs.

Each test builds a small CodeGraph by hand so the traversal and conservativeness rules
are exercised in isolation — no Orbit, no I/O.
"""

from __future__ import annotations

import pytest

from app.crosscut.models import (
    ChangedSymbol,
    ChangeType,
    CodeGraph,
    Definition,
    Mode,
    TestCase,
    TestInventory,
)
from app.crosscut.selection import select_tests

# ── builders ────────────────────────────────────────────────────────────────────


def _def(id_: int, name: str, path: str, dtype: str = "Function") -> Definition:
    return Definition(id=id_, name=name, file_path=path, definition_type=dtype)


def _graph(defs: list[Definition], call_edges: list[tuple[int, int]]) -> CodeGraph:
    """call_edges as (caller_id, callee_id); stored as reverse adjacency callers[callee]."""
    callers: dict[int, set[int]] = {}
    for caller, callee in call_edges:
        callers.setdefault(callee, set()).add(caller)
    return CodeGraph(definitions={d.id: d for d in defs}, callers=callers)


def _changed(name: str, path: str, ctype: ChangeType = ChangeType.MODIFIED) -> ChangedSymbol:
    return ChangedSymbol(name=name, file_path=path, change_type=ctype)


def _names(result) -> set[str]:
    return {t.name for t in result.selected}


# ── fixtures: a small realistic graph ─────────────────────────────────────────────


@pytest.fixture
def basic_inventory_and_graph():
    # source: src/payment.py::validate ; src/checkout.py::checkout calls validate
    validate = _def(1, "validate", "src/payment.py")
    checkout = _def(2, "checkout", "src/checkout.py")
    # tests
    t_payment = _def(10, "test_validate", "tests/test_payment.py", "Function")
    t_checkout = _def(11, "test_checkout", "tests/test_checkout.py", "Function")
    t_unrelated = _def(12, "test_unrelated", "tests/test_other.py", "Function")

    defs = [validate, checkout, t_payment, t_checkout, t_unrelated]
    # edges (caller -> callee):
    #   checkout calls validate
    #   test_validate calls validate
    #   test_checkout calls checkout
    #   test_unrelated calls nothing relevant
    edges = [(2, 1), (10, 1), (11, 2)]
    graph = _graph(defs, edges)
    inv = TestInventory(
        tests=(
            TestCase("test_validate", "tests/test_payment.py", 10),
            TestCase("test_checkout", "tests/test_checkout.py", 11),
            TestCase("test_unrelated", "tests/test_other.py", 12),
        )
    )
    return graph, inv


# ── Rule 1: transitive reach ──────────────────────────────────────────────────────


def test_direct_caller_test_selected(basic_inventory_and_graph):
    graph, inv = basic_inventory_and_graph
    r = select_tests([_changed("validate", "src/payment.py")], graph, inv)
    assert "test_validate" in _names(r)


def test_transitive_caller_two_hops(basic_inventory_and_graph):
    graph, inv = basic_inventory_and_graph
    # test_checkout -> checkout -> validate : 2 hops from validate
    r = select_tests([_changed("validate", "src/payment.py")], graph, inv)
    assert "test_checkout" in _names(r)


def test_unrelated_test_not_selected(basic_inventory_and_graph):
    graph, inv = basic_inventory_and_graph
    r = select_tests([_changed("validate", "src/payment.py")], graph, inv)
    assert "test_unrelated" not in _names(r)
    assert not r.run_full_suite


def test_depth_recorded_increases_with_distance(basic_inventory_and_graph):
    graph, inv = basic_inventory_and_graph
    r = select_tests([_changed("validate", "src/payment.py")], graph, inv)
    by_name = {t.name: t for t in r.selected}
    assert by_name["test_validate"].depth == 1
    assert by_name["test_checkout"].depth == 2


def test_reason_names_changed_symbol(basic_inventory_and_graph):
    graph, inv = basic_inventory_and_graph
    r = select_tests([_changed("validate", "src/payment.py")], graph, inv)
    reason = {t.name: t.reason for t in r.selected}["test_validate"]
    assert "validate" in reason and "src/payment.py" in reason


def test_n_hop_chain():
    # a <- b <- c <- d <- test  (test reaches a at depth 4)
    defs = [
        _def(1, "a", "src/a.py"),
        _def(2, "b", "src/b.py"),
        _def(3, "c", "src/c.py"),
        _def(4, "d", "src/d.py"),
        _def(5, "test_chain", "tests/test_chain.py"),
    ]
    edges = [(2, 1), (3, 2), (4, 3), (5, 4)]
    graph = _graph(defs, edges)
    inv = TestInventory(tests=(TestCase("test_chain", "tests/test_chain.py", 5),))
    r = select_tests([_changed("a", "src/a.py")], graph, inv)
    assert "test_chain" in _names(r)
    assert {t.name: t.depth for t in r.selected}["test_chain"] == 4


def test_cycle_terminates():
    # mutual recursion a<->b, test calls a
    defs = [
        _def(1, "a", "src/a.py"),
        _def(2, "b", "src/b.py"),
        _def(3, "test_a", "tests/test_a.py"),
    ]
    edges = [(1, 2), (2, 1), (3, 1)]  # a calls b, b calls a, test calls a
    graph = _graph(defs, edges)
    inv = TestInventory(tests=(TestCase("test_a", "tests/test_a.py", 3),))
    r = select_tests([_changed("a", "src/a.py")], graph, inv)
    assert "test_a" in _names(r)  # and did not hang


def test_depth_limit_excludes_far_tests():
    # test_near is 1 hop from a; test_far is 3 hops. With max_depth=2, far is excluded
    # while near keeps the selection non-empty (so the full-suite fallback does not fire).
    defs = [
        _def(1, "a", "src/a.py"),
        _def(2, "b", "src/b.py"),
        _def(3, "c", "src/c.py"),
        _def(4, "test_far", "tests/test_far.py"),
        _def(5, "test_near", "tests/test_near.py"),
    ]
    edges = [(2, 1), (3, 2), (4, 3), (5, 1)]  # far=3 hops, near=1 hop
    graph = _graph(defs, edges)
    inv = TestInventory(
        tests=(
            TestCase("test_far", "tests/test_far.py", 4),
            TestCase("test_near", "tests/test_near.py", 5),
        )
    )
    r = select_tests([_changed("a", "src/a.py")], graph, inv, max_depth=2)
    assert "test_near" in _names(r)
    assert "test_far" not in _names(r)
    assert not r.run_full_suite


# ── Rule 2: test-file changes ─────────────────────────────────────────────────────


def test_changed_test_file_included(basic_inventory_and_graph):
    graph, inv = basic_inventory_and_graph
    r = select_tests([_changed("test_checkout", "tests/test_checkout.py")], graph, inv)
    assert "test_checkout" in _names(r)
    assert {t.name: t.depth for t in r.selected}["test_checkout"] == 0


def test_new_test_file_included():
    graph = _graph([], [])
    inv = TestInventory(tests=())  # not yet mapped
    r = select_tests(
        [_changed("test_brand_new", "tests/test_brand_new.py", ChangeType.ADDED)],
        graph,
        inv,
    )
    assert any(t.file_path == "tests/test_brand_new.py" for t in r.selected)


def test_unmapped_test_file_always_included():
    graph = _graph([], [])
    inv = TestInventory(
        tests=(TestCase("test_known", "tests/test_known.py", None),),
        unmapped_test_files=frozenset({"tests/legacy_spec.rb"}),
    )
    r = select_tests([_changed("foo", "src/foo.py", ChangeType.ADDED)], graph, inv)
    assert any(t.file_path == "tests/legacy_spec.rb" for t in r.selected)


# ── Rule 3: deletion ──────────────────────────────────────────────────────────────


def test_deleted_symbol_selects_prior_callers_tests(basic_inventory_and_graph):
    graph, inv = basic_inventory_and_graph
    # delete validate: prior callers (checkout) and their tests must run
    r = select_tests(
        [_changed("validate", "src/payment.py", ChangeType.DELETED)], graph, inv
    )
    assert "test_validate" in _names(r)
    assert "test_checkout" in _names(r)


# ── Rule 4: no callers ────────────────────────────────────────────────────────────


def test_symbol_no_callers_runs_own_file_tests():
    # leaf source symbol with a conventional test file, no callers
    defs = [
        _def(1, "helper", "src/helper.py"),
        _def(2, "test_helper", "tests/test_helper.py"),
    ]
    graph = _graph(defs, [])  # no callers of helper
    inv = TestInventory(tests=(TestCase("test_helper", "tests/test_helper.py", 2),))
    r = select_tests([_changed("helper", "src/helper.py")], graph, inv)
    assert "test_helper" in _names(r)
    assert not r.run_full_suite


def test_symbol_no_callers_no_matching_test_runs_full_suite():
    defs = [_def(1, "orphan", "src/orphan.py")]
    graph = _graph(defs, [])
    inv = TestInventory(tests=(TestCase("test_other", "tests/test_other.py", 99),))
    r = select_tests([_changed("orphan", "src/orphan.py")], graph, inv)
    assert r.run_full_suite
    assert "test_other" in _names(r)  # full suite materialized, never silently empty


def test_unmapped_changed_source_runs_full_suite(basic_inventory_and_graph):
    graph, inv = basic_inventory_and_graph
    # a modified symbol Orbit never indexed -> unknown blast radius -> full suite
    r = select_tests([_changed("ghost", "src/ghost.py")], graph, inv)
    assert r.run_full_suite
    assert any("blast radius" in n for n in r.notes)


# ── empty / metrics / determinism ─────────────────────────────────────────────────


def test_no_changes_selects_nothing(basic_inventory_and_graph):
    graph, inv = basic_inventory_and_graph
    r = select_tests([], graph, inv)
    assert r.selected == ()
    assert not r.run_full_suite
    assert r.metrics.selected_tests == 0


def test_metrics_counts_and_percentage(basic_inventory_and_graph):
    graph, inv = basic_inventory_and_graph
    r = select_tests([_changed("validate", "src/payment.py")], graph, inv)
    assert r.metrics.total_tests == 3
    assert r.metrics.selected_tests == 2
    assert r.metrics.percentage_reduction == pytest.approx(33.3, abs=0.1)


def test_metrics_percentage_zero_when_no_tests():
    graph = _graph([_def(1, "a", "src/a.py")], [])
    inv = TestInventory(tests=())
    r = select_tests([_changed("a", "src/a.py", ChangeType.ADDED)], graph, inv)
    # no tests at all -> full suite fallback, percentage 0, never a divide-by-zero
    assert r.metrics.percentage_reduction == 0.0


def test_results_are_sorted_deterministically():
    defs = [
        _def(1, "core", "src/core.py"),
        _def(10, "test_b", "tests/test_b.py"),
        _def(11, "test_a", "tests/test_a.py"),
    ]
    edges = [(10, 1), (11, 1)]
    graph = _graph(defs, edges)
    inv = TestInventory(
        tests=(
            TestCase("test_b", "tests/test_b.py", 10),
            TestCase("test_a", "tests/test_a.py", 11),
        )
    )
    r1 = select_tests([_changed("core", "src/core.py")], graph, inv)
    r2 = select_tests([_changed("core", "src/core.py")], graph, inv)
    assert [t.name for t in r1.selected] == [t.name for t in r2.selected]
    # same depth -> sorted by file path then name
    assert [t.name for t in r1.selected] == ["test_a", "test_b"]


def test_mode_is_passed_through(basic_inventory_and_graph):
    graph, inv = basic_inventory_and_graph
    r = select_tests(
        [_changed("validate", "src/payment.py")], graph, inv, mode=Mode.REMOTE
    )
    assert r.mode == Mode.REMOTE


def test_multiple_changed_symbols_union():
    defs = [
        _def(1, "a", "src/a.py"),
        _def(2, "b", "src/b.py"),
        _def(10, "test_a", "tests/test_a.py"),
        _def(11, "test_b", "tests/test_b.py"),
    ]
    edges = [(10, 1), (11, 2)]
    graph = _graph(defs, edges)
    inv = TestInventory(
        tests=(
            TestCase("test_a", "tests/test_a.py", 10),
            TestCase("test_b", "tests/test_b.py", 11),
        )
    )
    r = select_tests(
        [_changed("a", "src/a.py"), _changed("b", "src/b.py")], graph, inv
    )
    assert _names(r) == {"test_a", "test_b"}


def test_shallowest_reason_wins_on_multiple_paths():
    # test reaches the change both directly (depth 1) and via a longer path (depth 2)
    defs = [
        _def(1, "core", "src/core.py"),
        _def(2, "wrapper", "src/wrapper.py"),
        _def(10, "test_core", "tests/test_core.py"),
    ]
    # test_core calls core (depth1) and calls wrapper which calls core (depth2)
    edges = [(10, 1), (10, 2), (2, 1)]
    graph = _graph(defs, edges)
    inv = TestInventory(tests=(TestCase("test_core", "tests/test_core.py", 10),))
    r = select_tests([_changed("core", "src/core.py")], graph, inv)
    assert {t.name: t.depth for t in r.selected}["test_core"] == 1


def test_added_symbol_with_callers_selected():
    # an added function that already has a caller wired in the indexed graph
    defs = [
        _def(1, "new_fn", "src/new.py"),
        _def(2, "user", "src/user.py"),
        _def(10, "test_user", "tests/test_user.py"),
    ]
    edges = [(2, 1), (10, 2)]
    graph = _graph(defs, edges)
    inv = TestInventory(tests=(TestCase("test_user", "tests/test_user.py", 10),))
    r = select_tests([_changed("new_fn", "src/new.py", ChangeType.ADDED)], graph, inv)
    assert "test_user" in _names(r)


def test_full_suite_includes_unmapped_files():
    graph = _graph([_def(1, "orphan", "src/orphan.py")], [])
    inv = TestInventory(
        tests=(TestCase("test_x", "tests/test_x.py", 50),),
        unmapped_test_files=frozenset({"tests/weird_spec.rb"}),
    )
    r = select_tests([_changed("orphan", "src/orphan.py")], graph, inv)
    assert r.run_full_suite
    assert any(t.file_path == "tests/weird_spec.rb" for t in r.selected)
    assert r.metrics.selected_tests == r.metrics.total_tests
