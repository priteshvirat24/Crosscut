"""Tests for the declared test-discovery conventions."""

from __future__ import annotations

import pytest

from app.crosscut import conventions as c


@pytest.mark.parametrize(
    "path",
    [
        "tests/test_payment.py",
        "src/app/foo_test.py",
        "frontend/Button.test.tsx",
        "frontend/Button.spec.ts",
        "spec/models/user_spec.rb",
        "app/models/user_test.rb",
        "src/utils/helpers.py",  # under no test dir but... not a test (checked below)
    ],
)
def test_is_test_file_recognizes_patterns(path):
    # last item is the negative control
    if path == "src/utils/helpers.py":
        assert not c.is_test_file(path)
    else:
        assert c.is_test_file(path)


def test_is_test_file_dir_based():
    assert c.is_test_file("backend/tests/unit/whatever.py")
    assert c.is_test_file("project/__tests__/render.js")


def test_is_test_file_excludes_dunder_and_conftest():
    assert not c.is_test_file("tests/__init__.py")
    assert not c.is_test_file("tests/conftest.py")
    assert not c.is_test_file("tests/setup.py")


def test_is_test_filename_strict():
    assert c.is_test_filename("a/b/test_x.py")
    assert c.is_test_filename("a/b/x_test.py")
    assert c.is_test_filename("a/b/x.spec.ts")
    # strict filename check ignores directory-only signals
    assert not c.is_test_filename("tests/helpers.py")
    assert not c.is_test_filename("tests/__init__.py")
    assert not c.is_test_filename("tests/conftest.py")


def test_is_test_definition_true_for_test_functions():
    assert c.is_test_definition("test_validate", "Function", "tests/test_x.py")
    assert c.is_test_definition("test_validate", "Method", "tests/test_x.py")
    assert c.is_test_definition("shouldValidate", "Function", "x.spec.ts")


def test_is_test_definition_false_positive_guards():
    # a helper/fixture inside a tests dir is NOT a test case
    assert not c.is_test_definition("make_user", "Function", "tests/test_x.py")
    assert not c.is_test_definition("setup_module", "Function", "tests/test_x.py")
    # a test_-named function in a non-test file is not a test case
    assert not c.is_test_definition("test_validate", "Function", "src/app.py")
    # a Field/Variable named test_x is not a callable test
    assert not c.is_test_definition("test_data", "Variable", "tests/test_x.py")


def test_is_test_class():
    assert c.is_test_class("TestPayment", "Class", "tests/test_x.py")
    assert c.is_test_class("PaymentTests", "Class", "tests/test_x.py")
    assert not c.is_test_class("PaymentHelper", "Class", "tests/test_x.py")
    assert not c.is_test_class("TestPayment", "Class", "src/app.py")


def test_test_file_matches_source():
    assert c.test_file_matches_source("tests/test_payment.py", "src/payment.py")
    assert c.test_file_matches_source("src/payment_test.py", "src/payment.py")
    assert c.test_file_matches_source("ui/Button.test.tsx", "ui/Button.tsx")
    assert not c.test_file_matches_source("tests/test_payment.py", "src/checkout.py")


def test_test_file_matches_source_ignores_generic_stems():
    # __init__ / index / main should not create spurious matches
    assert not c.test_file_matches_source("tests/test_init.py", "pkg/__init__.py")
    assert not c.test_file_matches_source("tests/test_index.py", "ui/index.ts")
