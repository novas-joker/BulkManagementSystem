"""Template routes for managing email templates."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.template_service import TemplateService
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.infrastructure.repositories.template_repository import TemplateRepository
from app.schemas.template import TemplateCreateRequest, TemplateResponse, TemplateUpdateRequest

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.get("", response_model=list[TemplateResponse])
async def list_templates(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List templates for the signed-in user."""
    repository = TemplateRepository(db)
    service = TemplateService(repository)
    templates = await service.list_templates(current_user.id)
    return [TemplateResponse(**template) for template in templates]


@router.post("", response_model=TemplateResponse)
async def create_template(
    payload: TemplateCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a template for the signed-in user."""
    repository = TemplateRepository(db)
    service = TemplateService(repository)

    try:
        template = await service.create_template(current_user.id, payload.model_dump())
        return TemplateResponse(**template)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Fetch a template."""
    repository = TemplateRepository(db)
    service = TemplateService(repository)
    template = await service.get_template(current_user.id, template_id)

    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    return TemplateResponse(**template)


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    payload: TemplateUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a template."""
    repository = TemplateRepository(db)
    service = TemplateService(repository)
    updated = await service.update_template(current_user.id, template_id, payload.model_dump(exclude_unset=True))

    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    return TemplateResponse(**updated)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a template."""
    repository = TemplateRepository(db)
    service = TemplateService(repository)
    deleted = await service.delete_template(current_user.id, template_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    return None
