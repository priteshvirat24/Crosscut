"""GitLab webhook receiver."""

from __future__ import annotations

import hashlib
import hmac

import structlog
from fastapi import APIRouter, HTTPException, Header, Request

from app.api.deps import SettingsDep, SessionDep
from app.schemas import WebhookMergeRequest, AnalysisCreate

logger = structlog.get_logger()
router = APIRouter()


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str,
) -> bool:
    """Verify GitLab webhook signature."""
    if not secret:
        return True  # No secret configured — skip verification
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


@router.post("/webhooks/gitlab")
async def receive_gitlab_webhook(
    request: Request,
    session: SessionDep,
    settings: SettingsDep,
    x_gitlab_token: str = Header(default=""),
    x_gitlab_event: str = Header(default=""),
) -> dict:
    """Receive and process GitLab webhook events."""
    body = await request.body()

    # Verify webhook token
    if settings.gitlab_webhook_secret:
        if x_gitlab_token != settings.gitlab_webhook_secret:
            raise HTTPException(status_code=401, detail="Invalid webhook token")

    logger.info("webhook.received", event=x_gitlab_event, size=len(body))

    # Only process merge request events
    if x_gitlab_event not in ("Merge Request Hook", "merge_request"):
        return {"status": "ignored", "reason": f"Event type '{x_gitlab_event}' not handled"}

    try:
        payload = WebhookMergeRequest.model_validate_json(body)
    except Exception as e:
        logger.error("webhook.parse_error", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    # Only analyze on open/update actions
    action = payload.object_attributes.action
    if action not in ("open", "reopen", "update"):
        return {"status": "ignored", "reason": f"Action '{action}' not handled"}

    # Trigger analysis
    from app.api.routes.analyses import create_analysis

    analysis_request = AnalysisCreate(
        project_id=payload.project.id,
        mr_iid=payload.object_attributes.iid,
        project_name=payload.project.path_with_namespace,
    )

    result = await create_analysis(analysis_request, session, settings)

    logger.info(
        "webhook.analysis_triggered",
        analysis_id=result.id,
        project=payload.project.path_with_namespace,
        mr_iid=payload.object_attributes.iid,
    )

    return {
        "status": "accepted",
        "analysis_id": result.id,
        "project": payload.project.path_with_namespace,
        "mr_iid": payload.object_attributes.iid,
    }
