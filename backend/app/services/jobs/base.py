"""Job connector base interface and connector registry."""
from abc import ABC, abstractmethod
from typing import Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NormalizedJob:
    """Normalized job listing from any source."""
    external_id: str
    title: str
    company: str
    description: str = ""
    description_html: str = ""
    responsibilities: list[str] = field(default_factory=list)
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    min_experience_years: Optional[float] = None
    max_experience_years: Optional[float] = None
    location: str = ""
    work_mode: str = ""  # remote, hybrid, onsite
    employment_type: str = ""  # full-time, part-time, contract
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    salary_currency: str = ""
    salary_period: str = ""
    date_posted: Optional[datetime] = None
    source_name: str = ""
    source_url: str = ""
    apply_url: str = ""
    company_logo_url: str = ""
    canonical_key: str = ""  # For deduplication


class BaseJobConnector(ABC):
    """Abstract base class for job source connectors."""

    @abstractmethod
    def get_name(self) -> str:
        """Return connector name."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if connector has required credentials."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str = "",
        location: str = "",
        page: int = 1,
        page_size: int = 20,
        **filters,
    ) -> tuple[list[NormalizedJob], int]:
        """Search for jobs. Returns (jobs, total_count)."""
        pass

    @abstractmethod
    async def get_job_detail(self, external_id: str) -> Optional[NormalizedJob]:
        """Get detailed job listing by external ID."""
        pass

    async def health_check(self) -> dict[str, Any]:
        """Check connector health."""
        return {
            "name": self.get_name(),
            "configured": self.is_configured(),
            "status": "ok" if self.is_configured() else "unconfigured",
        }


class ConnectorRegistry:
    """Registry for job source connectors."""

    _connectors: dict[str, BaseJobConnector] = {}

    @classmethod
    def register(cls, connector: BaseJobConnector):
        """Register a connector."""
        cls._connectors[connector.get_name()] = connector

    @classmethod
    def get(cls, name: str) -> Optional[BaseJobConnector]:
        """Get a connector by name."""
        return cls._connectors.get(name)

    @classmethod
    def get_all(cls) -> dict[str, BaseJobConnector]:
        """Get all registered connectors."""
        return cls._connectors.copy()

    @classmethod
    def get_configured(cls) -> list[BaseJobConnector]:
        """Get all configured connectors."""
        return [c for c in cls._connectors.values() if c.is_configured()]
