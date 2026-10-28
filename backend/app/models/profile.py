"""Candidate profile and related models."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    headline = Column(String(500))
    summary = Column(Text)
    phone = Column(String(50))
    location = Column(String(255))
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    portfolio_url = Column(String(500))
    total_experience_years = Column(Float, default=0)
    current_role = Column(String(255))
    current_company = Column(String(255))
    education_level = Column(String(100))  # e.g., "Bachelor's", "Master's"
    profile_completeness = Column(Integer, default=0)  # 0-100
    ai_extracted = Column(Boolean, default=False)
    last_analyzed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="profile")
    skills = relationship("CandidateSkill", back_populates="profile", cascade="all, delete-orphan")
    experiences = relationship("CandidateExperience", back_populates="profile", cascade="all, delete-orphan", order_by="desc(CandidateExperience.start_date)")
    projects = relationship("CandidateProject", back_populates="profile", cascade="all, delete-orphan")
    education = relationship("CandidateEducation", back_populates="profile", cascade="all, delete-orphan")
    certifications = relationship("CandidateCertification", back_populates="profile", cascade="all, delete-orphan")


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    normalized_name = Column(String(255), index=True)  # AI-normalized
    category = Column(String(100))  # "technical", "soft", "tool", "framework"
    proficiency_level = Column(String(50))  # "beginner", "intermediate", "advanced", "expert"
    years_of_experience = Column(Float)
    is_verified = Column(Boolean, default=False)  # User confirmed
    source = Column(String(50), default="ai_extracted")  # "ai_extracted", "user_added", "resume"
    evidence = Column(Text)  # Where in resume this was found
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    profile = relationship("CandidateProfile", back_populates="skills")


class CandidateExperience(Base):
    __tablename__ = "candidate_experiences"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    employment_type = Column(String(50))  # full-time, part-time, contract, internship
    start_date = Column(String(20))  # YYYY-MM or YYYY
    end_date = Column(String(20))  # YYYY-MM, YYYY, or "Present"
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    technologies = Column(JSON, default=list)  # ["Python", "React", ...]
    achievements = Column(JSON, default=list)  # ["Increased X by Y%", ...]
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    profile = relationship("CandidateProfile", back_populates="experiences")


class CandidateProject(Base):
    __tablename__ = "candidate_projects"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    technologies = Column(JSON, default=list)
    url = Column(String(500))
    role = Column(String(255))
    highlights = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    profile = relationship("CandidateProfile", back_populates="projects")


class CandidateEducation(Base):
    __tablename__ = "candidate_education"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    degree = Column(String(255), nullable=False)
    field_of_study = Column(String(255))
    institution = Column(String(255), nullable=False)
    location = Column(String(255))
    start_year = Column(Integer)
    end_year = Column(Integer)
    gpa = Column(String(20))
    achievements = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    profile = relationship("CandidateProfile", back_populates="education")


class CandidateCertification(Base):
    __tablename__ = "candidate_certifications"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    issuing_organization = Column(String(255))
    issue_date = Column(String(20))
    expiry_date = Column(String(20))
    credential_id = Column(String(255))
    credential_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    profile = relationship("CandidateProfile", back_populates="certifications")


class CareerPreference(Base):
    __tablename__ = "career_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    preferred_roles = Column(JSON, default=list)  # ["Backend Developer", "Full-Stack Developer"]
    preferred_locations = Column(JSON, default=list)  # ["Bangalore", "Remote"]
    preferred_work_modes = Column(JSON, default=list)  # ["remote", "hybrid", "onsite"]
    preferred_employment_types = Column(JSON, default=list)  # ["full-time", "contract"]
    experience_level = Column(String(50))  # "entry", "mid", "senior", "lead"
    min_salary = Column(Integer)
    max_salary = Column(Integer)
    salary_currency = Column(String(10), default="INR")
    notice_period_days = Column(Integer)
    willing_to_relocate = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="preferences")
