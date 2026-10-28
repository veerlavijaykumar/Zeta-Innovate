"""Tests for job search and deduplication."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.jobs import JobListing


@pytest.mark.asyncio
async def test_job_search_filters(client: AsyncClient, db_session: AsyncSession):
    # Add sample job to test DB
    job1 = JobListing(
        title="Senior Python Architect",
        company="GlobalTech",
        description="Lead Python cloud architecture",
        location="Bangalore",
        work_mode="remote",
        employment_type="full-time",
        canonical_key="test:001",
    )
    job2 = JobListing(
        title="Frontend Specialist",
        company="UIStudio",
        description="Vue and React UI development",
        location="Delhi",
        work_mode="onsite",
        employment_type="contract",
        canonical_key="test:002",
    )
    db_session.add(job1)
    db_session.add(job2)
    await db_session.flush()

    # Search by keyword
    res = await client.get("/api/v1/jobs?query=python")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["jobs"][0]["title"] == "Senior Python Architect"

    # Search by work_mode
    res_mode = await client.get("/api/v1/jobs?work_mode=remote")
    assert res_mode.status_code == 200
    assert res_mode.json()["total"] == 1
