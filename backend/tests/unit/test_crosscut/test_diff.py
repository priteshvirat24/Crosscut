"""Tests for diff parsing — edge cases across languages and change kinds."""

from __future__ import annotations

from app.crosscut.diff import changed_files, parse_diff
from app.crosscut.models import ChangeType


def _by_name(changes):
    return {c.name: c for c in changes}


def test_empty_diff():
    assert parse_diff("") == []
    assert parse_diff("   \n  ") == []


def test_signature_param_added():
    diff = """diff --git a/src/pay.py b/src/pay.py
--- a/src/pay.py
+++ b/src/pay.py
@@ -1,3 +1,3 @@
-def validate(amount):
+def validate(amount, region):
     return True
"""
    c = _by_name(parse_diff(diff))["validate"]
    assert c.change_type == ChangeType.MODIFIED
    assert c.parameters_changed
    assert not c.return_type_changed
    assert c.file_path == "src/pay.py"


def test_return_type_change_python():
    diff = """diff --git a/src/pay.py b/src/pay.py
@@ -1,2 +1,2 @@
-def total(x) -> int:
+def total(x) -> float:
     ...
"""
    c = _by_name(parse_diff(diff))["total"]
    assert c.change_type == ChangeType.MODIFIED
    assert c.return_type_changed
    assert not c.parameters_changed


def test_function_deleted():
    diff = """diff --git a/src/pay.py b/src/pay.py
@@ -1,4 +1,1 @@
-def old_helper(x):
-    return x
 keep = 1
"""
    c = _by_name(parse_diff(diff))["old_helper"]
    assert c.change_type == ChangeType.DELETED


def test_function_added():
    diff = """diff --git a/src/pay.py b/src/pay.py
@@ -1,1 +1,3 @@
 keep = 1
+def brand_new(a, b):
+    return a + b
"""
    c = _by_name(parse_diff(diff))["brand_new"]
    assert c.change_type == ChangeType.ADDED


def test_class_change_detected_as_class():
    diff = """diff --git a/src/m.py b/src/m.py
@@ -1,2 +1,2 @@
-class Foo:
+class Foo(Base):
     pass
"""
    # class line changed; "Foo" appears in both -> modified, symbol_type class
    c = _by_name(parse_diff(diff))["Foo"]
    assert c.symbol_type == "class"


def test_added_class():
    diff = """diff --git a/src/m.py b/src/m.py
@@ -1,1 +1,3 @@
 x = 1
+class NewModel:
+    pass
"""
    c = _by_name(parse_diff(diff))["NewModel"]
    assert c.change_type == ChangeType.ADDED
    assert c.symbol_type == "class"


def test_javascript_function():
    diff = """diff --git a/src/app.js b/src/app.js
@@ -1,2 +1,2 @@
-function handler(req, res) {
+function handler(req, res, next) {
"""
    c = _by_name(parse_diff(diff))["handler"]
    assert c.change_type == ChangeType.MODIFIED
    assert c.parameters_changed


def test_typescript_arrow_added():
    diff = """diff --git a/src/util.ts b/src/util.ts
@@ -1,1 +1,2 @@
 const x = 1
+export const compute = (a: number) => a * 2
"""
    c = _by_name(parse_diff(diff))["compute"]
    assert c.change_type == ChangeType.ADDED


def test_multi_file_diff():
    diff = """diff --git a/src/a.py b/src/a.py
@@ -1,1 +1,2 @@
 x = 1
+def fa():
+    pass
diff --git a/src/b.py b/src/b.py
@@ -1,1 +1,2 @@
 y = 1
+def fb():
+    pass
"""
    changes = parse_diff(diff)
    files = {c.file_path for c in changes}
    assert files == {"src/a.py", "src/b.py"}


def test_rename_emits_rename_changes():
    diff = """diff --git a/src/old_name.py b/src/new_name.py
similarity index 95%
rename from src/old_name.py
rename to src/new_name.py
"""
    changes = parse_diff(diff)
    types = {c.change_type for c in changes}
    paths = {c.file_path for c in changes}
    assert ChangeType.RENAMED in types
    assert "src/new_name.py" in paths
    assert "src/old_name.py" in paths


def test_malformed_diff_does_not_crash():
    diff = "this is not a real diff\n@@ broken @@\n+def x("
    # should not raise; may return [] or partial
    result = parse_diff(diff)
    assert isinstance(result, list)


def test_non_code_file_change_yields_no_symbols():
    diff = """diff --git a/README.md b/README.md
@@ -1,1 +1,2 @@
 # Title
+Some new prose line.
"""
    assert parse_diff(diff) == []


def test_changed_files_helper():
    diff = """diff --git a/src/a.py b/src/a.py
@@ -1 +1 @@
-x
+y
diff --git a/src/b.py b/src/b.py
@@ -1 +1 @@
-x
+y
"""
    assert changed_files(diff) == ["src/a.py", "src/b.py"]


def test_no_change_lines_returns_empty():
    diff = """diff --git a/src/a.py b/src/a.py
@@ -1,2 +1,2 @@
 unchanged
 also_unchanged
"""
    assert parse_diff(diff) == []


def test_keyword_lines_not_treated_as_symbols():
    diff = """diff --git a/src/a.py b/src/a.py
@@ -1,2 +1,3 @@
 def real_fn():
-    if old_cond:
+    if new_cond:
+    while True:
"""
    names = {c.name for c in parse_diff(diff)}
    assert "if" not in names
    assert "while" not in names
