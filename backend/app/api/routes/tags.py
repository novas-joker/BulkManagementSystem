"""Tag routes for managing contact tags."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.tag_service import TagService
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.infrastructure.repositories.tag_repository import TagRepository
from app.schemas.tag import TagCreateRequest, TagResponse, TagUpdateRequest

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=list[TagResponse])
async def list_tags(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all tags for the signed-in user."""
    repository = TagRepository(db)
    service = TagService(repository)
    tags = await service.list_tags(current_user.id)
    return [TagResponse(**tag) for tag in tags]


@router.post("", response_model=TagResponse)
async def create_tag(
    payload: TagCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new tag."""
    repository = TagRepository(db)
    service = TagService(repository)

    try:
        tag = await service.create_tag(current_user.id, payload.model_dump())
        return TagResponse(**tag)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Fetch a single tag."""
    repository = TagRepository(db)
    service = TagService(repository)
    tag = await service.get_tag(current_user.id, tag_id)

    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    return TagResponse(**tag)


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: str,
    payload: TagUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a tag."""
    repository = TagRepository(db)
    service = TagService(repository)
    updated = await service.update_tag(current_user.id, tag_id, payload.model_dump(exclude_unset=True))

    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    return TagResponse(**updated)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a tag."""
    repository = TagRepository(db)
    service = TagService(repository)
    deleted = await service.delete_tag(current_user.id, tag_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    return None


@router.post("/{tag_id}/contacts/{contact_id}", status_code=status.HTTP_201_CREATED)
async def assign_tag_to_contact(
    tag_id: str,
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Assign a tag to a contact."""
    repository = TagRepository(db)
    service = TagService(repository)
    result = await service.assign_tag_to_contact(current_user.id, tag_id, contact_id)

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    return result


@router.delete("/{tag_id}/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag_from_contact(
    tag_id: str,
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Remove a tag from a contact."""
    repository = TagRepository(db)
    service = TagService(repository)
    removed = await service.remove_tag_from_contact(current_user.id, tag_id, contact_id)

    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag or contact not found")

    return None
