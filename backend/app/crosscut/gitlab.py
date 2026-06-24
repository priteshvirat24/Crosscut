"""GitLab REST helpers — posting the MR comment. Real HTTP, no mocks.

Only invoked when a token + project + MR are configured (i.e. running inside CI on a real
MR). The targeted child pipeline itself is triggered by GitLab's dynamic child-pipeline
mechanism (the parent emits the YAML as an artifact and a trigger job includes it), so no
pipeline-trigger API call is needed here.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.crosscut.config import CrosscutConfig


class GitLabError(RuntimeError):
    pass


def post_mr_note(config: CrosscutConfig, body: str) -> dict[str, Any]:
    """Post (or could be extended to upsert) a note on the configured merge request."""
    if not (config.gitlab_token and config.project_id and config.mr_iid):
        raise GitLabError(
            "GitLab posting requires gitlab_token, project_id and mr_iid "
            "(set via CI variables / CI_* env)."
        )
    project = urllib.parse.quote_plus(str(config.project_id))
    url = f"{config.gitlab_url}/api/v4/projects/{project}/merge_requests/{config.mr_iid}/notes"
    data = urllib.parse.urlencode({"body": body}).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"PRIVATE-TOKEN": config.gitlab_token},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            note: dict[str, Any] = json.loads(resp.read().decode())
            return note
    except urllib.error.HTTPError as exc:
        raise GitLabError(f"GitLab API {exc.code}: {exc.read().decode()[:200]}") from exc
    except urllib.error.URLError as exc:
        raise GitLabError(f"GitLab request failed: {exc}") from exc
