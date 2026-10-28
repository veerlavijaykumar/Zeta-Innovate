"""Remotive free job feed connector.

Remotive API: https://remotive.com/api/remote-jobs
- 100% Free, zero subscription cost
- Real tech vacancies, tags, descriptions, company profiles, and direct application URLs
- No API key required
"""
import httpx
from datetime import datetime, timezone
from typing import Optional, Any
from html import unescape
import re
from app.services.jobs.base import BaseJobConnector, NormalizedJob
import structlog

logger = structlog.get_logger()


class RemotiveConnector(BaseJobConnector):
    """Free Remotive tech job API connector."""

    def __init__(self):
        self.base_url = "https://remotive.com/api/remote-jobs"

    def get_name(self) -> str:
        return "remotive"

    def is_configured(self) -> bool:
        # Free public API - always ready and configured out of the box!
        return True

    def _clean_html(self, html: str) -> str:
        """Strip HTML tags and decode entities."""
        if not html:
            return ""
        clean = re.sub(r'<[^>]+>', '', html)
        return unescape(clean).strip()

    def _extract_skills(self, tags: list[str], description: str) -> list[str]:
        """Combine explicit tags with common tech skills extracted from the description."""
        common_skills = [
            "python", "react", "typescript", "javascript", "fastapi", "django",
            "node.js", "nodejs", "sql", "postgresql", "mysql", "mongodb", "redis",
            "docker", "kubernetes", "aws", "gcp", "azure", "git", "ci/cd",
            "graphql", "linux", "html", "css", "tailwind", "go", "java", "c++",
            "machine learning", "pytorch", "tensorflow", "terraform",
        ]
        skills = set()
        for tag in tags or []:
            t_clean = tag.strip().lower()
            if len(t_clean) > 1:
                skills.add(t_clean)

        desc_lower = description.lower()
        for sk in common_skills:
            if sk in desc_lower:
                skills.add(sk)

        return list(skills)

    def _normalize_job(self, raw: dict) -> NormalizedJob:
        """Normalize Remotive API response to standard NormalizedJob format."""
        description = self._clean_html(raw.get("description", ""))
        tags = raw.get("tags", [])
        skills = self._extract_skills(tags, description)

        external_id = str(raw.get("id", ""))
        location = raw.get("candidate_required_location", "Remote") or "Remote"

        # Date posted
        date_posted = None
        if raw.get("publication_date"):
            try:
                date_posted = datetime.fromisoformat(raw["publication_date"].replace("Z", "+00:00"))
            except Exception:
                date_posted = datetime.now(timezone.utc)

        # Work mode & job type
        job_type = raw.get("job_type", "full_time") or "full-time"
        employment_type = "full-time" if "full" in job_type else "contract"

        # Salary parsing if present
        min_salary = None
        max_salary = None
        salary_str = raw.get("salary", "")
        if salary_str:
            numbers = re.findall(r'\d[\d,]*', salary_str)
            if numbers:
                try:
                    num_clean = [int(n.replace(',', '')) for n in numbers if int(n.replace(',', '')) > 1000]
                    if num_clean:
                        min_salary = min(num_clean)
                        max_salary = max(num_clean)
                except Exception:
                    pass

        return NormalizedJob(
            external_id=external_id,
            title=raw.get("title", "").strip(),
            company=raw.get("company_name", "Unknown").strip(),
            company_logo_url=raw.get("company_logo", "") or "",
            description=description,
            description_html=raw.get("description", ""),
            required_skills=skills[:8],
            preferred_skills=skills[8:15] if len(skills) > 8 else [],
            location=location,
            work_mode="remote",
            employment_type=employment_type,
            min_salary=min_salary,
            max_salary=max_salary,
            salary_currency="USD",
            salary_period="yearly",
            date_posted=date_posted,
            source_name="remotive",
            source_url=raw.get("url", ""),
            apply_url=raw.get("url", ""),
            canonical_key=f"remotive:{external_id}",
        )

    async def search(
        self,
        query: str = "",
        location: str = "",
        page: int = 1,
        page_size: int = 25,
        **filters,
    ) -> tuple[list[NormalizedJob], int]:
        """Fetch remote tech jobs from Remotive API (100% Free)."""
        params: dict[str, Any] = {
            "limit": min(page_size, 50),
        }
        if query:
            params["search"] = query

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                res = await client.get(self.base_url, params=params, headers=headers)
                res.raise_for_status()
                data = res.json()

            raw_jobs = data.get("jobs", [])
            normalized = [self._normalize_job(j) for j in raw_jobs]

            # Filter location if specified
            if location and location.lower() != "worldwide":
                filtered = [
                    j for j in normalized
                    if location.lower() in j.location.lower() or "worldwide" in j.location.lower()
                ]
                if filtered:
                    normalized = filtered

            logger.info("Remotive free job search complete", query=query, count=len(normalized))
            return normalized, len(normalized)

        except Exception as e:
            logger.error("Remotive connector request failed", error=str(e))
            raise

    async def get_job_detail(self, external_id: str) -> Optional[NormalizedJob]:
        return None

    async def health_check(self) -> dict[str, Any]:
        base = await super().health_check()
        base["cost"] = "100% Free (No subscription or API key required)"
        base["status"] = "ok"
        return base
