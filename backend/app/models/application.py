"""Application tracking, learning, documents, and search history models."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class ResumeDocument(Base):
    __tablename__ = "resume_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    extracted_text = Column(Text)
    is_primary = Column(Boolean, default=False)
    is_processed = Column(Boolean, default=False)
    processing_error = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="resumes")


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    listing_id = Column(Integer, ForeignKey("job_listings.id", ondelete="CASCADE"), nullable=False, index=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="saved_jobs")
    listing = relationship("JobListing")

    __table_args__ = (
        UniqueConstraint("user_id", "listing_id", name="uq_user_saved_job"),
    )


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    listing_id = Column(Integer, ForeignKey("job_listings.id", ondelete="SET NULL"), index=True)
    status = Column(String(50), default="saved", nullable=False, index=True)
    # Status values: saved, preparing, ready_to_apply, applied, assessment, interview, rejected, offer, withdrawn
    applied_at = Column(DateTime(timezone=True))
    company_name = Column(String(255))  # Denormalized for deleted listings
    job_title = Column(String(500))
    source_url = Column(String(1000))
    apply_url = Column(String(1000))
    resume_version_id = Column(Integer, ForeignKey("generated_documents.id", ondelete="SET NULL"))
    cover_letter_id = Column(Integer, ForeignKey("generated_documents.id", ondelete="SET NULL"))
    notes = Column(Text)
    next_step = Column(String(255))
    next_step_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="applications")
    listing = relationship("JobListing")
    status_history = relationship("ApplicationStatusHistory", back_populates="application", cascade="all, delete-orphan", order_by="desc(ApplicationStatusHistory.changed_at)")


class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status = Column(String(50))
    to_status = Column(String(50), nullable=False)
    notes = Column(Text)
    changed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    application = relationship("Application", back_populates="status_history")


class GeneratedDocument(Base):
    __tablename__ = "generated_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    listing_id = Column(Integer, ForeignKey("job_listings.id", ondelete="SET NULL"), index=True)
    document_type = Column(String(50), nullable=False)  # "resume", "cover_letter"
    title = Column(String(255))
    content = Column(Text)  # JSON or markdown content
    content_html = Column(Text)
    file_path = Column(String(500))  # Generated PDF path
    template_name = Column(String(100))
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="generated_documents")
    listing = relationship("JobListing")


class LearningRoadmap(Base):
    __tablename__ = "learning_roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role = Column(String(255), nullable=False)
    description = Column(Text)
    total_weeks = Column(Integer)
    hours_per_week = Column(Integer, default=10)
    overall_progress = Column(Float, default=0)  # 0-100
    ai_generated = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="learning_roadmaps")
    items = relationship("LearningItem", back_populates="roadmap", cascade="all, delete-orphan", order_by="LearningItem.week_number")


class LearningItem(Base):
    __tablename__ = "learning_items"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("learning_roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(255), nullable=False)
    category = Column(String(100))
    priority = Column(String(20), default="medium")  # "critical", "high", "medium", "low"
    why_important = Column(Text)
    week_number = Column(Integer)
    estimated_hours = Column(Integer)
    resources = Column(JSON, default=list)  # [{"title": "...", "url": "...", "type": "course|article|video"}]
    practice_projects = Column(JSON, default=list)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    evidence = Column(Text)  # User's proof of learning
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    roadmap = relationship("LearningRoadmap", back_populates="items")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query = Column(String(500))
    filters = Column(JSON, default=dict)
    results_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="search_history")
