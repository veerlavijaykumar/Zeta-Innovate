"""AI Resume and Cover-Letter Studio Service."""
import json
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.services.ai.base import AIService
from app.models.profile import CandidateProfile
from app.models.jobs import JobListing
from app.models.application import GeneratedDocument
import structlog

logger = structlog.get_logger()

RESUME_TAILOR_PROMPT = """You are a senior technical executive resume writer.
Tailor the candidate's resume specifically for the target job opportunity.

CRITICAL TRUTHFULNESS & ATS RULES:
1. NEVER fabricate work experience, fake employer names, falsified dates, or nonexistent degrees/certifications.
2. Only highlight skills and projects that the candidate ACTUALLY possesses in their profile.
3. Reframe and emphasize the candidate's genuine achievements and technical competencies to match the target job description keywords naturally.
4. Structure bullets using the Google XYZ formula: "Accomplished [X] as measured by [Y], by doing [Z]".
5. Provide a list of recommended edits and justifications so the candidate understands why each section was emphasized.

Return valid JSON with this structure:
{
    "title": "Tailored Resume - [Job Title] at [Company]",
    "professional_summary": "Tailored 3-4 sentence professional summary aligning genuine candidate strengths with the target role",
    "highlighted_skills": ["Skill 1", "Skill 2"],
    "tailored_experiences": [
        {
            "title": "Title",
            "company": "Company",
            "period": "Dates from profile",
            "bullets": [
                "Tailored bullet point strictly grounded in user's real experience"
            ]
        }
    ],
    "tailored_projects": [
        {
            "name": "Project Name",
            "technologies": ["Tech 1", "Tech 2"],
            "description": "Tailored highlight of how this project demonstrates job-relevant capabilities"
        }
    ],
    "strategic_recommendations": [
        "Explanation of what was prioritized and why it improves ATS match"
    ],
    "truthfulness_audit": "Confirmation that all claims were grounded in user profile data"
}"""

COVER_LETTER_PROMPT = """You are an executive career advisor.
Generate a compelling, personalized, highly authentic cover letter tailored to the job opportunity.

CRITICAL RULES:
1. Tone should be: {tone}.
2. Tone must be professional, direct, humble yet confident. Avoid cheesy cliches like "I am writing with great enthusiasm".
3. Cite real candidate projects, technologies, and achievements from their profile that directly solve the company's needs described in the job post.
4. NEVER fabricate experience or achievements.
5. Standard professional 3-4 paragraph business letter format.

Return valid JSON:
{
    "title": "Cover Letter - [Job Title] at [Company]",
    "salutation": "Dear Hiring Team at [Company],",
    "body_paragraphs": [
        "Opening paragraph stating the specific role and summarizing the value proposition grounded in actual background.",
        "Middle paragraph deep-diving into specific relevant achievements and tech stack mastery directly matching the job requirements.",
        "Closing paragraph connecting personal mission to the company's domain, with a clear call to conversation."
    ],
    "sign_off": "Sincerely,\\n[Candidate Name]"
}"""


class ResumeTailorService:
    """Service for tailoring resumes and generating cover letters."""

    def __init__(self):
        self.ai = AIService()

    def _format_profile_and_job(self, profile: CandidateProfile, job: JobListing) -> tuple[str, str]:
        """Convert profile and job to detailed text prompts."""
        profile_sections = [
            f"Candidate Name: {profile.user.full_name if profile.user else 'Candidate'}",
            f"Current Role: {profile.current_role or 'Engineer'}",
            f"Total Experience: {profile.total_experience_years or 0} years",
            f"Summary: {profile.summary or ''}",
        ]
        if profile.skills:
            profile_sections.append("Verified Skills: " + ", ".join([s.name for s in profile.skills]))
        if profile.experiences:
            exps = []
            for exp in profile.experiences:
                exps.append(
                    f"- {exp.title} at {exp.company} ({exp.start_date or ''} - {exp.end_date or 'Present'}): "
                    f"{exp.description or ''} | Tech: {', '.join(exp.technologies or [])}"
                )
            profile_sections.append("Work History:\n" + "\n".join(exps))
        if profile.projects:
            projs = []
            for p in profile.projects:
                projs.append(f"- {p.name}: {p.description or ''} | Tech: {', '.join(p.technologies or [])}")
            profile_sections.append("Projects:\n" + "\n".join(projs))

        job_sections = [
            f"Job Title: {job.title}",
            f"Company: {job.company}",
            f"Location: {job.location or 'Remote'}",
            f"Work Mode: {job.work_mode or 'Not specified'}",
            f"Required Skills: {', '.join(job.required_skills or [])}",
            f"Preferred Skills: {', '.join(job.preferred_skills or [])}",
            f"Description:\n{job.description[:3000] if job.description else ''}",
        ]

        return "\n".join(profile_sections), "\n".join(job_sections)

    async def generate_tailored_resume(
        self,
        user_id: int,
        listing_id: int,
        custom_instructions: Optional[str],
        db: AsyncSession,
    ) -> GeneratedDocument:
        """Generate a tailored resume and save as GeneratedDocument."""
        profile_res = await db.execute(
            select(CandidateProfile)
            .where(CandidateProfile.user_id == user_id)
            .options(
                selectinload(CandidateProfile.user),
                selectinload(CandidateProfile.skills),
                selectinload(CandidateProfile.experiences),
                selectinload(CandidateProfile.projects),
                selectinload(CandidateProfile.education),
            )
        )
        profile = profile_res.scalar_one_or_none()
        if not profile:
            raise ValueError("Candidate profile not found.")

        job_res = await db.execute(select(JobListing).where(JobListing.id == listing_id))
        job = job_res.scalar_one_or_none()
        if not job:
            raise ValueError("Job listing not found.")

        profile_text, job_text = self._format_profile_and_job(profile, job)

        prompt = (
            f"=== TARGET JOB DESCRIPTION ===\n{job_text}\n\n"
            f"=== CANDIDATE VERIFIED PROFILE ===\n{profile_text}\n\n"
        )
        if custom_instructions:
            prompt += f"USER CUSTOM PREFERENCES: {custom_instructions}\n\n"
        prompt += "Generate an ATS-optimized, fully truthful tailored resume schema."

        try:
            data = await self.ai.generate_json(
                prompt=prompt,
                system_instruction=RESUME_TAILOR_PROMPT,
                temperature=0.2,
            )
        except Exception as e:
            logger.error("Failed to generate tailored resume", error=str(e))
            raise RuntimeError(f"Resume generation failed: {str(e)}")

        # Build clean HTML presentation
        html_content = self._render_resume_html(profile, job, data)

        doc = GeneratedDocument(
            user_id=user_id,
            listing_id=listing_id,
            document_type="resume",
            title=data.get("title", f"Tailored Resume - {job.title} at {job.company}"),
            content=json.dumps(data, indent=2),
            content_html=html_content,
            template_name="modern_executive",
            version=1,
        )
        db.add(doc)
        await db.flush()
        await db.refresh(doc)
        return doc

    async def generate_cover_letter(
        self,
        user_id: int,
        listing_id: int,
        tone: str,
        custom_instructions: Optional[str],
        db: AsyncSession,
    ) -> GeneratedDocument:
        """Generate a tailored cover letter and save as GeneratedDocument."""
        profile_res = await db.execute(
            select(CandidateProfile)
            .where(CandidateProfile.user_id == user_id)
            .options(
                selectinload(CandidateProfile.user),
                selectinload(CandidateProfile.skills),
                selectinload(CandidateProfile.experiences),
                selectinload(CandidateProfile.projects),
            )
        )
        profile = profile_res.scalar_one_or_none()
        if not profile:
            raise ValueError("Candidate profile not found.")

        job_res = await db.execute(select(JobListing).where(JobListing.id == listing_id))
        job = job_res.scalar_one_or_none()
        if not job:
            raise ValueError("Job listing not found.")

        profile_text, job_text = self._format_profile_and_job(profile, job)

        prompt = (
            f"=== TARGET JOB ===\n{job_text}\n\n"
            f"=== CANDIDATE PROFILE ===\n{profile_text}\n\n"
        )
        if custom_instructions:
            prompt += f"CUSTOM INSTRUCTIONS: {custom_instructions}\n\n"
        prompt += "Generate the cover letter following the specified guidelines."

        formatted_sys_prompt = COVER_LETTER_PROMPT.format(tone=tone)

        try:
            data = await self.ai.generate_json(
                prompt=prompt,
                system_instruction=formatted_sys_prompt,
                temperature=0.3,
            )
        except Exception as e:
            logger.error("Failed to generate cover letter", error=str(e))
            raise RuntimeError(f"Cover letter generation failed: {str(e)}")

        html_content = self._render_cover_letter_html(profile, job, data)

        doc = GeneratedDocument(
            user_id=user_id,
            listing_id=listing_id,
            document_type="cover_letter",
            title=data.get("title", f"Cover Letter - {job.title} at {job.company}"),
            content=json.dumps(data, indent=2),
            content_html=html_content,
            template_name="formal_clean",
            version=1,
        )
        db.add(doc)
        await db.flush()
        await db.refresh(doc)
        return doc

    def _render_resume_html(self, profile: CandidateProfile, job: JobListing, data: dict) -> str:
        """Generate elegant, print-ready HTML for the tailored resume."""
        candidate_name = profile.user.full_name if profile.user else "Candidate"
        skills_chips = "".join([f'<span class="skill-tag">{s}</span>' for s in data.get("highlighted_skills", [])])

        exps_html = ""
        for exp in data.get("tailored_experiences", []):
            bullets = "".join([f"<li>{b}</li>" for b in exp.get("bullets", [])])
            exps_html += f"""
            <div class="job-entry">
                <div class="job-header">
                    <strong>{exp.get('title')}</strong> — <em>{exp.get('company')}</em>
                    <span class="dates">{exp.get('period', '')}</span>
                </div>
                <ul class="bullets">{bullets}</ul>
            </div>
            """

        projs_html = ""
        for p in data.get("tailored_projects", []):
            techs = ", ".join(p.get("technologies", []))
            projs_html += f"""
            <div class="project-entry">
                <strong>{p.get('name')}</strong> {f'<em>({techs})</em>' if techs else ''}
                <p>{p.get('description', '')}</p>
            </div>
            """

        return f"""
        <div class="resume-document">
            <header class="resume-header">
                <h1>{candidate_name}</h1>
                <div class="contact-info">
                    {f'<span>{profile.phone}</span> • ' if profile.phone else ''}
                    {f'<span>{profile.location}</span> • ' if profile.location else ''}
                    {f'<span>{profile.user.email}</span>' if profile.user and profile.user.email else ''}
                </div>
            </header>
            <section class="section">
                <h2>Professional Summary</h2>
                <p>{data.get('professional_summary', '')}</p>
            </section>
            <section class="section">
                <h2>Targeted Technical Competencies</h2>
                <div class="skills-grid">{skills_chips}</div>
            </section>
            <section class="section">
                <h2>Relevant Experience</h2>
                {exps_html}
            </section>
            {f'<section class="section"><h2>Key Projects</h2>{projs_html}</section>' if projs_html else ''}
        </div>
        """

    def _render_cover_letter_html(self, profile: CandidateProfile, job: JobListing, data: dict) -> str:
        """Generate elegant print-ready HTML for the cover letter."""
        candidate_name = profile.user.full_name if profile.user else "Candidate"
        paragraphs = "".join([f"<p>{p}</p>" for p in data.get("body_paragraphs", [])])
        sign_off = data.get("sign_off", f"Sincerely,\n{candidate_name}").replace("\n", "<br/>")

        return f"""
        <div class="cover-letter-document">
            <header class="letter-header">
                <h2>{candidate_name}</h2>
                <p>{profile.location or ''} {f'| {profile.user.email}' if profile.user and profile.user.email else ''}</p>
                <hr/>
            </header>
            <div class="letter-date">{datetime.now().strftime('%B %d, %Y')}</div>
            <div class="recipient">
                <strong>Hiring Team</strong><br/>
                {job.company}<br/>
                Role: {job.title}
            </div>
            <div class="letter-body">
                <p><strong>{data.get('salutation', 'Dear Hiring Team,')}</strong></p>
                {paragraphs}
                <p>{sign_off}</p>
            </div>
        </div>
        """
