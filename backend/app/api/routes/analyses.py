"""Analysis API routes — trigger, list, and inspect analyses."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

import structlog
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func, desc

from app.api.deps import SessionDep, SettingsDep
from app.models.analysis import Analysis, BreakingChange, AffectedRepository
from app.schemas import (
    AnalysisCreate,
    AnalysisResponse,
    AnalysisDetail,
    BreakingChangeResponse,
    AffectedRepoResponse,
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("/analyses", response_model=AnalysisResponse, status_code=201)
async def create_analysis(
    payload: AnalysisCreate,
    session: SessionDep,
    settings: SettingsDep,
) -> AnalysisResponse:
    """Trigger a new cross-repository impact analysis for a merge request."""
    logger.info(
        "analysis.create",
        project_id=payload.project_id,
        mr_iid=payload.mr_iid,
    )

    now = datetime.now(timezone.utc)
    analysis = Analysis(
        id=str(uuid.uuid4()),
        project_id=payload.project_id,
        project_name=payload.project_name or f"project-{payload.project_id}",
        mr_id=payload.mr_iid,  # Will be resolved via GitLab API
        mr_iid=payload.mr_iid,
        mr_title="",
        mr_url="",
        status="pending",
        created_at=now,
        updated_at=now,
    )
    session.add(analysis)
    await session.flush()

    # Trigger the agent pipeline asynchronously
    # In production: dispatch to Celery; for now, import and run inline
    try:
        from app.services.analysis_service import run_analysis_pipeline

        # Fire-and-forget (in a real system this would be a Celery task)
        import asyncio

        asyncio.create_task(run_analysis_pipeline(analysis.id))
    except ImportError:
        logger.warning("analysis_service not available, skipping pipeline trigger")

    return AnalysisResponse(
        id=analysis.id,
        project_name=analysis.project_name,
        mr_iid=analysis.mr_iid,
        mr_title=analysis.mr_title,
        mr_url=analysis.mr_url,
        status=analysis.status,
        blast_radius_score=analysis.blast_radius_score,
        risk_score=analysis.risk_score,
        risk_category=analysis.risk_category,
        affected_repos_count=analysis.affected_repos_count,
        affected_teams_count=analysis.affected_teams_count,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
    )


@router.get("/analyses", response_model=list[AnalysisResponse])
async def list_analyses(
    session: SessionDep,
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[AnalysisResponse]:
    """List analyses with optional filtering."""
    query = select(Analysis).order_by(desc(Analysis.created_at))

    if status:
        query = query.where(Analysis.status == status)

    query = query.limit(limit).offset(offset)
    result = await session.execute(query)
    analyses = result.scalars().all()

    return [
        AnalysisResponse(
            id=a.id,
            project_name=a.project_name,
            mr_iid=a.mr_iid,
            mr_title=a.mr_title,
            mr_url=a.mr_url,
            status=a.status,
            blast_radius_score=a.blast_radius_score,
            risk_score=a.risk_score,
            risk_category=a.risk_category,
            affected_repos_count=a.affected_repos_count,
            affected_teams_count=a.affected_teams_count,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )
        for a in analyses
    ]


@router.get("/analyses/{analysis_id}", response_model=AnalysisDetail)
async def get_analysis(
    analysis_id: str,
    session: SessionDep,
) -> AnalysisDetail:
    """Get full analysis detail including breaking changes and affected repos."""
    result = await session.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Load relationships
    bc_result = await session.execute(
        select(BreakingChange).where(BreakingChange.analysis_id == analysis_id)
    )
    breaking_changes = bc_result.scalars().all()

    ar_result = await session.execute(
        select(AffectedRepository).where(AffectedRepository.analysis_id == analysis_id)
    )
    affected_repos = ar_result.scalars().all()

    return AnalysisDetail(
        id=analysis.id,
        project_name=analysis.project_name,
        mr_iid=analysis.mr_iid,
        mr_title=analysis.mr_title,
        mr_url=analysis.mr_url,
        status=analysis.status,
        source_branch=analysis.source_branch,
        target_branch=analysis.target_branch,
        blast_radius_score=analysis.blast_radius_score,
        risk_score=analysis.risk_score,
        risk_category=analysis.risk_category,
        affected_repos_count=analysis.affected_repos_count,
        affected_teams_count=analysis.affected_teams_count,
        change_report=analysis.change_report,
        dependency_graph=analysis.dependency_graph,
        migration_plan=analysis.migration_plan,
        executive_summary=analysis.executive_summary,
        confidence_scores=analysis.confidence_scores,
        execution_log=analysis.execution_log,
        breaking_changes=[
            BreakingChangeResponse(
                id=bc.id,
                change_type=bc.change_type,
                symbol_name=bc.symbol_name,
                file_path=bc.file_path,
                severity=bc.severity,
                description=bc.description,
                confidence=bc.confidence,
                reasoning=bc.reasoning,
                line_number=bc.line_number,
                before_signature=bc.before_signature,
                after_signature=bc.after_signature,
            )
            for bc in breaking_changes
        ],
        affected_repos=[
            AffectedRepoResponse(
                id=ar.id,
                repo_name=ar.repo_name,
                repo_url=ar.repo_url,
                impact_level=ar.impact_level,
                affected_files=ar.affected_files,
                affected_functions=ar.affected_functions,
                call_count=ar.call_count,
                dependency_depth=ar.dependency_depth,
                team_name=ar.team_name,
                maintainers=ar.maintainers,
                migration_guide=ar.migration_guide,
                issue_url=ar.issue_url,
            )
            for ar in affected_repos
        ],
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
    )
