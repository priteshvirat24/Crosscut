"""Tests for the Orbit client's graph/inventory construction and mode handling.

Unit tests inject canned query rows (no binary needed). A separate integration test
exercises the real `orbit` CLI when it is installed and a graph has been indexed.
"""

from __future__ import annotations

import shutil

import pytest

from app.crosscut.models import Mode
from app.crosscut.orbit import OrbitClient, OrbitError, queries


class FakeOrbitClient(OrbitClient):
    """OrbitClient whose `query` returns canned rows based on the SQL issued."""

    def __init__(self, definitions, call_pairs, files):
        super().__init__(mode=Mode.LOCAL)
        self._defs = definitions
        self._pairs = call_pairs
        self._files = files

    def query(self, sql: str):  # type: ignore[override]
        if "caller_id" in sql:
            return self._pairs
        if "extension" in sql or "FROM gl_file" in sql:
            return self._files
        return self._defs


def _defrow(id_, name, path, dtype="Function"):
    return {
        "id": id_,
        "name": name,
        "file_path": path,
        "definition_type": dtype,
        "fqn": f"{path}::{name}",
        "start_line": 1,
        "end_line": 2,
        "project_id": 1,
    }


def test_build_graph_direct_edges():
    client = FakeOrbitClient(
        definitions=[_defrow(1, "a", "src/a.py"), _defrow(2, "b", "src/b.py")],
        call_pairs=[{"caller_id": 2, "callee_id": 1}],
        files=[],
    )
    g = client.build_graph()
    assert set(g.definitions) == {1, 2}
    assert g.callers_of(1) == {2}


def test_build_graph_skips_self_loops():
    client = FakeOrbitClient(
        definitions=[_defrow(1, "rec", "src/a.py")],
        call_pairs=[{"caller_id": 1, "callee_id": 1}],
        files=[],
    )
    g = client.build_graph()
    assert g.callers_of(1) == set()


def test_build_graph_handles_null_fields():
    row = _defrow(1, "a", "src/a.py")
    row["fqn"] = None
    row["start_line"] = None
    client = FakeOrbitClient(definitions=[row], call_pairs=[], files=[])
    g = client.build_graph()
    assert g.definitions[1].fqn == ""
    assert g.definitions[1].start_line == 0


def test_build_inventory_maps_tests_and_detects_unmapped():
    client = FakeOrbitClient(
        definitions=[
            _defrow(1, "validate", "src/payment.py"),
            _defrow(10, "test_validate", "tests/test_payment.py"),
            _defrow(11, "make_fixture", "tests/test_payment.py"),  # helper, not a test
        ],
        call_pairs=[],
        files=[
            {"path": "tests/test_payment.py", "extension": "py", "language": "python"},
            {"path": "tests/legacy_spec.rb", "extension": "rb", "language": "unknown"},
            {"path": "tests/__init__.py", "extension": "py", "language": "python"},
            {"path": "tests/conftest.py", "extension": "py", "language": "python"},
        ],
    )
    inv = client.build_inventory()
    names = {t.name for t in inv.tests}
    assert names == {"test_validate"}  # fixture excluded
    # ruby spec file Orbit could not parse -> unmapped; dunder/conftest excluded
    assert inv.unmapped_test_files == frozenset({"tests/legacy_spec.rb"})
    assert inv.total == 2


def test_build_inventory_marks_mapped_files_not_unmapped():
    client = FakeOrbitClient(
        definitions=[_defrow(10, "test_x", "tests/test_x.py")],
        call_pairs=[],
        files=[{"path": "tests/test_x.py", "extension": "py", "language": "python"}],
    )
    inv = client.build_inventory()
    assert inv.unmapped_test_files == frozenset()


def test_remote_mode_requires_credentials():
    client = OrbitClient(mode=Mode.REMOTE)
    with pytest.raises(OrbitError):
        client.query("anything")


def test_index_only_in_local_mode():
    client = OrbitClient(mode=Mode.REMOTE, api_url="https://x", token="t")
    with pytest.raises(OrbitError):
        client.index(".")


def test_call_pairs_sql_includes_all_three_edge_sources():
    sql = queries.call_pairs_sql()
    assert "CALLS" in sql
    assert "EXTENDS" in sql
    assert "gl_imported_symbol" in sql


# ── integration: real binary, real graph (skipped if unavailable) ─────────────────

orbit_available = shutil.which("orbit") is not None


@pytest.mark.skipif(not orbit_available, reason="orbit CLI not installed")
def test_real_orbit_graph_has_definitions():
    client = OrbitClient(mode=Mode.LOCAL)
    try:
        graph = client.build_graph()
    except OrbitError as exc:
        pytest.skip(f"no indexed graph available: {exc}")
    if not graph.definitions:
        pytest.skip("orbit graph is empty (nothing indexed)")
    # the real graph should expose CALLS edges
    assert any(graph.callers.values())
