"""Test-discovery conventions — pure, declared rules (no I/O).

Orbit has no TESTS edge: tests are ordinary functions living in test files,
identified by path/name convention. These rules are declared here so they are
auditable in one place and unit-testable in isolation.
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath

# A file is a test file if any of these hold (checked against the POSIX path).
_TEST_DIR_PARTS = {"tests", "test", "spec", "__tests__"}
_TEST_FILENAME_PATTERNS = (
    re.compile(r"^test_.+\.py$"),        # pytest / unittest:  test_foo.py
    re.compile(r".+_test\.py$"),         # go-style / pytest:  foo_test.py
    re.compile(r".+_test\.rb$"),         # ruby minitest:      foo_test.rb
    re.compile(r".+_spec\.rb$"),         # rspec:              foo_spec.rb
    re.compile(r".+\.test\.[jt]sx?$"),   # jest/vitest:        foo.test.ts
    re.compile(r".+\.spec\.[jt]sx?$"),   # jasmine/jest:       foo.spec.tsx
)

# Within a test file, a definition is a test case if its name matches these.
_TEST_NAME_PATTERNS = (
    re.compile(r"^test_"),               # python:  def test_*
    re.compile(r"^test[A-Z]"),           # junit-ish: testSomething
    re.compile(r"^should[A-Z\s]"),       # bdd:     should validate ...
    re.compile(r"^it[\s_]"),             # bdd:     it should ...
)
# A class is a test container if it looks like one (its methods named test_* count).
_TEST_CLASS_PATTERN = re.compile(r"^Test[A-Z0-9_]|.*Test$|.*Tests$|.*Spec$")

# Definition types Orbit emits that can be a runnable test case.
_CALLABLE_DEF_TYPES = {
    "Function",
    "Method",
    "AsyncFunction",
    "DecoratedFunction",
    "DecoratedMethod",
    "DecoratedAsyncFunction",
    "DecoratedAsyncMethod",
}


# Files that live under a tests/ dir but are never themselves runnable tests.
_NON_TEST_FILENAMES = {"__init__.py", "conftest.py", "setup.py"}


def is_test_filename(file_path: str) -> bool:
    """Strict: the *filename* matches a test pattern (test_x.py, x_test.py, x.spec.ts...).

    Used to decide which files must be run wholesale when Orbit cannot map them — this
    must not fire on __init__.py / conftest.py / fixtures merely because they sit in a
    tests/ directory.
    """
    if not file_path:
        return False
    name = PurePosixPath(file_path.replace("\\", "/")).name
    return any(pat.search(name) for pat in _TEST_FILENAME_PATTERNS)


def is_test_file(file_path: str) -> bool:
    """True if the path can contain tests, by directory or filename convention.

    Broader than :func:`is_test_filename` (a ``test_*`` function in ``tests/util.py`` is
    still a test), but excludes obvious non-test files like ``__init__.py``.
    """
    if not file_path:
        return False
    p = PurePosixPath(file_path.replace("\\", "/"))
    if p.name in _NON_TEST_FILENAMES:
        return False
    if any(part in _TEST_DIR_PARTS for part in p.parts[:-1]):
        return True
    return any(pat.search(p.name) for pat in _TEST_FILENAME_PATTERNS)


def is_test_definition(name: str, definition_type: str, file_path: str) -> bool:
    """True if a definition in a test file is itself a runnable test case.

    Guards against false positives: a fixture/helper inside a tests/ dir whose name
    does not match a test-case pattern is NOT a test (e.g. ``make_user`` in tests/).
    """
    if not is_test_file(file_path):
        return False
    if definition_type not in _CALLABLE_DEF_TYPES:
        return False
    return any(pat.search(name) for pat in _TEST_NAME_PATTERNS)


def is_test_class(name: str, definition_type: str, file_path: str) -> bool:
    """True if a class in a test file is a test container (e.g. ``class TestFoo``)."""
    if not is_test_file(file_path):
        return False
    if definition_type != "Class":
        return False
    return bool(_TEST_CLASS_PATTERN.match(name))


def _stem(file_path: str) -> str:
    """Filename without its test/spec affixes or extension. ``test_foo.py`` -> ``foo``."""
    name = PurePosixPath(file_path.replace("\\", "/")).name
    name = re.sub(r"\.(test|spec)\.[jt]sx?$", "", name)   # foo.test.ts -> foo
    name = re.sub(r"\.[A-Za-z0-9]+$", "", name)            # strip remaining extension
    name = re.sub(r"^test_", "", name)                     # test_foo -> foo
    name = re.sub(r"_(test|spec)$", "", name)              # foo_test -> foo
    return name


def test_file_matches_source(test_path: str, source_path: str) -> bool:
    """Heuristic: does this test file conventionally cover this source file?

    Matches by shared base name (``payment.py`` <-> ``test_payment.py``). Used only
    as a conservative fallback for a changed source symbol with no callers — never to
    *exclude* a test.
    """
    if not test_path or not source_path:
        return False
    src_stem = _stem(source_path)
    if not src_stem or src_stem in {"init", "__init__", "index", "main"}:
        return False
    return _stem(test_path) == src_stem
