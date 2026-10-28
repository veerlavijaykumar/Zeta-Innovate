"""Profile schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None
    proficiency_level: Optional[str] = None
    years_of_experience: Optional[float] = None


class SkillResponse(SkillBase):
    id: int
    normalized_name: Optional[str] = None
    is_verified: bool = False
    source: str = "ai_extracted"
    evidence: Optional[str] = None

    class Config:
        from_attributes = True


class SkillCreate(SkillBase):
    pass


class ExperienceBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    technologies: list[str] = []
    achievements: list[str] = []


class ExperienceResponse(ExperienceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ExperienceCreate(ExperienceBase):
    pass


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: list[str] = []
    url: Optional[str] = None
    role: Optional[str] = None
    highlights: list[str] = []


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectCreate(ProjectBase):
    pass


class EducationBase(BaseModel):
    degree: str
    field_of_study: Optional[str] = None
    institution: str
    location: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    gpa: Optional[str] = None
    achievements: list[str] = []


class EducationResponse(EducationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EducationCreate(EducationBase):
    pass


class CertificationBase(BaseModel):
    name: str
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None


class CertificationResponse(CertificationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CertificationCreate(CertificationBase):
    pass


class ProfileBase(BaseModel):
    headline: Optional[str] = None
    summary: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    total_experience_years: Optional[float] = None
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    education_level: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    profile_completeness: int = 0
    ai_extracted: bool = False
    last_analyzed_at: Optional[datetime] = None
    skills: list[SkillResponse] = []
    experiences: list[ExperienceResponse] = []
    projects: list[ProjectResponse] = []
    education: list[EducationResponse] = []
    certifications: list[CertificationResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfileUpdate(ProfileBase):
    pass


class PreferenceBase(BaseModel):
    preferred_roles: list[str] = []
    preferred_locations: list[str] = []
    preferred_work_modes: list[str] = []
    preferred_employment_types: list[str] = []
    experience_level: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    salary_currency: str = "INR"
    notice_period_days: Optional[int] = None
    willing_to_relocate: bool = False


class PreferenceResponse(PreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PreferenceUpdate(PreferenceBase):
    pass


class ResumeUploadResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    is_processed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AIExtractionResponse(BaseModel):
    profile: ProfileResponse
    extraction_confidence: float
    warnings: list[str] = []
    message: str
