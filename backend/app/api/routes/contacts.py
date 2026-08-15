"""Contact routes for managing subscribed audience records."""

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.contact_service import ContactService
from app.application.services.contact_import_service import ContactImportService
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.infrastructure.repositories.contact_repository import ContactRepository
from app.schemas.contact import ContactCreateRequest, ContactResponse, ContactUpdateRequest

router = APIRouter(prefix="/contacts", tags=["Contacts"])


class CSVImportRequest(BaseModel):
    """Request for CSV import with column mapping."""

    csv_content: str  # Raw CSV content as string
    column_mapping: dict[str, str] | None = None  # Maps CSV columns to Contact fields
    dedup_strategy: str = "skip"  # skip | merge | overwrite


class CSVValidationResponse(BaseModel):
    """CSV validation response."""

    valid: bool
    columns: list[str]
    errors: list[str]
    preview: list[dict]


class CSVImportResponse(BaseModel):
    """CSV import result response."""

    success: bool
    imported: int
    skipped: int
    total: int
    created_ids: list[str]
    errors: list[str]


class BulkStatusUpdateRequest(BaseModel):
    """Request to update status for multiple contacts."""

    contact_ids: list[str]
    new_status: str  # subscribed | unsubscribed | bounced


@router.get("", response_model=list[ContactResponse])
async def list_contacts(
    q: str | None = Query(default=None, alias="q"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List contacts for the signed-in user."""
    repository = ContactRepository(db)
    service = ContactService(repository)

    if q:
        contacts = await repository.search_for_user(current_user.id, q)
        return [ContactResponse(**service._serialize(contact)) for contact in contacts]

    contacts = await service.list_contacts(current_user.id)
    return [ContactResponse(**contact) for contact in contacts]


@router.post("", response_model=ContactResponse)
async def create_contact(
    payload: ContactCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new contact for the signed-in user."""
    repository = ContactRepository(db)
    service = ContactService(repository)

    try:
        contact = await service.create_contact(current_user.id, payload.model_dump())
        return ContactResponse(**contact)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Fetch a single contact."""
    repository = ContactRepository(db)
    service = ContactService(repository)
    contact = await service.get_contact(current_user.id, contact_id)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    return ContactResponse(**contact)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: str,
    payload: ContactUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a contact."""
    repository = ContactRepository(db)
    service = ContactService(repository)
    updated = await service.update_contact(current_user.id, contact_id, payload.model_dump(exclude_unset=True))

    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    return ContactResponse(**updated)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a contact."""
    repository = ContactRepository(db)
    service = ContactService(repository)
    deleted = await service.delete_contact(current_user.id, contact_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    return None


@router.post("/import/validate", response_model=CSVValidationResponse)
async def validate_csv_import(
    payload: CSVImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Validate CSV structure before importing."""
    repository = ContactRepository(db)
    service = ContactImportService(repository)
    result = await service.validate_csv(payload.csv_content)
    return CSVValidationResponse(**result)


@router.post("/import/preview")
async def preview_csv_import(
    payload: CSVImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Preview what will be imported without saving."""
    repository = ContactRepository(db)
    service = ContactImportService(repository)
    result = await service.preview_import(
        current_user.id,
        payload.csv_content,
        payload.column_mapping,
    )
    return result


@router.post("/import", response_model=CSVImportResponse)
async def import_contacts_from_csv(
    payload: CSVImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Import contacts from CSV file."""
    repository = ContactRepository(db)
    service = ContactImportService(repository)

    try:
        result = await service.import_contacts(
            current_user.id,
            payload.csv_content,
            payload.column_mapping,
            payload.dedup_strategy,
        )
        return CSVImportResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/bulk-subscribe")
async def bulk_subscribe(
    payload: BulkStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Subscribe multiple contacts."""
    repository = ContactRepository(db)
    service = ContactImportService(repository)
    result = await service.bulk_update_status(current_user.id, payload.contact_ids, "subscribed")
    return result


@router.post("/bulk-unsubscribe")
async def bulk_unsubscribe(
    payload: BulkStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Unsubscribe multiple contacts."""
    repository = ContactRepository(db)
    service = ContactImportService(repository)
    result = await service.bulk_update_status(current_user.id, payload.contact_ids, "unsubscribed")
    return result
