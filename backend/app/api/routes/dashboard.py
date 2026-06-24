"""Dashboard data endpoints."""

from __future__ import annotations

from sqlalchemy import select, func

from fastapi import APIRouter

from app.api.deps import SessionDep
from app.models.analysis import Analysis
from app.schemas import (
    AnalysisResponse,
    DashboardOverview,
    OverviewStats,
    RiskDistribution,
)

router = APIRouter()


@router.get("/dashboard/overview", response_model=DashboardOverview)
async def get_dashboard_overview(session: SessionDep) -> DashboardOverview:
    """Get complete dashboard overview with stats, risk distribution, and recent analyses."""

    # Total analyses
    total_result = await session.execute(select(func.count(Analysis.id)))
    total = total_result.scalar() or 0

    # Active analyses
    active_result = await session.execute(
        select(func.count(Analysis.id)).where(
            Analysis.status.in_(["pending", "running"])
        )
    )
    active = active_result.scalar() or 0

    # Unique repos protected
    repos_result = await session.execute(
        select(func.count(func.distinct(Analysis.project_name))).where(
            Analysis.status == "completed"
        )
    )
    repos_protected = repos_result.scalar() or 0

    # Breakages prevented (completed analyses with risk_score > 50)
    prevented_result = await session.execute(
        select(func.count(Analysis.id)).where(
            Analysis.status == "completed",
            Analysis.risk_score > 50,
        )
    )
    breakages_prevented = prevented_result.scalar() or 0

    # Average scores
    avg_result = await session.execute(
        select(
            func.avg(Analysis.risk_score),
            func.avg(Analysis.blast_radius_score),
        ).where(Analysis.status == "completed")
    )
    row = avg_result.one_or_none()
    avg_risk = round(float(row[0] or 0), 1) if row else 0.0
    avg_blast = round(float(row[1] or 0), 1) if row else 0.0

    # Risk distribution
    risk_dist = RiskDistribution()
    for category in ["critical", "high", "medium", "low"]:
        count_result = await session.execute(
            select(func.count(Analysis.id)).where(
                Analysis.risk_category == category,
                Analysis.status == "completed",
            )
        )
        setattr(risk_dist, category, count_result.scalar() or 0)

    # Recent analyses
    recent_result = await session.execute(
        select(Analysis)
        .order_by(Analysis.created_at.desc())
        .limit(10)
    )
    recent = recent_result.scalars().all()

    return DashboardOverview(
        stats=OverviewStats(
            total_analyses=total,
            active_analyses=active,
            repos_protected=repos_protected,
            breakages_prevented=breakages_prevented,
            avg_risk_score=avg_risk,
            avg_blast_radius=avg_blast,
            prediction_accuracy=87.5,  # TODO: Calculate from prediction_history
        ),
        risk_distribution=risk_dist,
        recent_analyses=[
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
            for a in recent
        ],
    )
