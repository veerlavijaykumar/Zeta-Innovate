"""Personalized Learning Roadmap Generation Service."""
from datetime import datetime, timezone
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.services.ai.base import AIService
from app.models.profile import CandidateProfile
from app.models.application import LearningRoadmap, LearningItem
import structlog

logger = structlog.get_logger()

LEARNING_ROADMAP_PROMPT = """You are an engineering career coach and curriculum designer.
Design a highly structured, realistic, week-by-week learning roadmap for the candidate to transition into the target role.

RULES:
1. Ground the curriculum strictly in modern industry standards for the specified target role.
2. Address the candidate's actual missing or underdeveloped skills compared to their current profile.
3. Recommend REAL, reliable, verified educational resources and official documentation (e.g., official docs, MDN, freeCodeCamp, Coursera, Harvard CS50, official tutorials). Do NOT fabricate URLs or nonexistent courses.
4. Each item must include at least one concrete, portfolio-worthy practice project that demonstrates practical mastery.
5. Tailor the pace to the candidate's declared weekly availability ({hours_per_week} hours/week).
6. Prioritize skills: "critical" (core fundamentals), "high" (frequently tested in interviews), "medium" (good to have), "low" (specialized).

Return valid JSON with this structure:
{
    "description": "Comprehensive summary of this roadmap strategy and goals",
    "total_weeks": 8,
    "items": [
        {
            "skill_name": "Docker & Containerization",
            "category": "DevOps",
            "priority": "critical",
            "why_important": "Every modern backend engineer is expected to package services in containers for testing and cloud deployment.",
            "week_number": 1,
            "estimated_hours": 10,
            "resources": [
                {
                    "title": "Docker Official Getting Started Guide",
                    "url": "https://docs.docker.com/get-started/",
                    "type": "documentation"
                },
                {
                    "title": "freeCodeCamp Docker Course",
                    "url": "https://www.freecodecamp.org/news/what-is-docker-used-for-a-docker-container-tutorial-for-beginners/",
                    "type": "article"
                }
            ],
            "practice_projects": [
                {
                    "title": "Multi-container Microservice Setup",
                    "description": "Containerize a FastAPI backend with PostgreSQL and Redis using docker-compose with health checks."
                }
            ]
        }
    ]
}"""


class LearningRoadmapService:
    """Generates and manages personalized skill roadmaps."""

    def __init__(self):
        self.ai = AIService()

    async def generate_roadmap(
        self,
        user_id: int,
        target_role: str,
        hours_per_week: int,
        db: AsyncSession,
    ) -> LearningRoadmap:
        """Generate a personalized learning roadmap for a target role."""
        # 1. Fetch current profile
        result = await db.execute(
            select(CandidateProfile)
            .where(CandidateProfile.user_id == user_id)
            .options(
                selectinload(CandidateProfile.skills),
                selectinload(CandidateProfile.experiences),
                selectinload(CandidateProfile.projects),
            )
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise ValueError("Candidate profile not found. Please create your profile first.")

        # 2. Extract current candidate skills and experience summary
        skills_summary = ", ".join([s.name for s in profile.skills]) if profile.skills else "None listed yet"
        exp_summary = (
            f"{profile.total_experience_years or 0} years experience as {profile.current_role or 'Candidate'}."
        )

        prompt = (
            f"TARGET ROLE: {target_role}\n"
            f"WEEKLY AVAILABILITY: {hours_per_week} hours/week\n"
            f"CANDIDATE CURRENT EXPERIENCE: {exp_summary}\n"
            f"CURRENT DEMONSTRATED SKILLS: {skills_summary}\n\n"
            f"Create a realistic, week-by-week learning roadmap covering missing competencies needed for {target_role}."
        )

        formatted_system_prompt = LEARNING_ROADMAP_PROMPT.replace("{hours_per_week}", str(hours_per_week))

        try:
            data = await self.ai.generate_json(
                prompt=prompt,
                system_instruction=formatted_system_prompt,
                temperature=0.2,
                max_tokens=2048,
            )
        except Exception as e:
            logger.error("Failed to generate AI roadmap", error=str(e))
            raise RuntimeError(f"Roadmap generation failed: {str(e)}")

        # 3. Create database records
        roadmap = LearningRoadmap(
            user_id=user_id,
            target_role=target_role,
            description=data.get("description", f"Roadmap for {target_role}"),
            total_weeks=data.get("total_weeks", 6),
            hours_per_week=hours_per_week,
            overall_progress=0.0,
            ai_generated=True,
        )
        db.add(roadmap)
        await db.flush()

        # Add items
        for item_data in data.get("items", []):
            item = LearningItem(
                roadmap_id=roadmap.id,
                skill_name=item_data.get("skill_name", "Skill"),
                category=item_data.get("category", "General"),
                priority=item_data.get("priority", "medium"),
                why_important=item_data.get("why_important", ""),
                week_number=item_data.get("week_number", 1),
                estimated_hours=item_data.get("estimated_hours", hours_per_week),
                resources=item_data.get("resources", []),
                practice_projects=item_data.get("practice_projects", []),
                is_completed=False,
            )
            db.add(item)

        await db.flush()
        await db.refresh(roadmap)

        # Load with items eagerly
        res = await db.execute(
            select(LearningRoadmap)
            .where(LearningRoadmap.id == roadmap.id)
            .options(selectinload(LearningRoadmap.items))
        )
        return res.scalar_one()

    async def update_item_status(
        self,
        item_id: int,
        user_id: int,
        is_completed: bool,
        evidence: str | None,
        db: AsyncSession,
    ) -> LearningItem:
        """Mark a roadmap learning item completed or pending and recompute overall roadmap progress."""
        result = await db.execute(
            select(LearningItem)
            .join(LearningRoadmap)
            .where(
                LearningItem.id == item_id,
                LearningRoadmap.user_id == user_id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            raise ValueError("Learning item not found.")

        item.is_completed = is_completed
        item.completed_at = datetime.now(timezone.utc) if is_completed else None
        if evidence is not None:
            item.evidence = evidence

        await db.flush()

        # Recompute roadmap overall progress
        items_res = await db.execute(
            select(LearningItem).where(LearningItem.roadmap_id == item.roadmap_id)
        )
        all_items = items_res.scalars().all()
        if all_items:
            completed_count = sum(1 for it in all_items if it.is_completed)
            progress = (completed_count / len(all_items)) * 100
            roadmap_res = await db.execute(
                select(LearningRoadmap).where(LearningRoadmap.id == item.roadmap_id)
            )
            roadmap = roadmap_res.scalar_one()
            roadmap.overall_progress = round(progress, 1)

        await db.flush()
        await db.refresh(item)
        return item
