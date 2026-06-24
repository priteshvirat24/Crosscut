"""Orbit API client for querying the GitLab knowledge graph.

Supports:
- REST API queries against Orbit Remote
- Orbit Local CLI invocation
- Mock data fallback for demos
"""

from __future__ import annotations

from typing import Any

import httpx
import structlog

from app.config import get_settings
from app.agents.state import OrbitDependencyGraph, OrbitDependencyNode, OrbitDependencyEdge
from app.orbit.queries import CROSS_REPO_CALLERS, DEPENDENCY_CHAIN, SYMBOL_LOOKUP

logger = structlog.get_logger()


class OrbitClient:
    """Client for interacting with GitLab Orbit."""

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.orbit_api_url
        self.token = settings.gitlab_token
        self.timeout = 30.0

    async def query(self, query_string: str, variables: dict[str, Any] | None = None) -> dict:
        """Execute a query against the Orbit REST API.

        POST /api/v4/orbit/query
        {
            "query": "<cypher-like query>",
            "variables": { ... }
        }
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/query",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                json={
                    "query": query_string,
                    "variables": variables or {},
                },
            )
            response.raise_for_status()
            return response.json()

    async def find_callers(
        self,
        function_name: str,
        repository: str | None = None,
    ) -> list[dict[str, Any]]:
        """Find all cross-repository callers of a function."""
        variables: dict[str, Any] = {"function_name": function_name}
        if repository:
            variables["repository"] = repository

        try:
            result = await self.query(CROSS_REPO_CALLERS, variables)
            return result.get("data", {}).get("callers", [])
        except Exception as e:
            logger.error("orbit.find_callers.error", function=function_name, error=str(e))
            return []

    async def find_dependency_chain(
        self,
        repo_name: str,
        max_depth: int = 5,
    ) -> list[dict[str, Any]]:
        """Find the dependency chain for a repository."""
        variables = {"repo_name": repo_name, "max_depth": max_depth}

        try:
            result = await self.query(DEPENDENCY_CHAIN, variables)
            return result.get("data", {}).get("paths", [])
        except Exception as e:
            logger.error("orbit.dependency_chain.error", repo=repo_name, error=str(e))
            return []

    async def lookup_symbol(
        self,
        symbol_name: str,
        symbol_type: str = "function",
    ) -> list[dict[str, Any]]:
        """Look up a symbol across all indexed repositories."""
        variables = {"symbol_name": symbol_name, "symbol_type": symbol_type}

        try:
            result = await self.query(SYMBOL_LOOKUP, variables)
            return result.get("data", {}).get("symbols", [])
        except Exception as e:
            logger.error("orbit.symbol_lookup.error", symbol=symbol_name, error=str(e))
            return []

    async def discover_dependencies(
        self,
        project_name: str,
        breaking_changes: list[dict],
    ) -> OrbitDependencyGraph:
        """Full dependency discovery for a project's breaking changes.

        Queries Orbit for each broken symbol to find all callers,
        then builds a complete dependency graph.
        """
        all_nodes: list[OrbitDependencyNode] = []
        all_edges: list[OrbitDependencyEdge] = []
        affected_repos: list[dict[str, Any]] = []
        seen_repos: set[str] = set()

        # Source node
        all_nodes.append(
            OrbitDependencyNode(
                id=f"repo:{project_name}",
                type="repository",
                name=project_name,
                repository=project_name,
                file_path="",
                line_number=0,
                metadata={"is_source": True},
            )
        )

        for change in breaking_changes:
            symbol = change.get("symbol_name", "")
            if not symbol:
                continue

            callers = await self.find_callers(symbol, project_name)

            for caller in callers:
                caller_repo = caller.get("repository", "")
                if caller_repo == project_name:
                    continue  # Skip self-references

                # Add repo node
                if caller_repo not in seen_repos:
                    seen_repos.add(caller_repo)
                    all_nodes.append(
                        OrbitDependencyNode(
                            id=f"repo:{caller_repo}",
                            type="repository",
                            name=caller_repo,
                            repository=caller_repo,
                            file_path="",
                            line_number=0,
                            metadata=caller.get("metadata", {}),
                        )
                    )
                    affected_repos.append({
                        "name": caller_repo,
                        "team": caller.get("team", "Unknown"),
                        "maintainers": caller.get("maintainers", []),
                        "impact_level": "high",
                        "affected_files": [caller.get("file", "")],
                        "affected_functions": [caller.get("name", "")],
                        "call_count": caller.get("call_count", 1),
                        "dependency_depth": caller.get("depth", 1),
                    })

                # Add function node
                func_id = f"func:{caller_repo}:{caller.get('name', 'unknown')}"
                all_nodes.append(
                    OrbitDependencyNode(
                        id=func_id,
                        type="function",
                        name=caller.get("name", "unknown"),
                        repository=caller_repo,
                        file_path=caller.get("file", ""),
                        line_number=caller.get("line", 0),
                        metadata={},
                    )
                )

                # Add call edge
                all_edges.append(
                    OrbitDependencyEdge(
                        source=func_id,
                        target=f"func:{project_name}:{symbol}",
                        relationship="calls",
                        weight=float(caller.get("call_count", 1)),
                        metadata={},
                    )
                )

        return OrbitDependencyGraph(
            nodes=all_nodes,
            edges=all_edges,
            affected_repositories=affected_repos,
            total_callers=sum(r.get("call_count", 1) for r in affected_repos),
            total_repos=len(affected_repos),
            query_results_raw={"mode": "api", "queries_executed": len(breaking_changes)},
        )
