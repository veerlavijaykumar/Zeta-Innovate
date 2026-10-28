"""Career and Application Analytics API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.jobs import JobListing, JobMatch
from app.models.application import SavedJob, Application, LearningRoadmap
from app.schemas.application import AnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Compute comprehensive career and application analytics from verified user records."""
    # 1. Total jobs discovered in the system
    total_jobs_res = await db.execute(select(func.count(JobListing.id)))
    total_jobs = total_jobs_res.scalar() or 0

    # 2. User's high relevance matches (score >= 70)
    matches_res = await db.execute(
        select(func.count(JobMatch.id)).where(
            JobMatch.user_id == current_user.id,
            JobMatch.overall_score >= 70.0,
        )
    )
    relevant_matches = matches_res.scalar() or 0

    # 3. Saved jobs
    saved_res = await db.execute(
        select(func.count(SavedJob.id)).where(SavedJob.user_id == current_user.id)
    )
    saved_jobs = saved_res.scalar() or 0

    # 4. Applications by status
    apps_res = await db.execute(
        select(Application.status, func.count(Application.id))
        .where(Application.user_id == current_user.id)
        .group_by(Application.status)
    )
    status_counts = dict(apps_res.all())

    applied_count = status_counts.get("applied", 0) + status_counts.get("assessment", 0) + status_counts.get("interview", 0) + status_counts.get("offer", 0) + status_counts.get("rejected", 0)
    interview_count = status_counts.get("interview", 0)
    offer_count = status_counts.get("offer", 0)

    conversion_rate = None
    if applied_count > 0:
        conversion_rate = round((interview_count / applied_count) * 100, 1)

    # 5. Skill gaps extracted from computed matches
    gaps_query = await db.execute(
        select(JobMatch.missing_skills).where(
            JobMatch.user_id == current_user.id,
            JobMatch.overall_score >= 50.0,
        ).limit(30)
    )
    gap_freq: dict[str, int] = {}
    for (missing_list,) in gaps_query.all():
        if missing_list and isinstance(missing_list, list):
            for sk in missing_list:
                sk_clean = sk.title().strip()
                gap_freq[sk_clean] = gap_freq.get(sk_clean, 0) + 1

    top_skill_gaps = [
        {"skill": skill, "frequency": count}
        for skill, count in sorted(gap_freq.items(), key=lambda x: x[1], reverse=True)[:8]
    ]

    # 6. Overall learning progress
    roadmaps_res = await db.execute(
        select(func.avg(LearningRoadmap.overall_progress)).where(
            LearningRoadmap.user_id == current_user.id
        )
    )
    avg_learning = roadmaps_res.scalar() or 0.0

    # 7. Application status distribution for charts
    timeline = [
        {"stage": "Saved", "count": status_counts.get("saved", 0)},
        {"stage": "Ready to Apply", "count": status_counts.get("ready_to_apply", 0)},
        {"stage": "Applied", "count": applied_count},
        {"stage": "Interviews", "count": interview_count},
        {"stage": "Offers", "count": offer_count},
    ]

    return AnalyticsResponse(
        total_jobs_discovered=total_jobs,
        relevant_matches=relevant_matches,
        saved_jobs=saved_jobs,
        applications_submitted=applied_count,
        interviews=interview_count,
        offers=offer_count,
        conversion_rate=conversion_rate,
        skill_gaps=top_skill_gaps,
        application_timeline=timeline,
        learning_progress=round(float(avg_learning), 1),
        top_matched_roles=[],
        recent_activity=[],
    )
