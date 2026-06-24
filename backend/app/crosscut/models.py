"""Data shapes — the contracts between Crosscut's modules.

These are plain frozen dataclasses so the selection core stays pure and trivially
testable. The Orbit client produces a :class:`CodeGraph`; diff parsing produces
:class:`ChangedSymbol`s; test discovery produces a :class:`TestInventory`;
:func:`crosscut.selection.select_tests` consumes all three.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class ChangeType(StrEnum):
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


class Mode(StrEnum):
    LOCAL = "local"
    REMOTE = "remote"


@dataclass(frozen=True)
class Definition:
    """A node from Orbit's ``gl_definition`` table."""

    id: int
    name: str
    file_path: str
    definition_type: str
    fqn: str = ""
    start_line: int = 0
    end_line: int = 0
    project_id: int = 0


@dataclass(frozen=True)
class ChangedSymbol:
    """A symbol changed by the MR diff (output of diff parsing)."""

    name: str
    file_path: str
    change_type: ChangeType
    symbol_type: str = "function"
    line_number: int = 0
    parameters_changed: bool = False
    return_type_changed: bool = False


@dataclass(frozen=True)
class CodeGraph:
    """A resolved reverse-call graph built from the real Orbit ontology.

    ``callers[callee_id]`` is the set of definition ids that call (or extend)
    ``callee_id``. Cross-file calls that Orbit routes through ``gl_imported_symbol``
    have already been resolved back to target definitions by the Orbit client, so the
    selection core can treat this as a plain in-memory graph.
    """

    definitions: dict[int, Definition] = field(default_factory=dict)
    callers: dict[int, set[int]] = field(default_factory=dict)

    def callers_of(self, def_id: int) -> set[int]:
        return self.callers.get(def_id, set())

    def definitions_in_file(self, file_path: str) -> list[Definition]:
        return [d for d in self.definitions.values() if d.file_path == file_path]

    def find(self, file_path: str, name: str) -> list[Definition]:
        return [
            d
            for d in self.definitions.values()
            if d.file_path == file_path and d.name == name
        ]


@dataclass(frozen=True)
class TestCase:
    """One runnable test, optionally linked to its Orbit definition id."""

    __test__ = False  # not a pytest test class

    name: str
    file_path: str
    definition_id: int | None = None


@dataclass(frozen=True)
class TestInventory:
    """All tests in the repo, plus any test files Orbit could not map.

    ``unmapped_test_files`` are paths that *look* like test files but for which Orbit
    produced no test-case definitions (unparsed language, parse error, etc.). They are
    always selected — Crosscut never silently drops a test it cannot reason about.
    """

    __test__ = False  # not a pytest test class

    tests: tuple[TestCase, ...] = ()
    unmapped_test_files: frozenset[str] = frozenset()

    @property
    def total(self) -> int:
        """Total selectable test units: mapped test cases + unmapped whole files."""
        return len(self.tests) + len(self.unmapped_test_files)


@dataclass(frozen=True)
class SelectedTest:
    """A selected test with the reason it was selected (explainability)."""

    name: str
    file_path: str
    reason: str
    changed_symbol: str | None = None
    depth: int = 0


@dataclass(frozen=True)
class SelectionMetrics:
    total_tests: int
    selected_tests: int

    @property
    def percentage_reduction(self) -> float:
        if self.total_tests <= 0:
            return 0.0
        return round((1 - self.selected_tests / self.total_tests) * 100, 1)

    def as_dict(self) -> dict:
        return {
            "total_tests": self.total_tests,
            "selected_tests": self.selected_tests,
            "percentage_reduction": self.percentage_reduction,
        }


@dataclass(frozen=True)
class SelectionResult:
    """The output of the selection core."""

    selected: tuple[SelectedTest, ...]
    metrics: SelectionMetrics
    mode: Mode
    run_full_suite: bool
    notes: tuple[str, ...] = ()

    @property
    def selected_files(self) -> list[str]:
        seen: dict[str, None] = {}
        for t in self.selected:
            seen.setdefault(t.file_path, None)
        return list(seen)


@dataclass(frozen=True)
class TimingResult:
    """A real, measured timing comparison (full suite vs selected subset)."""

    full_suite_seconds: float
    selected_seconds: float
    measured: bool  # True = actually executed; False = not run (no estimate invented)

    @property
    def seconds_saved(self) -> float:
        return round(max(0.0, self.full_suite_seconds - self.selected_seconds), 2)
