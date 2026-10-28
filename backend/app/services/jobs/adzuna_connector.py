"""Adzuna job connector - uses Adzuna's documented public API.

Adzuna API Documentation: https://developer.adzuna.com/overview
Requires free registration for API credentials (APP_ID and APP_KEY).
Free tier: 250 requests/day.

Setup instructions:
1. Register at https://developer.adzuna.com/
2. Get your APP_ID and APP_KEY
3. Set ADZUNA_APP_ID and ADZUNA_APP_KEY in your .env file
"""
import httpx
from datetime import datetime, timezone
from typing import Optional, Any
from html import unescape
import re
from app.core.config import settings
from app.services.jobs.base import BaseJobConnector, NormalizedJob
import structlog

logger = structlog.get_logger()


class AdzunaConnector(BaseJobConnector):
    """Adzuna job search API connector."""

    def __init__(self):
        self.base_url = settings.ADZUNA_BASE_URL
        self.app_id = settings.ADZUNA_APP_ID
        self.app_key = settings.ADZUNA_APP_KEY
        self.default_country = "in"  # India

    def get_name(self) -> str:
        return "adzuna"

    def is_configured(self) -> bool:
        return bool(self.app_id and self.app_key)

    def _clean_html(self, html: str) -> str:
        """Strip HTML tags and decode entities."""
        if not html:
            return ""
        clean = re.sub(r'<[^>]+>', '', html)
        return unescape(clean).strip()

    def _extract_skills_from_description(self, description: str) -> list[str]:
        """Extract likely skills from job description text."""
        common_skills = [
            "python", "java", "javascript", "typescript", "react", "angular", "vue",
            "node.js", "nodejs", "express", "django", "flask", "fastapi", "spring",
            "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "docker", "kubernetes", "aws", "azure", "gcp", "git", "linux",
            "html", "css", "rest", "graphql", "microservices", "agile", "scrum",
            "machine learning", "deep learning", "tensorflow", "pytorch",
            "ci/cd", "jenkins", "terraform", "ansible",
            "c++", "c#", ".net", "go", "rust", "swift", "kotlin",
            "tableau", "power bi", "spark", "hadoop", "kafka", "airflow",
        ]
        desc_lower = description.lower()
        return [skill for skill in common_skills if skill in desc_lower]

    def _determine_work_mode(self, location: str, description: str) -> str:
        """Infer work mode from location/description."""
        combined = f"{location} {description}".lower()
        if "remote" in combined:
            return "remote"
        elif "hybrid" in combined:
            return "hybrid"
        return "onsite"

    def _normalize_job(self, raw: dict) -> NormalizedJob:
        """Normalize Adzuna API response to standard format."""
        description = self._clean_html(raw.get("description", ""))
        location_name = raw.get("location", {}).get("display_name", "")

        # Salary
        min_salary = None
        max_salary = None
        if raw.get("salary_min"):
            min_salary = int(raw["salary_min"])
        if raw.get("salary_max"):
            max_salary = int(raw["salary_max"])

        # Date
        date_posted = None
        if raw.get("created"):
            try:
                date_posted = datetime.fromisoformat(raw["created"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        external_id = str(raw.get("id", ""))
        skills = self._extract_skills_from_description(description)

        return NormalizedJob(
            external_id=external_id,
            title=raw.get("title", "").strip(),
            company=raw.get("company", {}).get("display_name", "Unknown"),
            description=description,
            description_html=raw.get("description", ""),
            required_skills=skills,
            location=location_name,
            work_mode=self._determine_work_mode(location_name, description),
            employment_type=raw.get("contract_type", "full-time") or "full-time",
            min_salary=min_salary,
            max_salary=max_salary,
            salary_currency="INR" if self.default_country == "in" else "GBP",
            salary_period="yearly",
            date_posted=date_posted,
            source_name="adzuna",
            source_url=raw.get("redirect_url", ""),
            apply_url=raw.get("redirect_url", ""),
            canonical_key=f"adzuna:{external_id}",
        )

    async def search(
        self,
        query: str = "",
        location: str = "",
        page: int = 1,
        page_size: int = 20,
        **filters,
    ) -> tuple[list[NormalizedJob], int]:
        """Search Adzuna API for jobs."""
        if not self.is_configured():
            logger.warning("Adzuna connector not configured")
            return [], 0

        country = filters.get("country", self.default_country)
        url = f"{self.base_url}/jobs/{country}/search/{page}"

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": min(page_size, 50),
            "content-type": "application/json",
        }

        if query:
            params["what"] = query
        if location:
            params["where"] = location

        # Apply filters
        if filters.get("employment_type") == "full-time":
            params["full_time"] = 1
        elif filters.get("employment_type") == "part-time":
            params["part_time"] = 1
        elif filters.get("employment_type") == "contract":
            params["contract"] = 1

        if filters.get("min_salary"):
            params["salary_min"] = filters["min_salary"]
        if filters.get("max_salary"):
            params["salary_max"] = filters["max_salary"]

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            total = data.get("count", 0)
            results = data.get("results", [])
            jobs = [self._normalize_job(r) for r in results]

            logger.info("Adzuna search complete", query=query, results=len(jobs), total=total)
            return jobs, total

        except httpx.TimeoutException:
            logger.error("Adzuna API timeout", query=query)
            raise
        except httpx.HTTPStatusError as e:
            logger.error("Adzuna API error", status=e.response.status_code, detail=str(e))
            raise
        except Exception as e:
            logger.error("Adzuna connector error", error=str(e))
            raise

    async def get_job_detail(self, external_id: str) -> Optional[NormalizedJob]:
        """Get job detail - Adzuna doesn't have a separate detail endpoint, 
        so this returns the listing from search cache."""
        return None

    async def health_check(self) -> dict[str, Any]:
        """Check Adzuna API connectivity."""
        base = await super().health_check()
        if not self.is_configured():
            base["setup_instructions"] = (
                "Register at https://developer.adzuna.com/ to get APP_ID and APP_KEY. "
                "Set ADZUNA_APP_ID and ADZUNA_APP_KEY in your .env file."
            )
            return base

        try:
            # Test with a minimal search
            _, total = await self.search(query="developer", page_size=1)
            base["status"] = "ok"
            base["test_results"] = total
        except Exception as e:
            base["status"] = "error"
            base["error"] = str(e)

        return base
