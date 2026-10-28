"""Application Tracking API routes."""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.jobs import JobListing
from app.models.application import Application, ApplicationStatusHistory
from app.schemas.application import (
    ApplicationCreate,
    ApplicationStatusUpdate,
    ApplicationResponse,
    ApplicationListResponse,
)

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("", response_model=ApplicationListResponse)
async def list_applications(
    status_filter: Optional[str] = Query(None, description="Filter by application status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List tracked job applications with status history."""
    query = (
        select(Application)
        .where(Application.user_id == current_user.id)
        .options(
            selectinload(Application.status_history),
            selectinload(Application.listing),
        )
        .order_by(Application.updated_at.desc())
    )

    if status_filter:
        query = query.where(Application.status == status_filter)

    count_query = select(func.count(Application.id)).where(Application.user_id == current_user.id)
    if status_filter:
        count_query = count_query.where(Application.status == status_filter)
    total = (await db.execute(count_query)).scalar() or 0

    offset = (page - 1) * page_size
    results = await db.execute(query.offset(offset).limit(page_size))
    apps = results.scalars().all()

    return ApplicationListResponse(
        applications=apps,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start tracking an application for a specific job listing."""
    # Check if job exists
    job_res = await db.execute(select(JobListing).where(JobListing.id == data.listing_id))
    job = job_res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job listing not found")

    # Check if already tracking
    existing = await db.execute(
        select(Application).where(
            Application.user_id == current_user.id,
            Application.listing_id == data.listing_id,
        )
    )
    app = existing.scalar_one_or_none()
    if app:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Application for this job is already tracked.",
        )

    app = Application(
        user_id=current_user.id,
        listing_id=data.listing_id,
        status="saved",
        company_name=job.company,
        job_title=job.title,
        source_url=job.source_url,
        apply_url=job.apply_url,
        notes=data.notes,
    )
    db.add(app)
    await db.flush()

    # Log initial status history
    history = ApplicationStatusHistory(
        application_id=app.id,
        from_status=None,
        to_status="saved",
        notes="Tracked application created",
    )
    db.add(history)
    await db.flush()
    await db.refresh(app)

    res = await db.execute(
        select(Application)
        .where(Application.id == app.id)
        .options(selectinload(Application.status_history))
    )
    return res.scalar_one()


@router.put("/{app_id}/status", response_model=ApplicationResponse)
async def update_application_status(
    app_id: int,
    data: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update application stage (e.g. applied, interview, offer) and record status history."""
    res = await db.execute(
        select(Application).where(
            Application.id == app_id,
            Application.user_id == current_user.id,
        )
    )
    app = res.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    old_status = app.status
    app.status = data.status

    if data.status == "applied" and not app.applied_at:
        app.applied_at = datetime.now(timezone.utc)
    if data.notes:
        app.notes = data.notes
    if data.next_step:
        app.next_step = data.next_step
    if data.next_step_date:
        app.next_step_date = data.next_step_date

    # Add audit log
    history = ApplicationStatusHistory(
        application_id=app.id,
        from_status=old_status,
        to_status=data.status,
        notes=data.notes,
    )
    db.add(history)

    await db.flush()
    await db.refresh(app)

    updated = await db.execute(
        select(Application)
        .where(Application.id == app.id)
        .options(selectinload(Application.status_history))
    )
    return updated.scalar_one()


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a tracked application."""
    res = await db.execute(
        select(Application).where(
            Application.id == app_id,
            Application.user_id == current_user.id,
        )
    )
    app = res.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    await db.delete(app)
