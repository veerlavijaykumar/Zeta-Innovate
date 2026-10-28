"""Job-related schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class JobSearchParams(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None
    employment_type: Optional[str] = None
    min_experience: Optional[float] = None
    max_experience: Optional[float] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    source: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "relevance"  # "relevance", "date", "salary"


class JobListingResponse(BaseModel):
    id: int
    title: str
    company: str
    company_logo_url: Optional[str] = None
    description: Optional[str] = None
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    min_experience_years: Optional[float] = None
    max_experience_years: Optional[float] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None
    employment_type: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    date_posted: Optional[datetime] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    apply_url: Optional[str] = None
    is_active: bool = True
    last_verified_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class JobListingDetail(JobListingResponse):
    description_html: Optional[str] = None
    responsibilities: list[str] = []


class JobSearchResponse(BaseModel):
    jobs: list[JobListingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class JobSourceResponse(BaseModel):
    id: int
    name: str
    source_type: str
    is_active: bool
    is_configured: bool
    last_sync_at: Optional[datetime] = None
    total_listings: int = 0
    last_error: Optional[str] = None

    class Config:
        from_attributes = True


class JobMatchResponse(BaseModel):
    id: int
    listing: JobListingResponse
    overall_score: float
    required_skill_score: float
    preferred_skill_score: float
    experience_score: float
    semantic_score: float
    preference_score: float
    is_eligible: bool
    eligibility_warnings: list[str] = []
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    explanation: Optional[str] = None
    evidence: list[dict] = []
    scoring_version: str

    class Config:
        from_attributes = True


class JobMatchListResponse(BaseModel):
    matches: list[JobMatchResponse]
    total: int
    page: int
    page_size: int


class SavedJobCreate(BaseModel):
    listing_id: int
    notes: Optional[str] = None


class SavedJobResponse(BaseModel):
    id: int
    listing: JobListingResponse
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
