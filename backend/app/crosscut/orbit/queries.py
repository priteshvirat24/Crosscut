"""SQL against the real Orbit Local ontology (DuckDB), discovered live via `orbit schema`.

Tables: gl_definition, gl_file, gl_directory, gl_imported_symbol, gl_edge.
Edge relationship_kind values: CALLS, DEFINES, IMPORTS, CONTAINS, EXTENDS.
There is no TESTS edge — tests are ordinary definitions identified by path/name convention.
"""

from __future__ import annotations

# Definition types Orbit emits that can be a call/instantiation target. Includes every
# function/method/class variant (plain, async, decorated) across the 11+ languages Orbit
# parses, so cross-file call resolution doesn't miss e.g. @dataclass-decorated classes.
CALLABLE_DEF_TYPES = (
    "Function",
    "AsyncFunction",
    "Method",
    "Class",
    "Interface",
    "DecoratedFunction",
    "DecoratedAsyncFunction",
    "DecoratedMethod",
    "DecoratedAsyncMethod",
    "DecoratedClass",
)

# All definitions in the graph.
DEFINITIONS = """
SELECT id, name, fqn, file_path, definition_type, start_line, end_line, project_id
FROM gl_definition
"""

# All files (used to find test files Orbit could not map to any test case).
FILES = """
SELECT path, name, extension, language
FROM gl_file
"""


def call_pairs_sql() -> str:
    """Resolved (caller_id, callee_id) edges for reverse traversal.

    Three sources, unioned:
      1. Direct Definition -> Definition CALLS edges.
      2. EXTENDS edges (a subclass is treated as a caller of its superclass, so a change
         to the superclass re-tests the subclass).
      3. Cross-file CALLS that Orbit routes through gl_imported_symbol, resolved back to
         the target definition by name. This over-approximates (a name may match several
         definitions) which is intentional: over-selecting tests is safe, under-selecting
         is not.
    """
    callable_list = ", ".join(f"'{t}'" for t in CALLABLE_DEF_TYPES)
    return f"""
    SELECT e.source_id AS caller_id, e.target_id AS callee_id
    FROM gl_edge e
    WHERE e.relationship_kind = 'CALLS'
      AND e.source_kind = 'Definition'
      AND e.target_kind = 'Definition'
    UNION
    SELECT e.source_id AS caller_id, e.target_id AS callee_id
    FROM gl_edge e
    WHERE e.relationship_kind = 'EXTENDS'
      AND e.source_kind = 'Definition'
      AND e.target_kind = 'Definition'
    UNION
    SELECT e.source_id AS caller_id, d.id AS callee_id
    FROM gl_edge e
    JOIN gl_imported_symbol i ON e.target_id = i.id
    JOIN gl_definition d ON d.name = i.identifier_name
    WHERE e.relationship_kind = 'CALLS'
      AND e.source_kind = 'Definition'
      AND e.target_kind = 'ImportedSymbol'
      AND i.identifier_name <> ''
      AND d.definition_type IN ({callable_list})
    """
