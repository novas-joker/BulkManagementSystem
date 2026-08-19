"""Suppression list routes for managing blocked email addresses."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.suppression_service import SuppressionService
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.infrastructure.repositories.suppression_repository import SuppressionRepository
from app.schemas.suppression import (
    SuppressionCreateRequest,
    SuppressionResponse,
    SuppressionBulkCreateRequest,
)

router = APIRouter(prefix="/suppressions", tags=["Suppressions"])


@router.get("", response_model=list[SuppressionResponse])
async def list_suppressions(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all suppressed emails for the signed-in user."""
    repository = SuppressionRepository(db)
    service = SuppressionService(repository)
    suppressions = await service.list_suppressions(current_user.id)
    return [SuppressionResponse(**supp) for supp in suppressions]


@router.post("", response_model=SuppressionResponse)
async def add_suppression(
    payload: SuppressionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Add an email to the suppression list."""
    repository = SuppressionRepository(db)
    service = SuppressionService(repository)

    try:
        suppression = await service.suppress_email(current_user.id, payload.model_dump())
        return SuppressionResponse(**suppression)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/bulk", response_model=list[SuppressionResponse])
async def add_bulk_suppressions(
    payload: SuppressionBulkCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Add multiple emails to the suppression list."""
    repository = SuppressionRepository(db)
    service = SuppressionService(repository)

    try:
        suppressions = await service.suppress_multiple(current_user.id, payload.model_dump())
        return [SuppressionResponse(**supp) for supp in suppressions]
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{suppression_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_suppression(
    suppression_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Remove an email from the suppression list."""
    repository = SuppressionRepository(db)
    service = SuppressionService(repository)
    removed = await service.unsuppress_email(current_user.id, suppression_id)

    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suppression not found")

    return None
