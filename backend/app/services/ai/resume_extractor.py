"""Resume extraction service - extracts structured profile data from resumes using AI."""
import fitz  # PyMuPDF
from datetime import datetime, timezone
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.ai.base import AIService
from app.models.profile import (
    CandidateProfile,
    CandidateSkill,
    CandidateExperience,
    CandidateProject,
    CandidateEducation,
    CandidateCertification,
)
import structlog

logger = structlog.get_logger()

EXTRACTION_SYSTEM_PROMPT = """You are an expert resume parser. Extract structured information from the resume text.
Be accurate and factual - only extract information that is clearly stated in the resume.
Do NOT invent or assume any information not present in the text.
If you're uncertain about something, include it in the warnings list.

Return a JSON object with this exact structure:
{
    "name": "Full Name or null",
    "headline": "Professional headline from resume or null",
    "summary": "Professional summary/objective or null",
    "phone": "Phone number or null",
    "location": "City, State/Country or null",
    "linkedin_url": "LinkedIn URL or null",
    "github_url": "GitHub URL or null",
    "portfolio_url": "Portfolio/website URL or null",
    "total_experience_years": 0,
    "current_role": "Most recent job title or null",
    "current_company": "Most recent company or null",
    "education_level": "Highest degree (e.g., Bachelor's, Master's) or null",
    "skills": [
        {
            "name": "Skill name",
            "category": "technical|soft|tool|framework|language",
            "proficiency_level": "beginner|intermediate|advanced|expert or null",
            "evidence": "Quote or context from resume showing this skill"
        }
    ],
    "experiences": [
        {
            "title": "Job Title",
            "company": "Company Name",
            "location": "Location or null",
            "employment_type": "full-time|part-time|contract|internship or null",
            "start_date": "YYYY-MM or YYYY",
            "end_date": "YYYY-MM or YYYY or Present",
            "is_current": false,
            "description": "Role description",
            "technologies": ["Tech1", "Tech2"],
            "achievements": ["Achievement 1", "Achievement 2"]
        }
    ],
    "projects": [
        {
            "name": "Project Name",
            "description": "Project description",
            "technologies": ["Tech1", "Tech2"],
            "url": "Project URL or null",
            "role": "Your role or null",
            "highlights": ["Highlight 1"]
        }
    ],
    "education": [
        {
            "degree": "Degree name",
            "field_of_study": "Field or null",
            "institution": "University/School",
            "location": "Location or null",
            "start_year": 2020,
            "end_year": 2024,
            "gpa": "GPA or null",
            "achievements": ["Achievement"]
        }
    ],
    "certifications": [
        {
            "name": "Certification Name",
            "issuing_organization": "Issuer or null",
            "issue_date": "YYYY-MM or null",
            "credential_id": "ID or null",
            "credential_url": "URL or null"
        }
    ],
    "confidence": 0.85,
    "warnings": ["List of uncertain extractions or missing information"]
}"""


class ResumeExtractorService:
    """Extracts structured profile information from resume documents."""

    def __init__(self):
        self.ai = AIService()

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF."""
        try:
            doc = fitz.open(file_path)
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()

            full_text = "\n".join(text_parts)
            if not full_text.strip():
                raise ValueError("PDF appears to be empty or contains only images")

            # Limit text length to avoid token limits
            if len(full_text) > 20000:
                full_text = full_text[:20000]
                logger.warning("Resume text truncated to 20000 chars")

            return full_text
        except Exception as e:
            logger.error("PDF extraction failed", error=str(e))
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    async def extract_from_resume(
        self,
        file_path: str,
        user_id: int,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Extract profile data from resume and save to database."""

        # Extract text
        raw_text = self.extract_text_from_pdf(file_path)

        # AI extraction
        prompt = f"Extract structured information from this resume:\n\n{raw_text}"

        try:
            extracted = await self.ai.generate_json(
                prompt=prompt,
                system_instruction=EXTRACTION_SYSTEM_PROMPT,
                temperature=0.1,
            )
        except Exception as e:
            logger.error("AI extraction failed", error=str(e))
            raise RuntimeError(f"AI extraction failed: {str(e)}")

        # Get or create profile
        result = await db.execute(
            select(CandidateProfile).where(CandidateProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            profile = CandidateProfile(user_id=user_id)
            db.add(profile)
            await db.flush()

        # Update profile fields
        profile.headline = extracted.get("headline") or profile.headline
        profile.summary = extracted.get("summary") or profile.summary
        profile.phone = extracted.get("phone") or profile.phone
        profile.location = extracted.get("location") or profile.location
        profile.linkedin_url = extracted.get("linkedin_url") or profile.linkedin_url
        profile.github_url = extracted.get("github_url") or profile.github_url
        profile.portfolio_url = extracted.get("portfolio_url") or profile.portfolio_url
        profile.total_experience_years = extracted.get("total_experience_years") or profile.total_experience_years
        profile.current_role = extracted.get("current_role") or profile.current_role
        profile.current_company = extracted.get("current_company") or profile.current_company
        profile.education_level = extracted.get("education_level") or profile.education_level
        profile.ai_extracted = True
        profile.last_analyzed_at = datetime.now(timezone.utc)

        await db.flush()

        # Add skills
        for skill_data in extracted.get("skills", []):
            if not skill_data.get("name"):
                continue
            skill = CandidateSkill(
                profile_id=profile.id,
                name=skill_data["name"],
                normalized_name=skill_data["name"].lower().strip(),
                category=skill_data.get("category"),
                proficiency_level=skill_data.get("proficiency_level"),
                source="ai_extracted",
                evidence=skill_data.get("evidence"),
                is_verified=False,
            )
            db.add(skill)

        # Add experiences
        for exp_data in extracted.get("experiences", []):
            if not exp_data.get("title") or not exp_data.get("company"):
                continue
            exp = CandidateExperience(
                profile_id=profile.id,
                title=exp_data["title"],
                company=exp_data["company"],
                location=exp_data.get("location"),
                employment_type=exp_data.get("employment_type"),
                start_date=exp_data.get("start_date"),
                end_date=exp_data.get("end_date"),
                is_current=exp_data.get("is_current", False),
                description=exp_data.get("description"),
                technologies=exp_data.get("technologies", []),
                achievements=exp_data.get("achievements", []),
            )
            db.add(exp)

        # Add projects
        for proj_data in extracted.get("projects", []):
            if not proj_data.get("name"):
                continue
            proj = CandidateProject(
                profile_id=profile.id,
                name=proj_data["name"],
                description=proj_data.get("description"),
                technologies=proj_data.get("technologies", []),
                url=proj_data.get("url"),
                role=proj_data.get("role"),
                highlights=proj_data.get("highlights", []),
            )
            db.add(proj)

        # Add education
        for edu_data in extracted.get("education", []):
            if not edu_data.get("degree") or not edu_data.get("institution"):
                continue
            edu = CandidateEducation(
                profile_id=profile.id,
                degree=edu_data["degree"],
                field_of_study=edu_data.get("field_of_study"),
                institution=edu_data["institution"],
                location=edu_data.get("location"),
                start_year=edu_data.get("start_year"),
                end_year=edu_data.get("end_year"),
                gpa=edu_data.get("gpa"),
                achievements=edu_data.get("achievements", []),
            )
            db.add(edu)

        # Add certifications
        for cert_data in extracted.get("certifications", []):
            if not cert_data.get("name"):
                continue
            cert = CandidateCertification(
                profile_id=profile.id,
                name=cert_data["name"],
                issuing_organization=cert_data.get("issuing_organization"),
                issue_date=cert_data.get("issue_date"),
                credential_id=cert_data.get("credential_id"),
                credential_url=cert_data.get("credential_url"),
            )
            db.add(cert)

        await db.flush()

        # Calculate completeness
        profile.profile_completeness = self._calc_completeness(extracted)
        await db.flush()

        return {
            "raw_text": raw_text,
            "confidence": extracted.get("confidence", 0.7),
            "warnings": extracted.get("warnings", []),
        }

    def _calc_completeness(self, data: dict) -> int:
        """Calculate profile completeness from extracted data."""
        score = 0
        if data.get("headline"): score += 10
        if data.get("summary"): score += 10
        if data.get("location"): score += 5
        if data.get("total_experience_years"): score += 5
        if data.get("current_role"): score += 5
        if data.get("education_level"): score += 5
        skills = data.get("skills", [])
        if skills: score += min(20, len(skills) * 4)
        exps = data.get("experiences", [])
        if exps: score += min(20, len(exps) * 10)
        projects = data.get("projects", [])
        if projects: score += min(10, len(projects) * 5)
        education = data.get("education", [])
        if education: score += 10
        return min(100, score)
