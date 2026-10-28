"""Job-related models: listings, sources, skills, matches."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class JobSource(Base):
    __tablename__ = "job_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    source_type = Column(String(50), nullable=False)  # "api", "feed", "scraper"
    base_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_configured = Column(Boolean, default=False)
    last_sync_at = Column(DateTime(timezone=True))
    last_error = Column(Text)
    total_listings = Column(Integer, default=0)
    config = Column(JSON, default=dict)  # Non-sensitive config
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    listings = relationship("JobListing", back_populates="source")


class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("job_sources.id", ondelete="SET NULL"), index=True)
    external_id = Column(String(255), index=True)  # Provider's ID
    title = Column(String(500), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    company_logo_url = Column(String(500))
    description = Column(Text)
    description_html = Column(Text)
    responsibilities = Column(JSON, default=list)
    required_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    min_experience_years = Column(Float)
    max_experience_years = Column(Float)
    location = Column(String(255), index=True)
    work_mode = Column(String(50), index=True)  # "remote", "hybrid", "onsite"
    employment_type = Column(String(50), index=True)  # "full-time", "part-time", "contract"
    min_salary = Column(Integer)
    max_salary = Column(Integer)
    salary_currency = Column(String(10))
    salary_period = Column(String(20))  # "yearly", "monthly", "hourly"
    date_posted = Column(DateTime(timezone=True))
    date_expires = Column(DateTime(timezone=True))
    source_name = Column(String(100))
    source_url = Column(String(1000))  # Original listing URL
    apply_url = Column(String(1000))  # Official application URL
    is_active = Column(Boolean, default=True, index=True)
    last_verified_at = Column(DateTime(timezone=True))
    canonical_key = Column(String(500), unique=True, index=True)  # For dedup: source_name:external_id
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    source = relationship("JobSource", back_populates="listings")
    skills = relationship("JobSkill", back_populates="listing", cascade="all, delete-orphan")
    matches = relationship("JobMatch", back_populates="listing", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_source_external_id"),
    )


class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("job_listings.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    normalized_name = Column(String(255), index=True)
    is_required = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    listing = relationship("JobListing", back_populates="skills")


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    listing_id = Column(Integer, ForeignKey("job_listings.id", ondelete="CASCADE"), nullable=False, index=True)
    overall_score = Column(Float, nullable=False)  # 0-100
    required_skill_score = Column(Float, default=0)
    preferred_skill_score = Column(Float, default=0)
    experience_score = Column(Float, default=0)
    semantic_score = Column(Float, default=0)
    preference_score = Column(Float, default=0)
    is_eligible = Column(Boolean, default=True)
    eligibility_warnings = Column(JSON, default=list)
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    explanation = Column(Text)
    evidence = Column(JSON, default=list)  # [{"claim": "...", "source": "resume|jd", "text": "..."}]
    scoring_version = Column(String(20), default="v1")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    listing = relationship("JobListing", back_populates="matches")

    __table_args__ = (
        UniqueConstraint("user_id", "listing_id", name="uq_user_listing_match"),
    )


class MatchEvidence(Base):
    __tablename__ = "match_evidence"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("job_matches.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type = Column(String(50), nullable=False)  # "skill_match", "experience_match", "project_match"
    claim = Column(Text, nullable=False)
    source = Column(String(20), nullable=False)  # "resume", "job_description"
    source_text = Column(Text)
    confidence = Column(Float)  # 0-1
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
