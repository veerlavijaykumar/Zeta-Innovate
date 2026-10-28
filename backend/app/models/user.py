"""User model."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    profile = relationship("CandidateProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    resumes = relationship("ResumeDocument", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("CareerPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    saved_jobs = relationship("SavedJob", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    generated_documents = relationship("GeneratedDocument", back_populates="user", cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")
    learning_roadmaps = relationship("LearningRoadmap", back_populates="user", cascade="all, delete-orphan")
