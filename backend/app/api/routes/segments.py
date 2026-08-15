"""Segment routes for managing contact segments and filtering."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.segment_service import SegmentService
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.infrastructure.repositories.segment_repository import SegmentRepository
from app.schemas.segment import (
    SegmentCreateRequest,
    SegmentResponse,
    SegmentUpdateRequest,
    SegmentPreviewResponse,
)

router = APIRouter(prefix="/segments", tags=["Segments"])


@router.get("", response_model=list[SegmentResponse])
async def list_segments(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all segments for the signed-in user."""
    repository = SegmentRepository(db)
    service = SegmentService(repository)
    segments = await service.list_segments(current_user.id)
    return [SegmentResponse(**segment) for segment in segments]


@router.post("", response_model=SegmentResponse)
async def create_segment(
    payload: SegmentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new segment."""
    repository = SegmentRepository(db)
    service = SegmentService(repository)

    try:
        segment = await service.create_segment(current_user.id, payload.model_dump())
        return SegmentResponse(**segment)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{segment_id}", response_model=SegmentResponse)
async def get_segment(
    segment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Fetch a single segment."""
    repository = SegmentRepository(db)
    service = SegmentService(repository)
    segment = await service.get_segment(current_user.id, segment_id)

    if segment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Segment not found")

    return SegmentResponse(**segment)


@router.put("/{segment_id}", response_model=SegmentResponse)
async def update_segment(
    segment_id: str,
    payload: SegmentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a segment."""
    repository = SegmentRepository(db)
    service = SegmentService(repository)
    updated = await service.update_segment(current_user.id, segment_id, payload.model_dump(exclude_unset=True))

    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Segment not found")

    return SegmentResponse(**updated)


@router.delete("/{segment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_segment(
    segment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a segment."""
    repository = SegmentRepository(db)
    service = SegmentService(repository)
    deleted = await service.delete_segment(current_user.id, segment_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Segment not found")

    return None


@router.post("/{segment_id}/preview", response_model=SegmentPreviewResponse)
async def preview_segment(
    segment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Preview contacts matching a segment's filter criteria."""
    repository = SegmentRepository(db)
    service = SegmentService(repository)
    preview = await service.preview_segment(current_user.id, segment_id)

    if preview is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Segment not found")

    return SegmentPreviewResponse(**preview)
