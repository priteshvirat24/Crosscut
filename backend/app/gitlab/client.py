"""GitLab API client for MR operations, issue creation, and project data."""

from __future__ import annotations

from typing import Any

import httpx
import structlog

from app.config import get_settings

logger = structlog.get_logger()


class GitLabClient:
    """Async client for the GitLab REST API v4."""

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = f"{settings.gitlab_url}/api/v4"
        self.token = settings.gitlab_token
        self.timeout = 30.0
        self._headers = {
            "PRIVATE-TOKEN": self.token,
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict | list:
        """Make an authenticated API request."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method,
                f"{self.base_url}{path}",
                headers=self._headers,
                **kwargs,
            )
            response.raise_for_status()
            return response.json()

    # ── Merge Requests ────────────────────────────────────────────────────

    async def get_mr(self, project_id: int, mr_iid: int) -> dict:
        """Get merge request details."""
        return await self._request("GET", f"/projects/{project_id}/merge_requests/{mr_iid}")

    async def get_mr_diff(self, project_id: int, mr_iid: int) -> str:
        """Get the diff content for a merge request."""
        changes = await self._request(
            "GET", f"/projects/{project_id}/merge_requests/{mr_iid}/changes"
        )
        # Build unified diff from changes
        diff_parts = []
        for change in changes.get("changes", []):
            diff_parts.append(change.get("diff", ""))
        return "\n".join(diff_parts)

    async def add_mr_comment(
        self,
        project_id: int,
        mr_iid: int,
        body: str,
    ) -> dict:
        """Add a comment to a merge request."""
        return await self._request(
            "POST",
            f"/projects/{project_id}/merge_requests/{mr_iid}/notes",
            json={"body": body},
        )

    # ── Issues ────────────────────────────────────────────────────────────

    async def create_issue(
        self,
        project_id: int,
        title: str,
        description: str,
        labels: list[str] | None = None,
        assignee_ids: list[int] | None = None,
    ) -> dict:
        """Create a new issue in a project."""
        data: dict[str, Any] = {
            "title": title,
            "description": description,
        }
        if labels:
            data["labels"] = ",".join(labels)
        if assignee_ids:
            data["assignee_ids"] = assignee_ids

        return await self._request(
            "POST",
            f"/projects/{project_id}/issues",
            json=data,
        )

    # ── Projects ──────────────────────────────────────────────────────────

    async def get_project(self, project_id: int) -> dict:
        """Get project details."""
        return await self._request("GET", f"/projects/{project_id}")

    async def search_projects(self, search: str) -> list:
        """Search for projects by name."""
        return await self._request("GET", f"/projects?search={search}")

    # ── Members ───────────────────────────────────────────────────────────

    async def get_project_members(self, project_id: int) -> list:
        """Get project members (for ownership detection)."""
        return await self._request("GET", f"/projects/{project_id}/members/all")
