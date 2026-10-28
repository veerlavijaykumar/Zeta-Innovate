"""Seed verified sample tech jobs into database for local development and testing."""
import asyncio
from datetime import datetime, timezone, timedelta
from app.core.database import async_session_factory, init_db
from app.models.jobs import JobListing, JobSource, JobSkill

SAMPLE_JOBS = [
    {
        "external_id": "seed-001",
        "title": "Full Stack Engineer (React & Python)",
        "company": "Nexus Technologies",
        "description": "We are seeking a Full Stack Engineer to build responsive web applications using React, TypeScript, and FastAPI. You will design scalable REST APIs, write performant database queries, and contribute to cloud deployment on AWS.",
        "required_skills": ["react", "typescript", "python", "fastapi", "postgresql"],
        "preferred_skills": ["docker", "aws", "tailwind css", "redis"],
        "min_experience_years": 1.5,
        "max_experience_years": 4.0,
        "location": "Bangalore, India",
        "work_mode": "hybrid",
        "employment_type": "full-time",
        "min_salary": 1200000,
        "max_salary": 1800000,
        "salary_currency": "INR",
        "salary_period": "yearly",
        "source_name": "seed",
        "source_url": "https://example.com/careers/nexus-fullstack",
        "apply_url": "https://example.com/careers/nexus-fullstack/apply",
        "canonical_key": "seed:seed-001",
    },
    {
        "external_id": "seed-002",
        "title": "Backend Developer (Python / Django)",
        "company": "FinEdge Solutions",
        "description": "Looking for a Backend Developer to join our core payments infrastructure team. Must have strong fundamentals in Python, asynchronous architectures, relational database schema optimization, and secure API design.",
        "required_skills": ["python", "django", "postgresql", "sql", "git"],
        "preferred_skills": ["celery", "redis", "docker", "ci/cd"],
        "min_experience_years": 2.0,
        "max_experience_years": 5.0,
        "location": "Hyderabad, India",
        "work_mode": "remote",
        "employment_type": "full-time",
        "min_salary": 1400000,
        "max_salary": 2200000,
        "salary_currency": "INR",
        "salary_period": "yearly",
        "source_name": "seed",
        "source_url": "https://example.com/careers/finedge-backend",
        "apply_url": "https://example.com/careers/finedge-backend/apply",
        "canonical_key": "seed:seed-002",
    },
    {
        "external_id": "seed-003",
        "title": "Frontend Developer (React / Next.js)",
        "company": "DesignWave Interactive",
        "description": "Build high-performance, accessible, and delightful digital user interfaces. Strong proficiency with modern React 18, Next.js App Router, Tailwind CSS, and state management libraries required.",
        "required_skills": ["react", "javascript", "typescript", "html", "css", "tailwind css"],
        "preferred_skills": ["next.js", "graphql", "figma", "jest"],
        "min_experience_years": 1.0,
        "max_experience_years": 3.0,
        "location": "Pune, India",
        "work_mode": "hybrid",
        "employment_type": "full-time",
        "min_salary": 900000,
        "max_salary": 1500000,
        "salary_currency": "INR",
        "salary_period": "yearly",
        "source_name": "seed",
        "source_url": "https://example.com/careers/designwave-frontend",
        "apply_url": "https://example.com/careers/designwave-frontend/apply",
        "canonical_key": "seed:seed-003",
    },
    {
        "external_id": "seed-004",
        "title": "AI / Machine Learning Engineer",
        "company": "CognitiveLabs AI",
        "description": "Develop and deploy computer vision and LLM-powered applications. Experience fine-tuning open source models, building semantic retrieval pipelines (RAG), and serving models via FastAPI microservices.",
        "required_skills": ["python", "pytorch", "machine learning", "fastapi", "docker"],
        "preferred_skills": ["deep learning", "nlp", "kubernetes", "aws", "langchain"],
        "min_experience_years": 2.0,
        "max_experience_years": 6.0,
        "location": "Bangalore, India",
        "work_mode": "remote",
        "employment_type": "full-time",
        "min_salary": 2000000,
        "max_salary": 3200000,
        "salary_currency": "INR",
        "salary_period": "yearly",
        "source_name": "seed",
        "source_url": "https://example.com/careers/cognitivelabs-ml",
        "apply_url": "https://example.com/careers/cognitivelabs-ml/apply",
        "canonical_key": "seed:seed-004",
    },
    {
        "external_id": "seed-005",
        "title": "DevOps & Cloud Infrastructure Engineer",
        "company": "CloudScale Systems",
        "description": "Manage our multi-region Kubernetes clusters on AWS. Implement automated CI/CD pipelines using GitHub Actions, manage infrastructure as code with Terraform, and oversee monitoring with Prometheus/Grafana.",
        "required_skills": ["docker", "kubernetes", "aws", "terraform", "linux", "ci/cd"],
        "preferred_skills": ["python", "bash", "prometheus", "ansible"],
        "min_experience_years": 3.0,
        "max_experience_years": 7.0,
        "location": "Mumbai, India",
        "work_mode": "onsite",
        "employment_type": "full-time",
        "min_salary": 1800000,
        "max_salary": 2800000,
        "salary_currency": "INR",
        "salary_period": "yearly",
        "source_name": "seed",
        "source_url": "https://example.com/careers/cloudscale-devops",
        "apply_url": "https://example.com/careers/cloudscale-devops/apply",
        "canonical_key": "seed:seed-005",
    },
    {
        "external_id": "seed-006",
        "title": "Junior Software Engineer",
        "company": "InnoSpark Software",
        "description": "Great opportunity for early-career developers. Join our product engineering team to work across modern web technologies, write unit tests, and collaborate with senior mentors in an agile environment.",
        "required_skills": ["python", "javascript", "sql", "git"],
        "preferred_skills": ["react", "html", "css", "docker"],
        "min_experience_years": 0.0,
        "max_experience_years": 2.0,
        "location": "Chennai, India",
        "work_mode": "hybrid",
        "employment_type": "full-time",
        "min_salary": 600000,
        "max_salary": 950000,
        "salary_currency": "INR",
        "salary_period": "yearly",
        "source_name": "seed",
        "source_url": "https://example.com/careers/innospark-junior",
        "apply_url": "https://example.com/careers/innospark-junior/apply",
        "canonical_key": "seed:seed-006",
    },
]


async def seed_data():
    """Seed initial sample jobs."""
    await init_db()
    async with async_session_factory() as session:
        # Create seed source
        source = JobSource(
            name="seed",
            source_type="sample",
            is_active=True,
            is_configured=True,
            total_listings=len(SAMPLE_JOBS),
        )
        session.add(source)
        await session.flush()

        for j in SAMPLE_JOBS:
            listing = JobListing(
                source_id=source.id,
                external_id=j["external_id"],
                title=j["title"],
                company=j["company"],
                description=j["description"],
                required_skills=j["required_skills"],
                preferred_skills=j["preferred_skills"],
                min_experience_years=j["min_experience_years"],
                max_experience_years=j["max_experience_years"],
                location=j["location"],
                work_mode=j["work_mode"],
                employment_type=j["employment_type"],
                min_salary=j["min_salary"],
                max_salary=j["max_salary"],
                salary_currency=j["salary_currency"],
                salary_period=j["salary_period"],
                date_posted=datetime.now(timezone.utc) - timedelta(days=2),
                source_name=j["source_name"],
                source_url=j["source_url"],
                apply_url=j["apply_url"],
                canonical_key=j["canonical_key"],
                is_active=True,
                last_verified_at=datetime.now(timezone.utc),
            )
            session.add(listing)
            await session.flush()

            for sk in j["required_skills"]:
                session.add(JobSkill(listing_id=listing.id, name=sk, normalized_name=sk.lower(), is_required=True))
            for sk in j["preferred_skills"]:
                session.add(JobSkill(listing_id=listing.id, name=sk, normalized_name=sk.lower(), is_required=False))

        await session.commit()
        print(f"Successfully seeded {len(SAMPLE_JOBS)} sample jobs into the database.")


if __name__ == "__main__":
    asyncio.run(seed_data())
