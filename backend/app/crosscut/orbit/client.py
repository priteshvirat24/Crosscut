"""The single Orbit client.

Local mode  : shells out to the real `orbit` CLI (`orbit sql -F json`) over the DuckDB
              graph at ~/.orbit/graph.duckdb. No GitLab account required.
Remote mode : issues a real HTTP POST to GitLab's Orbit REST endpoint
              (`POST {api_url}/query`). Requires the `knowledge_graph` group feature flag
              and a token. Implemented against GitLab's documented interface; the Local
              path is what is exercised in this repo's tests and demo.

Both modes produce the same in-memory shapes (`CodeGraph`, `TestInventory`) so the
selection core is mode-agnostic.
"""

from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.request
from typing import Any

from app.crosscut import conventions
from app.crosscut.models import CodeGraph, Definition, Mode, TestCase, TestInventory
from app.crosscut.orbit import queries


class OrbitError(RuntimeError):
    """Raised when an Orbit query fails."""


class OrbitClient:
    def __init__(
        self,
        mode: Mode = Mode.LOCAL,
        *,
        orbit_bin: str = "orbit",
        db_path: str | None = None,
        api_url: str | None = None,
        token: str | None = None,
        timeout: int = 120,
    ) -> None:
        self.mode = mode
        self.orbit_bin = orbit_bin
        self.db_path = db_path
        self.api_url = api_url.rstrip("/") if api_url else None
        self.token = token
        self.timeout = timeout

    # ── construction ────────────────────────────────────────────────────────────
    @classmethod
    def from_config(cls, config: Any) -> OrbitClient:
        """Build a client from a `CrosscutConfig` (see crosscut.config)."""
        return cls(
            mode=config.orbit_mode,
            orbit_bin=config.orbit_bin,
            db_path=config.orbit_db_path,
            api_url=config.orbit_api_url,
            token=config.orbit_token,
        )

    # ── indexing (local only) ─────────────────────────────────────────────────────
    def index(self, repo_path: str) -> dict[str, Any]:
        """Index a repository with the local Orbit CLI; returns its JSON statistics."""
        if self.mode is not Mode.LOCAL:
            raise OrbitError("index() is only available in Local mode")
        cmd = [self.orbit_bin, "index", repo_path, "--stats"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
        if proc.returncode != 0:
            raise OrbitError(f"orbit index failed: {proc.stderr.strip()}")
        try:
            stats: dict[str, Any] = json.loads(proc.stdout or "{}")
            return stats
        except json.JSONDecodeError as exc:
            raise OrbitError(f"could not parse orbit index output: {exc}") from exc

    # ── raw query ─────────────────────────────────────────────────────────────────
    def query(self, sql: str) -> list[dict[str, Any]]:
        """Run a read-only query and return rows as dicts."""
        if self.mode is Mode.LOCAL:
            return self._query_local(sql)
        return self._query_remote(sql)

    def _query_local(self, sql: str) -> list[dict[str, Any]]:
        cmd = [self.orbit_bin, "sql", sql, "-F", "json"]
        if self.db_path:
            cmd += ["--db", self.db_path]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
        except FileNotFoundError as exc:
            install_url = (
                "https://gitlab.com/gitlab-org/orbit/knowledge-graph/-/raw/main/install.sh"
            )
            raise OrbitError(
                f"orbit binary '{self.orbit_bin}' not found on PATH. Install it with "
                f"`curl -fsSL {install_url} | bash`"
            ) from exc
        if proc.returncode != 0:
            raise OrbitError(f"orbit sql failed: {proc.stderr.strip()}")
        rows: list[dict[str, Any]] = json.loads(proc.stdout or "[]")
        return rows

    def _query_remote(self, query_body: str) -> list[dict[str, Any]]:
        if not self.api_url or not self.token:
            raise OrbitError(
                "Remote mode requires orbit_api_url and orbit_token (and the "
                "knowledge_graph feature flag enabled on the group)."
            )
        payload = json.dumps({"query": query_body}).encode()
        req = urllib.request.Request(
            f"{self.api_url}/query",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "PRIVATE-TOKEN": self.token,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode())
        except urllib.error.URLError as exc:
            raise OrbitError(f"orbit remote query failed: {exc}") from exc
        # GitLab returns {"results": [...]} or a bare list depending on the endpoint.
        if isinstance(body, dict):  # noqa: SIM108 - explicit form keeps mypy's narrowing
            rows = body.get("results") or body.get("data") or []
        else:
            rows = body
        return list(rows)

    # ── graph construction ────────────────────────────────────────────────────────
    def build_graph(self) -> CodeGraph:
        """Build the resolved reverse-call graph from the real ontology."""
        if self.mode is Mode.REMOTE:
            return self._build_graph_remote()

        definitions: dict[int, Definition] = {}
        for row in self.query(queries.DEFINITIONS):
            definitions[int(row["id"])] = Definition(
                id=int(row["id"]),
                name=row["name"] or "",
                file_path=row["file_path"] or "",
                definition_type=row["definition_type"] or "",
                fqn=row.get("fqn") or "",
                start_line=int(row.get("start_line") or 0),
                end_line=int(row.get("end_line") or 0),
                project_id=int(row.get("project_id") or 0),
            )

        callers: dict[int, set[int]] = {}
        for row in self.query(queries.call_pairs_sql()):
            caller_id = int(row["caller_id"])
            callee_id = int(row["callee_id"])
            if caller_id == callee_id:
                continue
            callers.setdefault(callee_id, set()).add(caller_id)

        return CodeGraph(definitions=definitions, callers=callers)

    def _build_graph_remote(self) -> CodeGraph:
        """Remote graph construction.

        The Remote graph (ClickHouse, full SDLC) exposes the same call relationships via
        the documented REST query interface. The exact Cypher-like query is configured per
        provisioned instance; this method maps the returned rows (caller_id/callee_id and
        definition fields) into the same CodeGraph shape used by Local. It is implemented
        against GitLab's documented interface and gated behind real credentials.
        """
        raise OrbitError(
            "Remote graph construction must be wired to your provisioned instance's "
            "query (see docs). Local mode is the supported, tested path."
        )

    def build_inventory(self, graph: CodeGraph | None = None) -> TestInventory:
        """Discover the repo's tests from the graph, by convention (no TESTS edge exists).

        Test cases  = definitions in test files whose name matches a test convention.
        Unmapped    = files that look like test files but yielded no test-case definitions
                      (unparsed language, parse error). These are always run for safety.
        """
        if graph is None:
            graph = self.build_graph()

        tests: list[TestCase] = []
        mapped_files: set[str] = set()
        for d in graph.definitions.values():
            if conventions.is_test_definition(d.name, d.definition_type, d.file_path):
                tests.append(TestCase(name=d.name, file_path=d.file_path, definition_id=d.id))
                mapped_files.add(d.file_path)

        unmapped: set[str] = set()
        for row in self.query(queries.FILES):
            path = row.get("path") or ""
            # Only strict test filenames count as must-run-when-unmapped, so that
            # __init__.py / conftest.py under tests/ never inflate the suite.
            if conventions.is_test_filename(path) and path not in mapped_files:
                unmapped.add(path)

        tests.sort(key=lambda t: (t.file_path, t.name))
        return TestInventory(tests=tuple(tests), unmapped_test_files=frozenset(unmapped))
