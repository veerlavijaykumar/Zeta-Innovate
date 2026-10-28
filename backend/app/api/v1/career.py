"""Career Intelligence API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.services.ai.career_intelligence import CareerIntelligenceService
from app.schemas.application import (
    CareerAnalysisResponse,
    CareerComparisonRequest,
    CareerComparisonResponse,
)

router = APIRouter(prefix="/career", tags=["Career Intelligence"])
career_service = CareerIntelligenceService()


@router.get("/recommendations", response_model=CareerAnalysisResponse)
async def get_career_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate or retrieve AI-powered career recommendations based on user profile facts."""
    try:
        analysis = await career_service.analyze_career(user_id=current_user.id, db=db)
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Career intelligence analysis failed: {str(e)}",
        )


@router.post("/compare", response_model=CareerComparisonResponse)
async def compare_careers(
    data: CareerComparisonRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Compare 2 to 5 career roles for the candidate based on profile skills, gaps, and readiness."""
    try:
        comparison = await career_service.compare_careers(
            user_id=current_user.id,
            roles=data.roles,
            db=db,
        )
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Career comparison failed: {str(e)}",
        )
