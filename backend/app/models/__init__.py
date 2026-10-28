"""Models package - import all models for Alembic discovery."""
from app.models.user import User
from app.models.profile import (
    CandidateProfile,
    CandidateSkill,
    CandidateExperience,
    CandidateProject,
    CandidateEducation,
    CandidateCertification,
    CareerPreference,
)
from app.models.jobs import (
    JobSource,
    JobListing,
    JobSkill,
    JobMatch,
    MatchEvidence,
)
from app.models.application import (
    ResumeDocument,
    SavedJob,
    Application,
    ApplicationStatusHistory,
    GeneratedDocument,
    LearningRoadmap,
    LearningItem,
    SearchHistory,
)

__all__ = [
    "User",
    "CandidateProfile",
    "CandidateSkill",
    "CandidateExperience",
    "CandidateProject",
    "CandidateEducation",
    "CandidateCertification",
    "CareerPreference",
    "JobSource",
    "JobListing",
    "JobSkill",
    "JobMatch",
    "MatchEvidence",
    "ResumeDocument",
    "SavedJob",
    "Application",
    "ApplicationStatusHistory",
    "GeneratedDocument",
    "LearningRoadmap",
    "LearningItem",
    "SearchHistory",
]
