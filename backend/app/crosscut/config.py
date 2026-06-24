"""Configuration — loaded once, at the edge, from the environment.

No other module reads os.environ directly. Sensible defaults make the Local path work
with zero configuration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from app.crosscut.models import Mode


@dataclass(frozen=True)
class CrosscutConfig:
    # Orbit
    orbit_mode: Mode = Mode.LOCAL
    orbit_bin: str = "orbit"
    orbit_db_path: str | None = None
    orbit_api_url: str | None = None
    orbit_token: str | None = None

    # GitLab (for posting the MR comment / triggering the pipeline)
    gitlab_url: str = "https://gitlab.com"
    gitlab_token: str | None = None
    project_id: str | None = None
    mr_iid: str | None = None

    # Test runner / generated child pipeline
    test_command: str = "pytest"
    ci_image: str | None = None
    ci_before_script: tuple[str, ...] = ()

    @classmethod
    def from_env(cls) -> CrosscutConfig:
        mode_raw = os.environ.get("CROSSCUT_ORBIT_MODE", "local").strip().lower()
        mode = Mode.REMOTE if mode_raw == "remote" else Mode.LOCAL
        return cls(
            orbit_mode=mode,
            orbit_bin=os.environ.get("CROSSCUT_ORBIT_BIN", "orbit"),
            orbit_db_path=os.environ.get("CROSSCUT_ORBIT_DB") or None,
            orbit_api_url=os.environ.get("CROSSCUT_ORBIT_API_URL") or None,
            orbit_token=os.environ.get("CROSSCUT_ORBIT_TOKEN") or None,
            gitlab_url=os.environ.get("CI_SERVER_URL", "https://gitlab.com"),
            gitlab_token=os.environ.get("CROSSCUT_GITLAB_TOKEN")
            or os.environ.get("GITLAB_TOKEN")
            or None,
            project_id=os.environ.get("CI_PROJECT_ID") or None,
            mr_iid=os.environ.get("CI_MERGE_REQUEST_IID") or None,
            test_command=os.environ.get("CROSSCUT_TEST_COMMAND", "pytest"),
            ci_image=os.environ.get("CROSSCUT_CI_IMAGE") or None,
            ci_before_script=tuple(
                s for s in os.environ.get("CROSSCUT_CI_BEFORE_SCRIPT", "").split("\n") if s
            ),
        )
