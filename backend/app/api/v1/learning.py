"""Personalized Learning Roadmap API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.application import LearningRoadmap, LearningItem
from app.services.ai.learning_roadmap import LearningRoadmapService
from app.schemas.application import (
    LearningRoadmapBase,
    LearningRoadmapResponse,
    LearningRoadmapListResponse,
    LearningItemResponse,
    LearningItemUpdate,
)

router = APIRouter(prefix="/learning", tags=["Learning Roadmap"])
roadmap_service = LearningRoadmapService()


@router.get("", response_model=LearningRoadmapListResponse)
async def get_roadmaps(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all learning roadmaps for the current user."""
    res = await db.execute(
        select(LearningRoadmap)
        .where(LearningRoadmap.user_id == current_user.id)
        .options(selectinload(LearningRoadmap.items))
        .order_by(LearningRoadmap.created_at.desc())
    )
    roadmaps = res.scalars().all()
    return LearningRoadmapListResponse(
        roadmaps=roadmaps,
        total=len(roadmaps),
    )


@router.get("/{roadmap_id}", response_model=LearningRoadmapResponse)
async def get_roadmap(
    roadmap_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific roadmap with all weekly items, resources, and projects."""
    res = await db.execute(
        select(LearningRoadmap)
        .where(
            LearningRoadmap.id == roadmap_id,
            LearningRoadmap.user_id == current_user.id,
        )
        .options(selectinload(LearningRoadmap.items))
    )
    roadmap = res.scalar_one_or_none()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Learning roadmap not found")
    return roadmap


@router.post("/generate", response_model=LearningRoadmapResponse, status_code=status.HTTP_201_CREATED)
async def generate_roadmap(
    data: LearningRoadmapBase,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a personalized AI learning roadmap for a target role."""
    try:
        roadmap = await roadmap_service.generate_roadmap(
            user_id=current_user.id,
            target_role=data.target_role,
            hours_per_week=data.hours_per_week,
            db=db,
        )
        return roadmap
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate roadmap: {str(e)}",
        )


@router.put("/items/{item_id}", response_model=LearningItemResponse)
async def update_learning_item(
    item_id: int,
    data: LearningItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a roadmap learning item as completed or update learning evidence."""
    try:
        item = await roadmap_service.update_item_status(
            item_id=item_id,
            user_id=current_user.id,
            is_completed=data.is_completed if data.is_completed is not None else False,
            evidence=data.evidence,
            db=db,
        )
        return item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{roadmap_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_roadmap(
    roadmap_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a learning roadmap."""
    res = await db.execute(
        select(LearningRoadmap).where(
            LearningRoadmap.id == roadmap_id,
            LearningRoadmap.user_id == current_user.id,
        )
    )
    roadmap = res.scalar_one_or_none()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    await db.delete(roadmap)
