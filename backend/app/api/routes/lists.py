"""Mailing list routes for managing audience lists."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.list_service import MailingListService
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.infrastructure.repositories.list_repository import MailingListRepository
from app.schemas.list import (
    MailingListCreateRequest,
    MailingListResponse,
    MailingListUpdateRequest,
    ListContactResponse,
)

router = APIRouter(prefix="/lists", tags=["Mailing Lists"])


@router.get("", response_model=list[MailingListResponse])
async def list_mailing_lists(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all mailing lists for the signed-in user."""
    repository = MailingListRepository(db)
    service = MailingListService(repository)
    lists = await service.list_lists(current_user.id)
    return [MailingListResponse(**lst) for lst in lists]


@router.post("", response_model=MailingListResponse)
async def create_mailing_list(
    payload: MailingListCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new mailing list."""
    repository = MailingListRepository(db)
    service = MailingListService(repository)

    try:
        lst = await service.create_list(current_user.id, payload.model_dump())
        return MailingListResponse(**lst)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{list_id}", response_model=MailingListResponse)
async def get_mailing_list(
    list_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Fetch a single mailing list."""
    repository = MailingListRepository(db)
    service = MailingListService(repository)
    lst = await service.get_list(current_user.id, list_id)

    if lst is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")

    return MailingListResponse(**lst)


@router.put("/{list_id}", response_model=MailingListResponse)
async def update_mailing_list(
    list_id: str,
    payload: MailingListUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a mailing list."""
    repository = MailingListRepository(db)
    service = MailingListService(repository)
    updated = await service.update_list(current_user.id, list_id, payload.model_dump(exclude_unset=True))

    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")

    return MailingListResponse(**updated)


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mailing_list(
    list_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a mailing list."""
    repository = MailingListRepository(db)
    service = MailingListService(repository)
    deleted = await service.delete_list(current_user.id, list_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")

    return None


@router.get("/{list_id}/contacts", response_model=list[ListContactResponse])
async def get_list_contacts(
    list_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all contacts in a mailing list."""
    repository = MailingListRepository(db)
    service = MailingListService(repository)
    contacts = await service.get_list_contacts(current_user.id, list_id)

    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")

    return [ListContactResponse(**contact) for contact in contacts]


@router.post("/{list_id}/contacts/{contact_id}", status_code=status.HTTP_201_CREATED)
async def add_contact_to_list(
    list_id: str,
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Add a contact to a mailing list."""
    repository = MailingListRepository(db)
    service = MailingListService(repository)
    result = await service.add_contact_to_list(current_user.id, list_id, contact_id)

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")

    return result


@router.delete("/{list_id}/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact_from_list(
    list_id: str,
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Remove a contact from a mailing list."""
    repository = MailingListRepository(db)
    service = MailingListService(repository)
    removed = await service.remove_contact_from_list(current_user.id, list_id, contact_id)

    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List or contact not found")

    return None
