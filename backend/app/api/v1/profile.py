"""Profile management API routes."""
import os
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
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
from app.models.application import ResumeDocument
from app.schemas.profile import (
    ProfileResponse,
    ProfileUpdate,
    SkillCreate,
    SkillResponse,
    ExperienceCreate,
    ExperienceResponse,
    ProjectCreate,
    ProjectResponse,
    EducationCreate,
    EducationResponse,
    CertificationCreate,
    CertificationResponse,
    PreferenceResponse,
    PreferenceUpdate,
    ResumeUploadResponse,
    AIExtractionResponse,
)

router = APIRouter(prefix="/profile", tags=["Profile"])


async def _get_profile_with_relations(db: AsyncSession, user_id: int) -> CandidateProfile:
    """Get profile with all eagerly loaded relations."""
    result = await db.execute(
        select(CandidateProfile)
        .where(CandidateProfile.user_id == user_id)
        .options(
            selectinload(CandidateProfile.skills),
            selectinload(CandidateProfile.experiences),
            selectinload(CandidateProfile.projects),
            selectinload(CandidateProfile.education),
            selectinload(CandidateProfile.certifications),
        )
    )
    return result.scalar_one_or_none()


def _calc_completeness(profile: CandidateProfile) -> int:
    """Calculate profile completeness percentage without async lazy-load issues."""
    from sqlalchemy import inspect
    score = 0
    if profile.headline: score += 10
    if profile.summary: score += 10
    if profile.location: score += 5
    if profile.total_experience_years: score += 5
    if profile.current_role: score += 5
    if profile.education_level: score += 5
    
    insp = inspect(profile)
    skills = insp.dict.get("skills")
    if skills: score += min(20, len(skills) * 4)
    exps = insp.dict.get("experiences")
    if exps: score += min(20, len(exps) * 10)
    projects = insp.dict.get("projects")
    if projects: score += min(10, len(projects) * 5)
    education = insp.dict.get("education")
    if education: score += 10
    return min(100, score)


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's profile."""
    profile = await _get_profile_with_relations(db, current_user.id)
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        await db.flush()
        profile = await _get_profile_with_relations(db, current_user.id)
    return profile


@router.put("", response_model=ProfileResponse)
async def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update profile fields."""
    profile = await _get_profile_with_relations(db, current_user.id)
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        await db.flush()
        profile = await _get_profile_with_relations(db, current_user.id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    profile.profile_completeness = _calc_completeness(profile)
    await db.flush()
    profile = await _get_profile_with_relations(db, current_user.id)
    return profile


# Skills CRUD
@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def add_skill(
    data: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a skill to profile."""
    profile = await _get_profile_with_relations(db, current_user.id)
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        await db.flush()

    skill = CandidateSkill(
        profile_id=profile.id,
        name=data.name,
        normalized_name=data.name.lower().strip(),
        category=data.category,
        proficiency_level=data.proficiency_level,
        years_of_experience=data.years_of_experience,
        source="user_added",
        is_verified=True,
    )
    db.add(skill)
    await db.flush()
    await db.refresh(skill)
    return skill


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a skill from profile."""
    result = await db.execute(
        select(CandidateSkill)
        .join(CandidateProfile)
        .where(CandidateSkill.id == skill_id, CandidateProfile.user_id == current_user.id)
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    await db.delete(skill)


# Experience CRUD
@router.post("/experiences", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
async def add_experience(
    data: ExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add work experience."""
    profile = await _get_profile_with_relations(db, current_user.id)
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        await db.flush()

    exp = CandidateExperience(profile_id=profile.id, **data.model_dump())
    db.add(exp)
    await db.flush()
    await db.refresh(exp)
    return exp


@router.delete("/experiences/{exp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience(
    exp_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete work experience."""
    result = await db.execute(
        select(CandidateExperience)
        .join(CandidateProfile)
        .where(CandidateExperience.id == exp_id, CandidateProfile.user_id == current_user.id)
    )
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    await db.delete(exp)


# Projects CRUD
@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def add_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a project."""
    profile = await _get_profile_with_relations(db, current_user.id)
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        await db.flush()

    project = CandidateProject(profile_id=profile.id, **data.model_dump())
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a project."""
    result = await db.execute(
        select(CandidateProject)
        .join(CandidateProfile)
        .where(CandidateProject.id == project_id, CandidateProfile.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)


# Education CRUD
@router.post("/education", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
async def add_education(
    data: EducationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add education entry."""
    profile = await _get_profile_with_relations(db, current_user.id)
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        await db.flush()

    edu = CandidateEducation(profile_id=profile.id, **data.model_dump())
    db.add(edu)
    await db.flush()
    await db.refresh(edu)
    return edu


@router.delete("/education/{edu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(
    edu_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete education entry."""
    result = await db.execute(
        select(CandidateEducation)
        .join(CandidateProfile)
        .where(CandidateEducation.id == edu_id, CandidateProfile.user_id == current_user.id)
    )
    edu = result.scalar_one_or_none()
    if not edu:
        raise HTTPException(status_code=404, detail="Education entry not found")
    await db.delete(edu)


# Certifications CRUD
@router.post("/certifications", response_model=CertificationResponse, status_code=status.HTTP_201_CREATED)
async def add_certification(
    data: CertificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a certification."""
    profile = await _get_profile_with_relations(db, current_user.id)
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        await db.flush()

    cert = CandidateCertification(profile_id=profile.id, **data.model_dump())
    db.add(cert)
    await db.flush()
    await db.refresh(cert)
    return cert


@router.delete("/certifications/{cert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_certification(
    cert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a certification."""
    result = await db.execute(
        select(CandidateCertification)
        .join(CandidateProfile)
        .where(CandidateCertification.id == cert_id, CandidateProfile.user_id == current_user.id)
    )
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")
    await db.delete(cert)


# Preferences
@router.get("/preferences", response_model=PreferenceResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get career preferences."""
    result = await db.execute(
        select(CareerPreference).where(CareerPreference.user_id == current_user.id)
    )
    pref = result.scalar_one_or_none()
    if not pref:
        pref = CareerPreference(user_id=current_user.id)
        db.add(pref)
        await db.flush()
        await db.refresh(pref)
    return pref


@router.put("/preferences", response_model=PreferenceResponse)
async def update_preferences(
    data: PreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update career preferences."""
    result = await db.execute(
        select(CareerPreference).where(CareerPreference.user_id == current_user.id)
    )
    pref = result.scalar_one_or_none()
    if not pref:
        pref = CareerPreference(user_id=current_user.id)
        db.add(pref)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pref, field, value)

    await db.flush()
    await db.refresh(pref)
    return pref


# Resume Upload
@router.post("/resume/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a resume PDF for AI extraction."""
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are supported",
        )

    # Read and validate size
    content = await file.read()
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit",
        )

    # Save file
    upload_dir = settings.upload_path / str(current_user.id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_dir / safe_filename

    with open(file_path, "wb") as f:
        f.write(content)

    # Store in DB
    resume = ResumeDocument(
        user_id=current_user.id,
        filename=safe_filename,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size=len(content),
        mime_type=file.content_type,
        is_primary=True,
    )

    # Mark other resumes as non-primary
    existing = await db.execute(
        select(ResumeDocument).where(
            ResumeDocument.user_id == current_user.id,
            ResumeDocument.is_primary == True,
        )
    )
    for existing_resume in existing.scalars():
        existing_resume.is_primary = False

    db.add(resume)
    await db.flush()
    await db.refresh(resume)
    return resume


@router.post("/resume/{resume_id}/extract", response_model=AIExtractionResponse)
async def extract_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Extract profile information from uploaded resume using AI."""
    from app.services.ai.resume_extractor import ResumeExtractorService

    result = await db.execute(
        select(ResumeDocument).where(
            ResumeDocument.id == resume_id,
            ResumeDocument.user_id == current_user.id,
        )
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    extractor = ResumeExtractorService()
    try:
        extraction_result = await extractor.extract_from_resume(
            file_path=resume.file_path,
            user_id=current_user.id,
            db=db,
        )

        resume.is_processed = True
        resume.extracted_text = extraction_result.get("raw_text", "")
        await db.flush()

        profile = await _get_profile_with_relations(db, current_user.id)

        return AIExtractionResponse(
            profile=profile,
            extraction_confidence=extraction_result.get("confidence", 0.7),
            warnings=extraction_result.get("warnings", []),
            message="Profile extracted successfully. Please review and verify the information.",
        )
    except Exception as e:
        resume.processing_error = str(e)
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume extraction failed: {str(e)}",
        )
