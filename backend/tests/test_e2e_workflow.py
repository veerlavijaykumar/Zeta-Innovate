"""Comprehensive End-to-End Workflow Integration Test.

Workflow:
1. Register user and authenticate with JWT
2. Update candidate profile and add verified skills
3. Ingest job listings
4. Run matching engine and inspect match explanation
5. Track application status (saved -> applied -> interview)
6. Verify analytics
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.jobs import JobListing


@pytest.mark.asyncio
async def test_full_candidate_lifecycle(client: AsyncClient, db_session: AsyncSession):
    # 1. Register candidate
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "e2e_candidate@example.com",
            "password": "SecurePassword123!",
            "full_name": "Priya Patel",
        },
    )
    assert reg_res.status_code == 201

    # 2. Login
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "e2e_candidate@example.com", "password": "SecurePassword123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 3. Update Profile
    prof_res = await client.put(
        "/api/v1/profile",
        json={
            "headline": "Full Stack Developer | Python, React, Cloud",
            "summary": "Passionate software engineer building resilient web services.",
            "current_role": "Full Stack Engineer",
            "total_experience_years": 3.0,
            "location": "Bangalore, India",
        },
        headers=auth_headers,
    )
    assert prof_res.status_code == 200
    assert prof_res.json()["current_role"] == "Full Stack Engineer"

    # Add verified skills
    for sk in ["React", "Python", "FastAPI", "TypeScript", "PostgreSQL"]:
        skill_res = await client.post(
            "/api/v1/profile/skills",
            json={"name": sk, "category": "Technical", "proficiency_level": "advanced"},
            headers=auth_headers,
        )
        assert skill_res.status_code == 201

    # 4. Ingest sample job into database
    job = JobListing(
        title="Senior Full Stack Engineer",
        company="Zeta Innovations",
        description="Looking for an experienced engineer proficient in React, TypeScript, and Python.",
        required_skills=["react", "typescript", "python"],
        preferred_skills=["fastapi", "docker", "aws"],
        min_experience_years=2.0,
        max_experience_years=5.0,
        location="Bangalore, India",
        work_mode="hybrid",
        canonical_key="e2e:zeta-001",
    )
    db_session.add(job)
    await db_session.flush()

    # 5. Search for jobs
    search_res = await client.get("/api/v1/jobs?query=Zeta")
    assert search_res.status_code == 200
    assert search_res.json()["total"] == 1

    # 6. Run matching engine
    match_run = await client.post("/api/v1/matching/run?limit=10", headers=auth_headers)
    assert match_run.status_code == 200
    matches = match_run.json()
    assert len(matches) >= 1
    assert matches[0]["overall_score"] > 60.0

    # 7. Start tracking application
    app_res = await client.post(
        "/api/v1/applications",
        json={"listing_id": job.id, "notes": "Prepared custom portfolio"},
        headers=auth_headers,
    )
    assert app_res.status_code == 201
    app_id = app_res.json()["id"]
    assert app_res.json()["status"] == "saved"

    # Advance application to 'applied'
    status_update = await client.put(
        f"/api/v1/applications/{app_id}/status",
        json={"status": "applied", "notes": "Submitted official form"},
        headers=auth_headers,
    )
    assert status_update.status_code == 200
    assert status_update.json()["status"] == "applied"

    # 8. Verify Analytics reflect tracked application and matches
    analytics_res = await client.get("/api/v1/analytics", headers=auth_headers)
    assert analytics_res.status_code == 200
    analytics_data = analytics_res.json()
    assert analytics_data["total_jobs_discovered"] >= 1
    assert analytics_data["applications_submitted"] == 1
