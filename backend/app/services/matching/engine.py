"""Job matching engine - multi-stage matching pipeline."""
from typing import Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.services.ai.base import AIService
from app.models.profile import CandidateProfile, CandidateSkill, CareerPreference
from app.models.jobs import JobListing, JobMatch
import structlog

logger = structlog.get_logger()

# Configurable scoring weights
SCORING_WEIGHTS = {
    "required_skill": 0.35,
    "preferred_skill": 0.15,
    "experience": 0.20,
    "semantic": 0.15,
    "preference": 0.15,
}

MATCHING_PROMPT = """Analyze the match between this candidate and job listing.

RULES:
- Only count skills the candidate actually has evidence for
- Do NOT assume the candidate has a skill just because it's in the job description
- Be honest about missing requirements
- Provide specific evidence from the candidate's profile for each matched skill
- Flag uncertain eligibility clearly

Return JSON:
{
    "matched_required_skills": ["skill1", "skill2"],
    "matched_preferred_skills": ["skill1"],
    "missing_required_skills": ["skill1"],
    "missing_preferred_skills": ["skill1"],
    "experience_relevance": 0.7,
    "experience_explanation": "Why experience matches or doesn't",
    "is_eligible": true,
    "eligibility_warnings": ["Warning 1"],
    "evidence": [
        {"claim": "Has Python experience", "source": "resume", "text": "Evidence text from profile"}
    ],
    "explanation": "Overall match explanation",
    "semantic_relevance": 0.75
}"""


class MatchingEngine:
    """Multi-stage job matching pipeline."""

    def __init__(self):
        self.ai = AIService()
        self.weights = SCORING_WEIGHTS.copy()

    async def match_jobs(
        self,
        user_id: int,
        listing_ids: list[int],
        db: AsyncSession,
    ) -> list[dict[str, Any]]:
        """Match candidate against multiple job listings."""
        # Load profile
        result = await db.execute(
            select(CandidateProfile)
            .where(CandidateProfile.user_id == user_id)
            .options(
                selectinload(CandidateProfile.skills),
                selectinload(CandidateProfile.experiences),
                selectinload(CandidateProfile.projects),
                selectinload(CandidateProfile.education),
            )
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise ValueError("No profile found")

        # Load preferences
        pref_result = await db.execute(
            select(CareerPreference).where(CareerPreference.user_id == user_id)
        )
        preferences = pref_result.scalar_one_or_none()

        # Load listings
        listings_result = await db.execute(
            select(JobListing).where(JobListing.id.in_(listing_ids))
        )
        listings = listings_result.scalars().all()

        matches = []
        for listing in listings:
            match = await self._match_single(profile, preferences, listing, user_id, db)
            matches.append(match)

        # Sort by overall score
        matches.sort(key=lambda m: m["overall_score"], reverse=True)
        return matches

    async def _match_single(
        self,
        profile: CandidateProfile,
        preferences: CareerPreference | None,
        listing: JobListing,
        user_id: int,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Match a single listing against the profile."""

        # STAGE 1: Quick eligibility check
        eligibility_warnings = []
        is_eligible = True

        if preferences:
            # Location check
            if preferences.preferred_locations and listing.location:
                location_match = any(
                    loc.lower() in listing.location.lower()
                    for loc in preferences.preferred_locations
                )
                if not location_match and "remote" not in (listing.work_mode or "").lower():
                    eligibility_warnings.append(f"Location '{listing.location}' not in preferred locations")

            # Work mode check
            if preferences.preferred_work_modes and listing.work_mode:
                if listing.work_mode not in preferences.preferred_work_modes:
                    eligibility_warnings.append(f"Work mode '{listing.work_mode}' not preferred")

        # Experience check
        if listing.min_experience_years and profile.total_experience_years:
            if profile.total_experience_years < listing.min_experience_years:
                eligibility_warnings.append(
                    f"Requires {listing.min_experience_years}+ years, you have {profile.total_experience_years}"
                )

        # STAGE 2: Skill matching
        candidate_skills = {s.normalized_name or s.name.lower() for s in profile.skills}
        required_skills = {s.lower() for s in (listing.required_skills or [])}
        preferred_skills = {s.lower() for s in (listing.preferred_skills or [])}

        matched_required = candidate_skills & required_skills
        missing_required = required_skills - candidate_skills
        matched_preferred = candidate_skills & preferred_skills
        missing_preferred = preferred_skills - candidate_skills

        # STAGE 3: Calculate component scores
        required_score = (len(matched_required) / max(len(required_skills), 1)) * 100
        preferred_score = (len(matched_preferred) / max(len(preferred_skills), 1)) * 100

        # Experience score
        experience_score = 50  # base
        if listing.min_experience_years and profile.total_experience_years:
            ratio = profile.total_experience_years / listing.min_experience_years
            experience_score = min(100, ratio * 70)
        elif profile.total_experience_years and profile.total_experience_years > 0:
            experience_score = 60

        # Preference score
        preference_score = 50  # base
        if preferences:
            pref_matches = 0
            pref_total = 0
            if preferences.preferred_work_modes and listing.work_mode:
                pref_total += 1
                if listing.work_mode in preferences.preferred_work_modes:
                    pref_matches += 1
            if preferences.preferred_employment_types and listing.employment_type:
                pref_total += 1
                if listing.employment_type in preferences.preferred_employment_types:
                    pref_matches += 1
            if pref_total > 0:
                preference_score = (pref_matches / pref_total) * 100

        # Semantic score (simplified - use title/skills overlap)
        semantic_score = 50
        title_words = set(listing.title.lower().split())
        if profile.current_role:
            role_words = set(profile.current_role.lower().split())
            overlap = len(title_words & role_words)
            semantic_score = min(100, 50 + overlap * 15)

        # STAGE 4: Overall score
        overall_score = (
            required_score * self.weights["required_skill"]
            + preferred_score * self.weights["preferred_skill"]
            + experience_score * self.weights["experience"]
            + semantic_score * self.weights["semantic"]
            + preference_score * self.weights["preference"]
        )

        # STAGE 5: Build explanation
        explanation_parts = []
        if matched_required:
            explanation_parts.append(f"Matches {len(matched_required)}/{len(required_skills)} required skills")
        if missing_required:
            explanation_parts.append(f"Missing required: {', '.join(list(missing_required)[:5])}")
        if matched_preferred:
            explanation_parts.append(f"Has {len(matched_preferred)} preferred skills")
        explanation = ". ".join(explanation_parts) if explanation_parts else "Relevance based on profile analysis"

        # Evidence
        evidence = []
        for skill in matched_required:
            # Find evidence from candidate skills
            for cs in profile.skills:
                if (cs.normalized_name or cs.name.lower()) == skill:
                    evidence.append({
                        "claim": f"Has {cs.name} skill",
                        "source": "resume",
                        "text": cs.evidence or f"Listed in candidate skills ({cs.source})",
                    })
                    break

        # Save match to DB
        existing = await db.execute(
            select(JobMatch).where(
                JobMatch.user_id == user_id,
                JobMatch.listing_id == listing.id,
            )
        )
        match_record = existing.scalar_one_or_none()

        match_data = {
            "user_id": user_id,
            "listing_id": listing.id,
            "overall_score": round(overall_score, 1),
            "required_skill_score": round(required_score, 1),
            "preferred_skill_score": round(preferred_score, 1),
            "experience_score": round(experience_score, 1),
            "semantic_score": round(semantic_score, 1),
            "preference_score": round(preference_score, 1),
            "is_eligible": is_eligible,
            "eligibility_warnings": eligibility_warnings,
            "matched_skills": list(matched_required | matched_preferred),
            "missing_skills": list(missing_required),
            "explanation": explanation,
            "evidence": evidence,
            "scoring_version": "v1",
        }

        if match_record:
            for key, value in match_data.items():
                setattr(match_record, key, value)
        else:
            match_record = JobMatch(**match_data)
            db.add(match_record)

        await db.flush()

        return match_data
