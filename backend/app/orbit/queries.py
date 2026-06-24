"""Pre-built Orbit query templates.

These queries use Orbit's Cypher-like DSL for querying the knowledge graph.
"""

# ── Cross-repository callers ──────────────────────────────────────────────────
# Finds all functions across repositories that call the specified function

CROSS_REPO_CALLERS = """
MATCH (caller:Function)-[:CALLS]->(target:Function {name: $function_name})
WHERE caller.repository != target.repository
RETURN caller.repository AS repository,
       caller.file AS file,
       caller.name AS name,
       caller.line AS line,
       count(*) AS call_count
ORDER BY call_count DESC
"""

# ── Dependency chain ──────────────────────────────────────────────────────────
# Finds the full dependency chain up to N levels deep

DEPENDENCY_CHAIN = """
MATCH path = (source:Repository)-[:DEPENDS_ON*1..$max_depth]->(target:Repository {name: $repo_name})
RETURN path,
       length(path) AS depth,
       [n IN nodes(path) | n.name] AS repo_chain
ORDER BY depth ASC
"""

# ── Symbol lookup ─────────────────────────────────────────────────────────────
# Finds all occurrences of a symbol across indexed repositories

SYMBOL_LOOKUP = """
MATCH (s:Symbol {name: $symbol_name, type: $symbol_type})
RETURN s.repository AS repository,
       s.file AS file,
       s.name AS name,
       s.line AS line,
       s.type AS type
ORDER BY s.repository
"""

# ── Import graph ──────────────────────────────────────────────────────────────
# Finds which files import a specific module

IMPORT_GRAPH = """
MATCH (importer:File)-[:IMPORTS]->(target:Module {name: $module_name})
RETURN importer.repository AS repository,
       importer.path AS file_path,
       target.name AS imported_module
"""

# ── Repository relationships ──────────────────────────────────────────────────
# Maps all relationships between repositories in a group

REPO_RELATIONSHIPS = """
MATCH (a:Repository)-[r:DEPENDS_ON]->(b:Repository)
WHERE a.group = $group_name OR b.group = $group_name
RETURN a.name AS source_repo,
       b.name AS target_repo,
       r.type AS dependency_type,
       r.weight AS weight
"""
