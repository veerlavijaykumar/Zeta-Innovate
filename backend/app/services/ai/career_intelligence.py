"""Career intelligence service - AI-powered career recommendations."""
from datetime import datetime, timezone
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.services.ai.base import AIService
from app.models.profile import CandidateProfile
import structlog

logger = structlog.get_logger()

CAREER_ANALYSIS_PROMPT = """You are an expert career counselor and job market analyst. 
Analyze the candidate's profile and recommend suitable career paths.

RULES:
- Base recommendations ONLY on the candidate's actual skills, experience, projects, and education
- Do NOT assume skills or experience not evidenced in the profile
- Clearly mark uncertain conclusions with low confidence
- Be honest about gaps and missing qualifications
- Do NOT predict employment success or guarantee interviews
- Consider the Indian and global tech job market
- Provide actionable, specific recommendations

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
            "confidence": "low|medium|high"
        }
    ],
    "profile_summary": "Brief summary of candidate's profile strengths",
    "overall_readiness": "A candid assessment of job-market readiness",
    "warnings": ["Any concerns or caveats about the recommendations"]
}"""

CAREER_COMPARISON_PROMPT = """Compare the following career roles for the given candidate profile.
For each role, evaluate fit based on the candidate's actual skills and experience.

RULES:
- Use only evidence from the profile
- Don't fabricate qualifications
- Be honest about gaps
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
    """AI-powered career analysis and recommendation engine."""

    def __init__(self):
        self.ai = AIService()

    def _profile_to_text(self, profile: CandidateProfile) -> str:
        """Convert profile to structured text for AI analysis."""
        parts = []

        if profile.headline:
            parts.append(f"Headline: {profile.headline}")
        if profile.summary:
            parts.append(f"Summary: {profile.summary}")
        if profile.current_role:
            parts.append(f"Current Role: {profile.current_role}")
        if profile.current_company:
            parts.append(f"Current Company: {profile.current_company}")
        if profile.total_experience_years:
            parts.append(f"Total Experience: {profile.total_experience_years} years")
        if profile.education_level:
            parts.append(f"Education Level: {profile.education_level}")
        if profile.location:
            parts.append(f"Location: {profile.location}")

        # Skills
        if profile.skills:
            skill_list = [f"- {s.name} ({s.category or 'general'}, {s.proficiency_level or 'unknown level'})" for s in profile.skills]
            parts.append(f"\nSkills:\n" + "\n".join(skill_list))

        # Experience
        if profile.experiences:
            exp_list = []
            for exp in profile.experiences:
                exp_text = f"- {exp.title} at {exp.company}"
                if exp.start_date:
                    exp_text += f" ({exp.start_date} - {exp.end_date or 'Present'})"
                if exp.description:
                    exp_text += f"\n  {exp.description[:300]}"
                if exp.technologies:
                    exp_text += f"\n  Technologies: {', '.join(exp.technologies)}"
                exp_list.append(exp_text)
            parts.append(f"\nWork Experience:\n" + "\n".join(exp_list))

        # Projects
        if profile.projects:
            proj_list = []
            for proj in profile.projects:
                proj_text = f"- {proj.name}"
                if proj.description:
                    proj_text += f": {proj.description[:200]}"
                if proj.technologies:
                    proj_text += f"\n  Technologies: {', '.join(proj.technologies)}"
                proj_list.append(proj_text)
            parts.append(f"\nProjects:\n" + "\n".join(proj_list))

        # Education
        if profile.education:
            edu_list = [f"- {e.degree} in {e.field_of_study or 'N/A'} from {e.institution}" for e in profile.education]
            parts.append(f"\nEducation:\n" + "\n".join(edu_list))

        # Certifications
        if profile.certifications:
            cert_list = [f"- {c.name} ({c.issuing_organization or 'N/A'})" for c in profile.certifications]
            parts.append(f"\nCertifications:\n" + "\n".join(cert_list))

        return "\n".join(parts)

    async def analyze_career(
        self,
        user_id: int,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Generate career recommendations based on profile."""
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
        prompt = f"Analyze this candidate's profile and recommend suitable career paths:\n\n{profile_text}"

        analysis = await self.ai.generate_json(
            prompt=prompt,
            system_instruction=CAREER_ANALYSIS_PROMPT,
        )

        # Add metadata
        analysis["generated_at"] = datetime.now(timezone.utc).isoformat()

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
