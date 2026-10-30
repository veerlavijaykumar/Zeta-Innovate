"""Career intelligence service - AI-powered career recommendations."""
from datetime import datetime, timezone
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.services.ai.base import AIService
from app.models.profile import CandidateProfile
import structlog

import time

logger = structlog.get_logger()

CAREER_ANALYSIS_PROMPT = """You are an expert career counselor and job market analyst. 
Analyze the candidate's profile and recommend the top 2-3 most suitable career paths.

RULES:
- Recommend strictly the TOP 2 to 3 best matching roles based on profile evidence.
- Base recommendations ONLY on the candidate's actual skills, experience, projects, and education.
- Keep reasoning, descriptions, and recommended steps concise (max 2 sentences per field).
- Be honest about gaps and missing qualifications.
- Do NOT predict employment success or guarantee interviews.

Return a JSON object:
{
    "recommendations": [
        {
            "role_title": "Role Title",
            "fit_score": 75,
            "why_it_fits": "Specific reasoning based on profile evidence",
            "relevant_skills": ["skill1", "skill2"],
            "relevant_experience": ["experience point 1"],
            "missing_skills": ["skill that needs development"],
            "entry_level_considerations": "For entry-level candidates, considerations...",
            "recommended_next_steps": ["Step 1", "Step 2"],
            "alternative_paths": ["Alternative Role 1"],
            "confidence": "medium"
        }
    ],
    "profile_summary": "Brief 1-2 sentence summary of candidate's profile strengths",
    "overall_readiness": "A candid 1-2 sentence assessment of job-market readiness",
    "warnings": []
}"""

CAREER_COMPARISON_PROMPT = """Compare the following career roles for the given candidate profile.
For each role, evaluate fit based on the candidate's actual skills and experience.

RULES:
- Use only evidence from the profile
- Keep reasoning concise (max 2 sentences)
- Compare objectively

Return a JSON object:
{
    "roles": [
        {
            "role_title": "Role Title",
            "fit_score": 75,
            "why_it_fits": "Reasoning",
            "relevant_skills": [],
            "relevant_experience": [],
            "missing_skills": [],
            "entry_level_considerations": "...",
            "recommended_next_steps": [],
            "alternative_paths": [],
            "confidence": "medium"
        }
    ],
    "comparison_summary": "Summary comparing the roles for this candidate"
}"""


class CareerIntelligenceService:
    """AI-powered career analysis and recommendation engine with caching."""

    def __init__(self):
        self.ai = AIService()
        self._cache: dict[int, dict[str, Any]] = {}
        self._cache_ttl = 1800  # 30 minutes

    def _profile_to_text(self, profile: CandidateProfile) -> str:
        """Convert profile to structured concise text for fast AI analysis."""
        parts = []

        if profile.headline:
            parts.append(f"Headline: {profile.headline}")
        if profile.summary:
            parts.append(f"Summary: {profile.summary[:250]}")
        if profile.current_role:
            parts.append(f"Current Role: {profile.current_role}")
        if profile.total_experience_years:
            parts.append(f"Total Experience: {profile.total_experience_years} years")
        if profile.education_level:
            parts.append(f"Education: {profile.education_level}")

        # Top 25 skills
        if profile.skills:
            top_skills = [s.name for s in profile.skills[:25]]
            parts.append(f"Skills: {', '.join(top_skills)}")

        # Top 3 experiences
        if profile.experiences:
            exp_list = []
            for exp in profile.experiences[:3]:
                exp_text = f"- {exp.title} at {exp.company}"
                if exp.description:
                    exp_text += f": {exp.description[:150]}"
                if exp.technologies:
                    exp_text += f" (Tech: {', '.join(exp.technologies[:6])})"
                exp_list.append(exp_text)
            parts.append(f"Experience:\n" + "\n".join(exp_list))

        # Top 2 projects
        if profile.projects:
            proj_list = []
            for proj in profile.projects[:2]:
                p_text = f"- {proj.name}"
                if proj.description:
                    p_text += f": {proj.description[:100]}"
                proj_list.append(p_text)
            parts.append(f"Projects:\n" + "\n".join(proj_list))

        return "\n".join(parts)

    async def analyze_career(
        self,
        user_id: int,
        db: AsyncSession,
        refresh: bool = False,
    ) -> dict[str, Any]:
        """Generate or retrieve cached career recommendations based on profile."""
        now = time.time()
        if not refresh and user_id in self._cache:
            entry = self._cache[user_id]
            if now - entry["timestamp"] < self._cache_ttl:
                logger.info("Returning cached career intelligence", user_id=user_id)
                return entry["data"]

        result = await db.execute(
            select(CandidateProfile)
            .where(CandidateProfile.user_id == user_id)
            .options(
                selectinload(CandidateProfile.skills),
                selectinload(CandidateProfile.experiences),
                selectinload(CandidateProfile.projects),
                selectinload(CandidateProfile.education),
                selectinload(CandidateProfile.certifications),
            )
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise ValueError("No profile found. Please create your profile first.")

        if not profile.skills and not profile.experiences:
            raise ValueError("Profile needs at least some skills or experience for career analysis.")

        profile_text = self._profile_to_text(profile)
        prompt = f"Analyze this candidate profile and recommend suitable career paths:\n\n{profile_text}"

        analysis = await self.ai.generate_json(
            prompt=prompt,
            system_instruction=CAREER_ANALYSIS_PROMPT,
            temperature=0.1,
            max_tokens=1500,
        )

        analysis["generated_at"] = datetime.now(timezone.utc).isoformat()

        # Cache response
        self._cache[user_id] = {
            "timestamp": now,
            "data": analysis,
        }

        return analysis

    async def compare_careers(
        self,
        user_id: int,
        roles: list[str],
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Compare multiple career roles for the candidate."""
        result = await db.execute(
            select(CandidateProfile)
            .where(CandidateProfile.user_id == user_id)
            .options(
                selectinload(CandidateProfile.skills),
                selectinload(CandidateProfile.experiences),
                selectinload(CandidateProfile.projects),
                selectinload(CandidateProfile.education),
                selectinload(CandidateProfile.certifications),
            )
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise ValueError("No profile found.")

        profile_text = self._profile_to_text(profile)
        roles_text = ", ".join(roles)
        prompt = f"Compare these career roles for the candidate: {roles_text}\n\nCandidate Profile:\n{profile_text}"

        comparison = await self.ai.generate_json(
            prompt=prompt,
            system_instruction=CAREER_COMPARISON_PROMPT,
        )

        return comparison
