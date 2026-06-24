"""Diff parsing — pure, no I/O.

Turns a unified diff into a list of :class:`ChangedSymbol`. Multi-language, multi-file.
Detects added / deleted / modified (signature change) functions, classes and methods, and
file renames. This is deliberately conservative: when in doubt it emits a change so the
selection core errs toward running more tests, never fewer.
"""

from __future__ import annotations

import re
from typing import Any

from app.crosscut.models import ChangedSymbol, ChangeType

# Symbol-definition patterns across languages. Group 1 = name, group 2 = params (opt),
# group 3 = return type (python, opt).
_PATTERNS: dict[str, re.Pattern[str]] = {
    "python_def": re.compile(r"^\s*(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^:]+))?"),
    "python_class": re.compile(r"^\s*class\s+(\w+)"),
    "js_function": re.compile(
        r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)"
    ),
    "js_arrow": re.compile(
        r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>"
    ),
    "js_method": re.compile(
        r"^\s*(?:public|private|protected|static|async|\s)*(\w+)\s*\(([^)]*)\)\s*\{?\s*$"
    ),
    "ts_class": re.compile(r"^\s*(?:export\s+)?(?:abstract\s+)?class\s+(\w+)"),
    "ruby_def": re.compile(r"^\s*def\s+(\w+)(?:\(([^)]*)\))?"),
    "ruby_class": re.compile(r"^\s*class\s+(\w+)"),
    "go_func": re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?(\w+)\s*\(([^)]*)\)"),
}
_CLASS_PATTERNS = {"python_class", "ts_class", "ruby_class"}


def parse_diff(diff_content: str) -> list[ChangedSymbol]:
    """Parse a unified diff into a list of changed symbols."""
    if not diff_content or not diff_content.strip():
        return []
    hunks, renames = _parse_hunks(diff_content)
    changes = _extract_symbol_changes(hunks)
    changes.extend(renames)
    return _dedupe(changes)


def changed_files(diff_content: str) -> list[str]:
    """Return the list of files touched by the diff (added/modified/deleted/renamed)."""
    files: list[str] = []
    seen: set[str] = set()
    for line in diff_content.split("\n"):
        if line.startswith("diff --git"):
            m = re.search(r"b/(.+)$", line)
            if m and m.group(1) not in seen:
                seen.add(m.group(1))
                files.append(m.group(1))
    return files


# ── internals ─────────────────────────────────────────────────────────────────────


def _parse_hunks(diff_content: str) -> tuple[list[dict[str, Any]], list[ChangedSymbol]]:
    hunks: list[dict[str, Any]] = []
    renames: list[ChangedSymbol] = []
    current_file = ""
    rename_from = ""
    current: dict[str, Any] | None = None

    for line in diff_content.split("\n"):
        if line.startswith("diff --git"):
            if current:
                hunks.append(current)
                current = None
            m = re.search(r"b/(.+)$", line)
            current_file = m.group(1) if m else ""
            rename_from = ""
        elif line.startswith("rename from "):
            rename_from = line[len("rename from ") :].strip()
        elif line.startswith("rename to "):
            rename_to = line[len("rename to ") :].strip()
            renames.append(
                ChangedSymbol(
                    name=rename_to,
                    file_path=rename_to,
                    change_type=ChangeType.RENAMED,
                    symbol_type="file",
                    line_number=0,
                )
            )
            if rename_from:
                renames.append(
                    ChangedSymbol(
                        name=rename_from,
                        file_path=rename_from,
                        change_type=ChangeType.RENAMED,
                        symbol_type="file",
                        line_number=0,
                    )
                )
        elif line.startswith("@@"):
            if current:
                hunks.append(current)
            m = re.search(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            current = {
                "file": current_file,
                "old_start": int(m.group(1)) if m else 0,
                "new_start": int(m.group(2)) if m else 0,
                "added": [],
                "removed": [],
            }
        elif current is not None:
            if line.startswith("+") and not line.startswith("+++"):
                current["added"].append(line[1:])
            elif line.startswith("-") and not line.startswith("---"):
                current["removed"].append(line[1:])

    if current:
        hunks.append(current)
    return hunks, renames


def _match_symbol(line: str) -> tuple[str, str, str, str] | None:
    """Return (name, params, return_type, kind) for the first pattern that matches."""
    for kind, pat in _PATTERNS.items():
        m = pat.match(line)
        if not m:
            continue
        name = m.group(1)
        # skip language keywords that the loose js_method pattern can catch
        if name in {"if", "for", "while", "switch", "catch", "return", "function"}:
            continue
        params = m.group(2) if (m.lastindex or 0) >= 2 and m.group(2) is not None else ""
        ret = m.group(3).strip() if (m.lastindex or 0) >= 3 and m.group(3) else ""
        return name, params, ret, kind
    return None


def _extract_symbol_changes(hunks: list[dict[str, Any]]) -> list[ChangedSymbol]:
    changes: list[ChangedSymbol] = []
    for hunk in hunks:
        file_path = hunk["file"]
        removed_syms = {s[0]: s for s in (_match_symbol(ln) for ln in hunk["removed"]) if s}
        added_syms = {s[0]: s for s in (_match_symbol(ln) for ln in hunk["added"]) if s}

        # Deleted or modified (present in removed)
        for name, (_rname, rparams, rret, rkind) in removed_syms.items():
            symbol_type = "class" if rkind in _CLASS_PATTERNS else "function"
            if name not in added_syms:
                changes.append(
                    ChangedSymbol(
                        name=name,
                        file_path=file_path,
                        change_type=ChangeType.DELETED,
                        symbol_type=symbol_type,
                        line_number=hunk["old_start"],
                    )
                )
            else:
                _, aparams, aret, _ = added_syms[name]
                params_changed = rparams.strip() != aparams.strip()
                return_changed = rret.strip() != aret.strip()
                changes.append(
                    ChangedSymbol(
                        name=name,
                        file_path=file_path,
                        change_type=ChangeType.MODIFIED,
                        symbol_type=symbol_type,
                        line_number=hunk["new_start"],
                        parameters_changed=params_changed,
                        return_type_changed=return_changed,
                    )
                )

        # Added (present in added but not removed)
        for name, (_aname, _aparams, _aret, akind) in added_syms.items():
            if name in removed_syms:
                continue
            symbol_type = "class" if akind in _CLASS_PATTERNS else "function"
            changes.append(
                ChangedSymbol(
                    name=name,
                    file_path=file_path,
                    change_type=ChangeType.ADDED,
                    symbol_type=symbol_type,
                    line_number=hunk["new_start"],
                )
            )
    return changes


def _dedupe(changes: list[ChangedSymbol]) -> list[ChangedSymbol]:
    seen: set[tuple[str, str, str]] = set()
    out: list[ChangedSymbol] = []
    for c in changes:
        key = (c.file_path, c.name, c.change_type.value)
        if key not in seen:
            seen.add(key)
            out.append(c)
    return out
