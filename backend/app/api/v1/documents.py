"""AI Resume and Cover-Letter Studio API routes."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.application import GeneratedDocument
from app.services.ai.resume_tailor import ResumeTailorService
from app.schemas.application import (
    GenerateResumeRequest,
    GenerateCoverLetterRequest,
    GeneratedDocumentResponse,
    DocumentUpdateRequest,
)

router = APIRouter(prefix="/documents", tags=["Document Studio"])
tailor_service = ResumeTailorService()


@router.get("", response_model=list[GeneratedDocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all generated resumes and cover letters for current user."""
    res = await db.execute(
        select(GeneratedDocument)
        .where(GeneratedDocument.user_id == current_user.id)
        .order_by(GeneratedDocument.created_at.desc())
    )
    return res.scalars().all()


@router.get("/{doc_id}", response_model=GeneratedDocumentResponse)
async def get_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific generated document with raw content and rendered HTML."""
    res = await db.execute(
        select(GeneratedDocument).where(
            GeneratedDocument.id == doc_id,
            GeneratedDocument.user_id == current_user.id,
        )
    )
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/resume", response_model=GeneratedDocumentResponse, status_code=status.HTTP_201_CREATED)
async def generate_tailored_resume(
    data: GenerateResumeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a truthful, ATS-optimized tailored resume for a specific job."""
    try:
        doc = await tailor_service.generate_tailored_resume(
            user_id=current_user.id,
            listing_id=data.listing_id,
            custom_instructions=data.customize_instructions,
            db=db,
        )
        return doc
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume tailoring failed: {str(e)}",
        )


@router.post("/cover-letter", response_model=GeneratedDocumentResponse, status_code=status.HTTP_201_CREATED)
async def generate_cover_letter(
    data: GenerateCoverLetterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a truthful, personalized cover letter for a specific job."""
    try:
        doc = await tailor_service.generate_cover_letter(
            user_id=current_user.id,
            listing_id=data.listing_id,
            tone=data.tone,
            custom_instructions=data.customize_instructions,
            db=db,
        )
        return doc
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cover letter generation failed: {str(e)}",
        )


@router.put("/{doc_id}", response_model=GeneratedDocumentResponse)
async def update_document(
    doc_id: int,
    data: DocumentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Edit generated document content and update version."""
    res = await db.execute(
        select(GeneratedDocument).where(
            GeneratedDocument.id == doc_id,
            GeneratedDocument.user_id == current_user.id,
        )
    )
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.content = data.content
    if data.title:
        doc.title = data.title
    doc.version += 1

    await db.flush()
    await db.refresh(doc)
    return doc


@router.get("/{doc_id}/html", response_class=Response)
async def get_document_html(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get ready-to-print full HTML document with styling."""
    res = await db.execute(
        select(GeneratedDocument).where(
            GeneratedDocument.id == doc_id,
            GeneratedDocument.user_id == current_user.id,
        )
    )
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{doc.title or 'Document'}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1e293b;
            line-height: 1.6;
            margin: 40px auto;
            max-width: 800px;
            padding: 0 20px;
        }}
        h1 {{ font-size: 26px; margin-bottom: 4px; color: #0f172a; }}
        h2 {{ font-size: 16px; text-transform: uppercase; letter-spacing: 0.05em; color: #2563eb; border-bottom: 2px solid #e2e8f0; padding-bottom: 4px; margin-top: 24px; }}
        .contact-info {{ font-size: 14px; color: #64748b; margin-bottom: 20px; }}
        .skills-grid {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }}
        .skill-tag {{ background: #eff6ff; color: #1d4ed8; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }}
        .job-entry {{ margin-bottom: 16px; }}
        .job-header {{ display: flex; justify-content: space-between; margin-bottom: 4px; }}
        .dates {{ color: #64748b; font-size: 13px; }}
        .bullets {{ margin: 4px 0 0 20px; padding: 0; }}
        .bullets li {{ margin-bottom: 4px; font-size: 14px; }}
        .project-entry {{ margin-bottom: 12px; font-size: 14px; }}
        .letter-header hr {{ border: 0; border-top: 1px solid #e2e8f0; margin: 16px 0; }}
        .letter-date {{ margin-bottom: 16px; color: #64748b; font-size: 14px; }}
        .recipient {{ margin-bottom: 24px; font-size: 14px; }}
        .letter-body p {{ margin-bottom: 16px; font-size: 15px; }}
        @media print {{
            body {{ margin: 0; padding: 0; }}
        }}
    </style>
</head>
<body>
    {doc.content_html or f'<pre>{doc.content}</pre>'}
</body>
</html>"""
    return Response(content=styled_html, media_type="text/html")


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a generated document."""
    res = await db.execute(
        select(GeneratedDocument).where(
            GeneratedDocument.id == doc_id,
            GeneratedDocument.user_id == current_user.id,
        )
    )
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(doc)
