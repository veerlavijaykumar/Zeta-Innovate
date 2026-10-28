"""Unit tests for the multi-stage matching engine."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.profile import CandidateProfile, CandidateSkill
from app.models.jobs import JobListing
from app.services.matching.engine import MatchingEngine
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_matching_engine_computation(db_session: AsyncSession):
    engine = MatchingEngine()

    # Create candidate
    user = User(
        email="dev@example.com",
        hashed_password=get_password_hash("Secret123!"),
        full_name="Software Candidate",
    )
    db_session.add(user)
    await db_session.flush()

    profile = CandidateProfile(
        user_id=user.id,
        current_role="Backend Developer",
        total_experience_years=3.0,
    )
    db_session.add(profile)
    await db_session.flush()

    # Add skills
    for skill in ["python", "fastapi", "postgresql", "docker"]:
        db_session.add(CandidateSkill(
            profile_id=profile.id,
            name=skill,
            normalized_name=skill,
            is_verified=True,
            evidence="Worked on production APIs",
        ))

    # Create job listing
    job = JobListing(
        title="Python Backend Engineer",
        company="TechCorp",
        required_skills=["python", "fastapi", "postgresql"],
        preferred_skills=["docker", "aws"],
        min_experience_years=2.0,
        max_experience_years=5.0,
        work_mode="remote",
        canonical_key="test:job-1",
    )
    db_session.add(job)
    await db_session.flush()

    # Execute matching
    matches = await engine.match_jobs(
        user_id=user.id,
        listing_ids=[job.id],
        db=db_session,
    )

    assert len(matches) == 1
    match = matches[0]
    assert match["overall_score"] > 65.0
    assert match["is_eligible"] is True
    assert "python" in match["matched_skills"]
    assert "fastapi" in match["matched_skills"]
    assert "postgresql" in match["matched_skills"]
    assert len(match["evidence"]) >= 3
