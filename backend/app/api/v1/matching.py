"""Job matching and explainability API routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.jobs import JobListing, JobMatch
from app.services.matching.engine import MatchingEngine
from app.schemas.jobs import JobMatchResponse, JobMatchListResponse

router = APIRouter(prefix="/matching", tags=["Job Matching"])
matching_engine = MatchingEngine()


@router.post("/run", response_model=list[JobMatchResponse])
async def run_matching(
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run the multi-stage matching pipeline against recent jobs in the database."""
    # Find active listings
    listings_res = await db.execute(
        select(JobListing.id)
        .where(JobListing.is_active == True)
        .order_by(JobListing.id.desc())
        .limit(limit)
    )
    listing_ids = [row[0] for row in listings_res.all()]

    if not listing_ids:
        return []

    try:
        await matching_engine.match_jobs(
            user_id=current_user.id,
            listing_ids=listing_ids,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Retrieve stored matches with listing details
    matches_res = await db.execute(
        select(JobMatch)
        .where(JobMatch.user_id == current_user.id)
        .options(selectinload(JobMatch.listing))
        .order_by(JobMatch.overall_score.desc())
        .limit(limit)
    )
    return matches_res.scalars().all()


@router.get("/recommendations", response_model=JobMatchListResponse)
async def get_match_recommendations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    min_score: float = Query(0.0, ge=0.0, le=100.0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get stored job match recommendations for the current user."""
    query = (
        select(JobMatch)
        .where(
            JobMatch.user_id == current_user.id,
            JobMatch.overall_score >= min_score,
        )
        .options(selectinload(JobMatch.listing))
        .order_by(JobMatch.overall_score.desc())
    )

    offset = (page - 1) * page_size
    results = await db.execute(query.offset(offset).limit(page_size))
    matches = results.scalars().all()

    # Total count
    from sqlalchemy import func
    count_res = await db.execute(
        select(func.count(JobMatch.id)).where(
            JobMatch.user_id == current_user.id,
            JobMatch.overall_score >= min_score,
        )
    )
    total = count_res.scalar() or 0

    return JobMatchListResponse(
        matches=matches,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/job/{listing_id}", response_model=JobMatchResponse)
async def get_job_match(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get or compute the match and evidence explanation for a specific job."""
    res = await db.execute(
        select(JobMatch)
        .where(
            JobMatch.user_id == current_user.id,
            JobMatch.listing_id == listing_id,
        )
        .options(selectinload(JobMatch.listing))
    )
    match = res.scalar_one_or_none()

    if not match:
        # Compute match on the fly
        try:
            await matching_engine.match_jobs(
                user_id=current_user.id,
                listing_ids=[listing_id],
                db=db,
            )
            res = await db.execute(
                select(JobMatch)
                .where(
                    JobMatch.user_id == current_user.id,
                    JobMatch.listing_id == listing_id,
                )
                .options(selectinload(JobMatch.listing))
            )
            match = res.scalar_one_or_none()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    if not match:
        raise HTTPException(status_code=404, detail="Job match could not be computed")

    return match
