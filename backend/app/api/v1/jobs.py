"""Job search, details, sources, and saved jobs API routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.jobs import JobListing, JobSource
from app.models.application import SavedJob
from app.services.jobs.job_service import JobService
from app.services.jobs.base import ConnectorRegistry
from app.schemas.jobs import (
    JobSearchParams,
    JobSearchResponse,
    JobListingResponse,
    JobListingDetail,
    JobSourceResponse,
    SavedJobCreate,
    SavedJobResponse,
)

router = APIRouter(prefix="/jobs", tags=["Jobs"])
job_service = JobService()


@router.get("", response_model=JobSearchResponse)
async def search_jobs(
    query: Optional[str] = Query(None, description="Keywords in title, company, description"),
    location: Optional[str] = Query(None, description="Location search"),
    work_mode: Optional[str] = Query(None, description="remote, hybrid, onsite"),
    employment_type: Optional[str] = Query(None, description="full-time, part-time, contract"),
    min_experience: Optional[float] = Query(None),
    max_experience: Optional[float] = Query(None),
    min_salary: Optional[int] = Query(None),
    max_salary: Optional[int] = Query(None),
    source: Optional[str] = Query(None),
    sort_by: str = Query("relevance", description="relevance, date, salary"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Search for verified job listings with multi-field filters."""
    params = JobSearchParams(
        query=query,
        location=location,
        work_mode=work_mode,
        employment_type=employment_type,
        min_experience=min_experience,
        max_experience=max_experience,
        min_salary=min_salary,
        max_salary=max_salary,
        source=source,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )

    jobs, total = await job_service.search_jobs(params, db)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return JobSearchResponse(
        jobs=jobs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/sources", response_model=list[JobSourceResponse])
async def get_job_sources(db: AsyncSession = Depends(get_db)):
    """List all supported job source connectors and their sync/health status."""
    await job_service.ensure_job_sources(db)
    res = await db.execute(select(JobSource).order_by(JobSource.name))
    return res.scalars().all()


@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_external_jobs(
    query: str = Query("Software Engineer", description="Role to sync"),
    location: str = Query("India", description="Location to sync"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger job ingestion from configured connectors."""
    count = await job_service.sync_from_connectors(query=query, location=location, db=db)
    return {
        "status": "success",
        "new_listings_synced": count,
        "message": f"Successfully ingested {count} jobs from active connectors."
    }


@router.get("/saved", response_model=list[SavedJobResponse])
async def get_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all jobs bookmarked/saved by the current user."""
    res = await db.execute(
        select(SavedJob)
        .where(SavedJob.user_id == current_user.id)
        .options(selectinload(SavedJob.listing))
        .order_by(SavedJob.created_at.desc())
    )
    return res.scalars().all()


@router.post("/saved", response_model=SavedJobResponse, status_code=status.HTTP_201_CREATED)
async def save_job(
    data: SavedJobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save/bookmark a job listing."""
    # Check if job exists
    job_res = await db.execute(select(JobListing).where(JobListing.id == data.listing_id))
    job = job_res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job listing not found")

    # Check if already saved
    existing = await db.execute(
        select(SavedJob).where(
            SavedJob.user_id == current_user.id,
            SavedJob.listing_id == data.listing_id,
        )
    )
    saved = existing.scalar_one_or_none()
    if saved:
        if data.notes:
            saved.notes = data.notes
            await db.flush()
        return saved

    saved = SavedJob(
        user_id=current_user.id,
        listing_id=data.listing_id,
        notes=data.notes,
    )
    db.add(saved)
    await db.flush()
    await db.refresh(saved)

    # Reload with listing relationship
    res = await db.execute(
        select(SavedJob)
        .where(SavedJob.id == saved.id)
        .options(selectinload(SavedJob.listing))
    )
    return res.scalar_one()


@router.delete("/saved/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unsave_job(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a job from saved jobs."""
    res = await db.execute(
        select(SavedJob).where(
            SavedJob.user_id == current_user.id,
            SavedJob.listing_id == listing_id,
        )
    )
    saved = res.scalar_one_or_none()
    if not saved:
        raise HTTPException(status_code=404, detail="Saved job entry not found")
    await db.delete(saved)


@router.get("/{listing_id}", response_model=JobListingDetail)
async def get_job_detail(
    listing_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get full details for a single job listing."""
    res = await db.execute(select(JobListing).where(JobListing.id == listing_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job listing not found")
    return job
