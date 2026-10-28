"""Application, learning, and document schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Application Schemas
class ApplicationCreate(BaseModel):
    listing_id: int
    notes: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(saved|preparing|ready_to_apply|applied|assessment|interview|rejected|offer|withdrawn)$")
    notes: Optional[str] = None
    next_step: Optional[str] = None
    next_step_date: Optional[datetime] = None


class ApplicationStatusHistoryResponse(BaseModel):
    id: int
    from_status: Optional[str] = None
    to_status: str
    notes: Optional[str] = None
    changed_at: datetime

    class Config:
        from_attributes = True


class ApplicationResponse(BaseModel):
    id: int
    listing_id: Optional[int] = None
    status: str
    applied_at: Optional[datetime] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    source_url: Optional[str] = None
    apply_url: Optional[str] = None
    notes: Optional[str] = None
    next_step: Optional[str] = None
    next_step_date: Optional[datetime] = None
    status_history: list[ApplicationStatusHistoryResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    applications: list[ApplicationResponse]
    total: int
    page: int
    page_size: int


# Learning Schemas
class LearningItemBase(BaseModel):
    skill_name: str
    category: Optional[str] = None
    priority: str = "medium"
    why_important: Optional[str] = None
    week_number: Optional[int] = None
    estimated_hours: Optional[int] = None
    resources: list[dict] = []
    practice_projects: list[dict] = []


class LearningItemResponse(LearningItemBase):
    id: int
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    evidence: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LearningItemUpdate(BaseModel):
    is_completed: Optional[bool] = None
    evidence: Optional[str] = None


class LearningRoadmapBase(BaseModel):
    target_role: str
    hours_per_week: int = Field(default=10, ge=1, le=80)


class LearningRoadmapResponse(LearningRoadmapBase):
    id: int
    description: Optional[str] = None
    total_weeks: Optional[int] = None
    overall_progress: float = 0
    ai_generated: bool = True
    items: list[LearningItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LearningRoadmapListResponse(BaseModel):
    roadmaps: list[LearningRoadmapResponse]
    total: int


# Document Schemas
class GenerateResumeRequest(BaseModel):
    listing_id: int
    template_name: str = "professional"
    customize_instructions: Optional[str] = None


class GenerateCoverLetterRequest(BaseModel):
    listing_id: int
    tone: str = "professional"  # "professional", "enthusiastic", "concise"
    customize_instructions: Optional[str] = None


class GeneratedDocumentResponse(BaseModel):
    id: int
    document_type: str
    title: Optional[str] = None
    content: Optional[str] = None
    content_html: Optional[str] = None
    file_path: Optional[str] = None
    template_name: Optional[str] = None
    version: int = 1
    listing_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentUpdateRequest(BaseModel):
    content: str
    title: Optional[str] = None


# Career Recommendation Schemas
class CareerRecommendation(BaseModel):
    role_title: str
    fit_score: float = Field(..., ge=0, le=100)
    why_it_fits: str
    relevant_skills: list[str] = []
    relevant_experience: list[str] = []
    missing_skills: list[str] = []
    entry_level_considerations: Optional[str] = None
    recommended_next_steps: list[str] = []
    alternative_paths: list[str] = []
    confidence: str = "medium"  # "low", "medium", "high"


class CareerAnalysisResponse(BaseModel):
    recommendations: list[CareerRecommendation]
    profile_summary: str
    overall_readiness: str
    warnings: list[str] = []
    generated_at: datetime


class CareerComparisonRequest(BaseModel):
    roles: list[str] = Field(..., min_length=2, max_length=5)


class CareerComparisonResponse(BaseModel):
    roles: list[CareerRecommendation]
    comparison_summary: str


# Analytics Schemas
class AnalyticsResponse(BaseModel):
    total_jobs_discovered: int = 0
    relevant_matches: int = 0
    saved_jobs: int = 0
    applications_submitted: int = 0
    interviews: int = 0
    offers: int = 0
    conversion_rate: Optional[float] = None
    skill_gaps: list[dict] = []
    application_timeline: list[dict] = []
    learning_progress: float = 0
    top_matched_roles: list[dict] = []
    recent_activity: list[dict] = []
