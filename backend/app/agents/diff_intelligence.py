"""Agent 1: Diff Intelligence — Analyzes MR diffs to extract structured change reports.

Responsibilities:
- Parse unified diff format
- Extract modified, deleted, renamed, added functions/classes
- Detect signature changes, parameter changes, return type changes
- Produce a structured ChangeReport
"""

from __future__ import annotations

import re
import structlog
from typing import Any

from app.agents.state import SentinelState, ChangeReport, ChangeItem

logger = structlog.get_logger()


# ── Diff parsing utilities ────────────────────────────────────────────────────


def parse_diff_hunks(diff_content: str) -> list[dict[str, Any]]:
    """Parse unified diff into structured hunks."""
    hunks: list[dict[str, Any]] = []
    current_file = ""
    current_hunk: dict[str, Any] | None = None

    for line in diff_content.split("\n"):
        # File header
        if line.startswith("diff --git"):
            match = re.search(r"b/(.+)$", line)
            if match:
                current_file = match.group(1)

        elif line.startswith("--- "):
            pass  # Old file path

        elif line.startswith("+++ "):
            pass  # New file path

        elif line.startswith("@@"):
            # New hunk
            if current_hunk:
                hunks.append(current_hunk)
            line_match = re.search(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            current_hunk = {
                "file": current_file,
                "old_start": int(line_match.group(1)) if line_match else 0,
                "new_start": int(line_match.group(2)) if line_match else 0,
                "added_lines": [],
                "removed_lines": [],
                "context_lines": [],
            }

        elif current_hunk is not None:
            if line.startswith("+") and not line.startswith("+++"):
                current_hunk["added_lines"].append(line[1:])
            elif line.startswith("-") and not line.startswith("---"):
                current_hunk["removed_lines"].append(line[1:])
            else:
                current_hunk["context_lines"].append(line)

    if current_hunk:
        hunks.append(current_hunk)

    return hunks


def extract_function_changes(hunks: list[dict[str, Any]]) -> list[ChangeItem]:
    """Extract function-level changes from diff hunks."""
    changes: list[ChangeItem] = []

    # Patterns for function/method detection across languages
    patterns = {
        "python_def": re.compile(r"^\s*(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*(\S+))?"),
        "js_function": re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)"),
        "js_arrow": re.compile(r"^\s*(?:export\s+)?(?:const|let)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)"),
        "ruby_def": re.compile(r"^\s*def\s+(\w+)(?:\(([^)]*)\))?"),
        "class_def": re.compile(r"^\s*class\s+(\w+)"),
    }

    for hunk in hunks:
        file_path = hunk["file"]

        # Find removed functions (deleted)
        for line in hunk["removed_lines"]:
            for pattern_name, pattern in patterns.items():
                match = pattern.match(line)
                if match:
                    func_name = match.group(1)
                    params = match.group(2) if match.lastindex and match.lastindex >= 2 else ""

                    # Check if it still exists in added lines
                    is_deleted = True
                    new_signature = ""
                    for added_line in hunk["added_lines"]:
                        added_match = pattern.match(added_line)
                        if added_match and added_match.group(1) == func_name:
                            is_deleted = False
                            new_signature = added_line.strip()
                            break

                    if is_deleted:
                        changes.append(
                            ChangeItem(
                                change_type="deleted",
                                symbol_name=func_name,
                                symbol_type="class" if "class" in pattern_name else "function",
                                file_path=file_path,
                                line_number=hunk["old_start"],
                                description=f"{'Class' if 'class' in pattern_name else 'Function'} '{func_name}' was deleted",
                                before_signature=line.strip(),
                                after_signature="",
                                parameters_changed=False,
                                return_type_changed=False,
                            )
                        )
                    else:
                        # Signature changed
                        old_params = params or ""
                        new_match = pattern.match(new_signature)
                        new_params = (
                            new_match.group(2)
                            if new_match and new_match.lastindex and new_match.lastindex >= 2
                            else ""
                        )

                        params_changed = old_params.strip() != new_params.strip()
                        return_changed = False
                        if "python_def" in pattern_name and match.lastindex and match.lastindex >= 3:
                            old_return = match.group(3) or ""
                            new_full_match = patterns["python_def"].match(new_signature)
                            new_return = (
                                new_full_match.group(3) or ""
                                if new_full_match and new_full_match.lastindex and new_full_match.lastindex >= 3
                                else ""
                            )
                            return_changed = old_return != new_return

                        if params_changed or return_changed:
                            changes.append(
                                ChangeItem(
                                    change_type="modified",
                                    symbol_name=func_name,
                                    symbol_type="function",
                                    file_path=file_path,
                                    line_number=hunk["new_start"],
                                    description=f"Function '{func_name}' signature changed",
                                    before_signature=line.strip(),
                                    after_signature=new_signature.strip(),
                                    parameters_changed=params_changed,
                                    return_type_changed=return_changed,
                                )
                            )

        # Find new functions (added)
        for line in hunk["added_lines"]:
            for pattern_name, pattern in patterns.items():
                match = pattern.match(line)
                if match:
                    func_name = match.group(1)

                    # Check if it's genuinely new (not in removed lines)
                    is_new = True
                    for removed_line in hunk["removed_lines"]:
                        removed_match = pattern.match(removed_line)
                        if removed_match and removed_match.group(1) == func_name:
                            is_new = False
                            break

                    if is_new:
                        changes.append(
                            ChangeItem(
                                change_type="added",
                                symbol_name=func_name,
                                symbol_type="class" if "class" in pattern_name else "function",
                                file_path=file_path,
                                line_number=hunk["new_start"],
                                description=f"New {'class' if 'class' in pattern_name else 'function'} '{func_name}' added",
                                before_signature="",
                                after_signature=line.strip(),
                                parameters_changed=False,
                                return_type_changed=False,
                            )
                        )

    return changes


# ── Agent Node ────────────────────────────────────────────────────────────────


async def diff_intelligence_agent(state: SentinelState) -> dict:
    """LangGraph node: Analyze MR diff and produce a structured change report.

    Reads: diff_content
    Writes: change_report, execution_log
    """
    logger.info("agent.diff_analyzer.start", analysis_id=state.get("analysis_id"))

    diff_content = state.get("diff_content", "")
    execution_log = list(state.get("execution_log", []))
    
    if not diff_content:
        execution_log.append("Crosscut: No diff content provided")
        return {
            "change_report": ChangeReport(
                total_changes=0,
                files_changed=[],
                changes=[],
                summary="No diff content available for analysis.",
            ),
            "execution_log": execution_log,
            "current_step": "diff_intelligence_complete",
        }

    # Parse the diff
    hunks = parse_diff_hunks(diff_content)
    files_changed = list({h["file"] for h in hunks})

    # Extract function-level changes
    changes = extract_function_changes(hunks)
    execution_log.append(
        f"Diff Analyzer extracted {len(changes)} function/class modifications."
    )

    # Build summary
    deleted = sum(1 for c in changes if c["change_type"] == "deleted")
    modified = sum(1 for c in changes if c["change_type"] == "modified")
    added = sum(1 for c in changes if c["change_type"] == "added")

    summary = (
        f"Analyzed {len(hunks)} diff hunks across {len(files_changed)} files. "
        f"Found {len(changes)} symbol changes: "
        f"{deleted} deleted, {modified} modified, {added} added."
    )

    execution_log.append(f"Diff Analyzer: {summary}")

    change_report = ChangeReport(
        total_changes=len(changes),
        files_changed=files_changed,
        changes=changes,
        summary=summary,
    )

    logger.info(
        "Diff Analyzer completed", extra={"changes": len(changes)},
        files=len(files_changed),
    )

    return {
        "change_report": change_report,
        "execution_log": execution_log,
        "current_step": "diff_intelligence_complete",
    }
