"""End-to-end CLI test with a fake Orbit backend (no binary, no network)."""

from __future__ import annotations

import app.crosscut.cli as cli
from app.crosscut.models import CodeGraph, Definition, TestCase, TestInventory


class _FakeClient:
    def __init__(self, graph, inventory):
        self._graph = graph
        self._inventory = inventory

    @classmethod
    def make(cls, graph, inventory):
        def _from_config(_config):
            return cls(graph, inventory)

        return _from_config

    def build_graph(self):
        return self._graph

    def build_inventory(self, graph=None):
        return self._inventory


def _fixture_graph():
    validate = Definition(1, "validate", "src/payment.py", "Function")
    test_validate = Definition(10, "test_validate", "tests/test_payment.py", "Function")
    graph = CodeGraph(
        definitions={1: validate, 10: test_validate},
        callers={1: {10}},
    )
    inv = TestInventory(
        tests=(
            TestCase("test_validate", "tests/test_payment.py", 10),
            TestCase("test_other", "tests/test_other.py", 11),
        )
    )
    return graph, inv


def test_cli_writes_pipeline_and_comment(tmp_path, monkeypatch):
    graph, inv = _fixture_graph()
    monkeypatch.setattr(cli.OrbitClient, "from_config", _FakeClient.make(graph, inv))

    diff = tmp_path / "changes.diff"
    diff.write_text(
        "diff --git a/src/payment.py b/src/payment.py\n"
        "@@ -1,2 +1,2 @@\n"
        "-def validate(amount):\n"
        "+def validate(amount, region):\n"
    )
    out_pipe = tmp_path / "pipe.yml"
    out_comment = tmp_path / "comment.md"

    rc = cli.main(
        [
            "--repo", str(tmp_path),
            "--diff", str(diff),
            "--out-pipeline", str(out_pipe),
            "--out-comment", str(out_comment),
        ]
    )
    assert rc == 0
    pipe_text = out_pipe.read_text()
    comment_text = out_comment.read_text()
    assert "crosscut:targeted" in pipe_text
    assert "tests/test_payment.py" in pipe_text
    assert "tests/test_other.py" not in pipe_text  # unrelated test excluded
    assert "Running 1 of 2 tests" in comment_text
    assert "validate" in comment_text


def test_cli_handles_no_changes(tmp_path, monkeypatch):
    graph, inv = _fixture_graph()
    monkeypatch.setattr(cli.OrbitClient, "from_config", _FakeClient.make(graph, inv))
    diff = tmp_path / "empty.diff"
    diff.write_text("")
    out_pipe = tmp_path / "pipe.yml"
    out_comment = tmp_path / "comment.md"
    rc = cli.main(
        ["--repo", str(tmp_path), "--diff", str(diff),
         "--out-pipeline", str(out_pipe), "--out-comment", str(out_comment)]
    )
    assert rc == 0
    assert "no-impacted-tests" in out_pipe.read_text()
