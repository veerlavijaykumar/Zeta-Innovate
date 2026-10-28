"""Job discovery, deduplication, and persistence service."""
from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, desc
from app.models.jobs import JobListing, JobSource, JobSkill
from app.services.jobs.base import ConnectorRegistry, NormalizedJob
from app.schemas.jobs import JobSearchParams
import structlog

logger = structlog.get_logger()


class JobService:
    """Manages job searches, deduplication, connector ingestion, and database queries."""

    async def ensure_job_sources(self, db: AsyncSession):
        """Ensure all registered job sources exist in the database."""
        connectors = ConnectorRegistry.get_all()
        for name, connector in connectors.items():
            res = await db.execute(select(JobSource).where(JobSource.name == name))
            source = res.scalar_one_or_none()
            if not source:
                source = JobSource(
                    name=name,
                    source_type="api",
                    is_active=True,
                    is_configured=connector.is_configured(),
                )
                db.add(source)
            else:
                source.is_configured = connector.is_configured()
        await db.flush()

    async def ingest_normalized_jobs(
        self,
        jobs: list[NormalizedJob],
        source_name: str,
        db: AsyncSession,
    ) -> list[JobListing]:
        """Ingest, deduplicate, and persist normalized jobs."""
        # Get source ID
        src_res = await db.execute(select(JobSource).where(JobSource.name == source_name))
        source = src_res.scalar_one_or_none()
        source_id = source.id if source else None

        persisted = []
        for nj in jobs:
            canonical_key = nj.canonical_key or f"{source_name}:{nj.external_id}"

            # Deduplication: check existing canonical key
            res = await db.execute(
                select(JobListing).where(JobListing.canonical_key == canonical_key)
            )
            existing = res.scalar_one_or_none()

            if existing:
                # Update freshness
                existing.last_verified_at = datetime.now(timezone.utc)
                existing.is_active = True
                persisted.append(existing)
            else:
                new_listing = JobListing(
                    source_id=source_id,
                    external_id=nj.external_id,
                    title=nj.title,
                    company=nj.company,
                    company_logo_url=nj.company_logo_url,
                    description=nj.description,
                    description_html=nj.description_html,
                    responsibilities=nj.responsibilities,
                    required_skills=nj.required_skills,
                    preferred_skills=nj.preferred_skills,
                    min_experience_years=nj.min_experience_years,
                    max_experience_years=nj.max_experience_years,
                    location=nj.location,
                    work_mode=nj.work_mode,
                    employment_type=nj.employment_type,
                    min_salary=nj.min_salary,
                    max_salary=nj.max_salary,
                    salary_currency=nj.salary_currency,
                    salary_period=nj.salary_period,
                    date_posted=nj.date_posted or datetime.now(timezone.utc),
                    source_name=source_name,
                    source_url=nj.source_url,
                    apply_url=nj.apply_url,
                    canonical_key=canonical_key,
                    is_active=True,
                    last_verified_at=datetime.now(timezone.utc),
                )
                db.add(new_listing)
                await db.flush()

                # Add individual job skills
                for sk in nj.required_skills:
                    db.add(JobSkill(
                        listing_id=new_listing.id,
                        name=sk,
                        normalized_name=sk.lower().strip(),
                        is_required=True,
                    ))
                for sk in nj.preferred_skills:
                    db.add(JobSkill(
                        listing_id=new_listing.id,
                        name=sk,
                        normalized_name=sk.lower().strip(),
                        is_required=False,
                    ))

                persisted.append(new_listing)

        if source:
            source.last_sync_at = datetime.now(timezone.utc)
            # count total listings for this source
            count_res = await db.execute(
                select(func.count(JobListing.id)).where(JobListing.source_id == source.id)
            )
            source.total_listings = count_res.scalar() or 0

        await db.flush()
        return persisted

    async def search_jobs(
        self,
        params: JobSearchParams,
        db: AsyncSession,
    ) -> tuple[list[JobListing], int]:
        """Search jobs from the database with multi-field filtering and pagination."""
        query = select(JobListing).where(JobListing.is_active == True)

        # Keyword query search across title, company, description
        if params.query:
            term = f"%{params.query.strip()}%"
            query = query.where(
                or_(
                    JobListing.title.ilike(term),
                    JobListing.company.ilike(term),
                    JobListing.description.ilike(term),
                )
            )

        # Location filter
        if params.location:
            query = query.where(JobListing.location.ilike(f"%{params.location.strip()}%"))

        # Work mode filter
        if params.work_mode:
            query = query.where(JobListing.work_mode == params.work_mode)

        # Employment type filter
        if params.employment_type:
            query = query.where(JobListing.employment_type == params.employment_type)

        # Experience filters
        if params.min_experience is not None:
            query = query.where(
                or_(
                    JobListing.min_experience_years == None,
                    JobListing.min_experience_years >= params.min_experience,
                )
            )
        if params.max_experience is not None:
            query = query.where(
                or_(
                    JobListing.max_experience_years == None,
                    JobListing.max_experience_years <= params.max_experience,
                )
            )

        # Salary filters
        if params.min_salary is not None:
            query = query.where(
                or_(
                    JobListing.max_salary == None,
                    JobListing.max_salary >= params.min_salary,
                )
            )
        if params.max_salary is not None:
            query = query.where(
                or_(
                    JobListing.min_salary == None,
                    JobListing.min_salary <= params.max_salary,
                )
            )

        # Source filter
        if params.source:
            query = query.where(JobListing.source_name == params.source)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        # Sort
        if params.sort_by == "date":
            query = query.order_by(desc(JobListing.date_posted))
        elif params.sort_by == "salary":
            query = query.order_by(desc(JobListing.max_salary))
        else:
            query = query.order_by(desc(JobListing.id))

        # Pagination
        offset = (params.page - 1) * params.page_size
        query = query.offset(offset).limit(params.page_size)

        result = await db.execute(query)
        jobs = result.scalars().all()

        return list(jobs), total

    async def sync_from_connectors(
        self,
        query: str = "software engineer",
        location: str = "India",
        db: AsyncSession = None,
    ) -> int:
        """Trigger sync from all configured connectors."""
        total_ingested = 0
        connectors = ConnectorRegistry.get_configured()

        for connector in connectors:
            try:
                jobs, _ = await connector.search(query=query, location=location, page=1, page_size=25)
                if jobs and db:
                    ingested = await self.ingest_normalized_jobs(jobs, connector.get_name(), db)
                    total_ingested += len(ingested)
            except Exception as e:
                logger.error("Connector sync failed", connector=connector.get_name(), error=str(e))
                # Update source error
                if db:
                    src_res = await db.execute(
                        select(JobSource).where(JobSource.name == connector.get_name())
                    )
                    src = src_res.scalar_one_or_none()
                    if src:
                        src.last_error = str(e)
                        await db.flush()

        return total_ingested
