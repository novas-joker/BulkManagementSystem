"""Service for importing contacts from CSV files."""

import csv
import io
from typing import Any

from app.application.services.base_service import BaseService
from app.infrastructure.repositories.contact_repository import ContactRepository
from app.infrastructure.database.models import Contact


class ContactImportService(BaseService[ContactRepository]):
    """Business logic for bulk importing contacts from CSV."""

    async def validate_csv(self, csv_content: str) -> dict[str, Any]:
        """
        Validate CSV structure and detect columns.
        Returns: {valid: bool, columns: list, errors: list, preview: list}
        """
        errors = []
        preview = []
        columns = []

        try:
            # Parse CSV
            reader = csv.DictReader(io.StringIO(csv_content))
            if not reader.fieldnames:
                errors.append("CSV has no columns")
                return {"valid": False, "columns": [], "errors": errors, "preview": []}

            columns = list(reader.fieldnames)

            # Required columns
            required = {"email"}
            missing = required - set(col.lower() for col in columns)
            if missing:
                errors.append(f"Missing required columns: {', '.join(missing)}")

            # Preview first 5 rows
            for i, row in enumerate(reader):
                if i >= 5:
                    break
                preview.append(row)

            return {
                "valid": len(errors) == 0,
                "columns": columns,
                "errors": errors,
                "preview": preview,
            }
        except Exception as e:
            return {
                "valid": False,
                "columns": [],
                "errors": [f"CSV parsing error: {str(e)}"],
                "preview": [],
            }

    async def preview_import(
        self,
        user_id: str,
        csv_content: str,
        column_mapping: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Preview what will be imported without actually saving.
        column_mapping: maps CSV column names to Contact fields
        """
        if not column_mapping:
            column_mapping = {}

        preview_data = []
        errors = []

        try:
            reader = csv.DictReader(io.StringIO(csv_content))

            for i, row in enumerate(reader):
                if i >= 10:  # Preview max 10 rows
                    break

                # Map columns
                contact_data = {"user_id": user_id}
                for csv_col, model_field in column_mapping.items():
                    if csv_col in row:
                        contact_data[model_field] = row[csv_col]

                # Validate email
                if "email" not in contact_data or not contact_data["email"]:
                    errors.append(f"Row {i + 2}: Missing email")
                    continue

                preview_data.append(contact_data)

            return {
                "total_rows": i + 1,
                "preview_rows": len(preview_data),
                "preview": preview_data[:5],
                "errors": errors,
            }
        except Exception as e:
            return {
                "total_rows": 0,
                "preview_rows": 0,
                "preview": [],
                "errors": [f"Error: {str(e)}"],
            }

    async def import_contacts(
        self,
        user_id: str,
        csv_content: str,
        column_mapping: dict[str, str] | None = None,
        dedup_strategy: str = "skip",  # skip | merge | overwrite
    ) -> dict[str, Any]:
        """
        Import contacts from CSV.
        dedup_strategy:
          - skip: skip duplicate emails
          - merge: keep existing, merge new fields
          - overwrite: replace with new data
        """
        if not column_mapping:
            column_mapping = {}

        imported = 0
        skipped = 0
        errors = []
        created_ids = []

        try:
            reader = csv.DictReader(io.StringIO(csv_content))

            for row_num, row in enumerate(reader, start=2):
                try:
                    # Map columns
                    contact_data = {"user_id": user_id}
                    for csv_col, model_field in column_mapping.items():
                        if csv_col in row and row[csv_col]:
                            contact_data[model_field] = row[csv_col]

                    # Validate required fields
                    if "email" not in contact_data or not contact_data["email"]:
                        errors.append(f"Row {row_num}: Missing email")
                        skipped += 1
                        continue

                    # Check for duplicates
                    existing = await self.repository.get_by_user_and_email(
                        user_id, contact_data["email"]
                    )

                    if existing:
                        if dedup_strategy == "skip":
                            skipped += 1
                            continue
                        elif dedup_strategy == "merge":
                            # Update only provided fields
                            updated = await self.repository.update(existing.id, contact_data)
                            created_ids.append(updated.id)
                            imported += 1
                        elif dedup_strategy == "overwrite":
                            # Update all fields
                            await self.repository.delete(existing.id)
                            new_contact = Contact(**contact_data)
                            created = await self.repository.create(new_contact)
                            created_ids.append(created.id)
                            imported += 1
                    else:
                        # Create new contact
                        new_contact = Contact(**contact_data)
                        created = await self.repository.create(new_contact)
                        created_ids.append(created.id)
                        imported += 1

                except Exception as row_error:
                    errors.append(f"Row {row_num}: {str(row_error)}")
                    skipped += 1

            return {
                "success": True,
                "imported": imported,
                "skipped": skipped,
                "total": imported + skipped,
                "created_ids": created_ids,
                "errors": errors,
            }

        except Exception as e:
            return {
                "success": False,
                "imported": 0,
                "skipped": 0,
                "total": 0,
                "created_ids": [],
                "errors": [f"Import failed: {str(e)}"],
            }

    async def bulk_update_status(
        self, user_id: str, contact_ids: list[str], new_status: str
    ) -> dict[str, Any]:
        """Update status for multiple contacts."""
        updated = 0
        failed = []

        for contact_id in contact_ids:
            try:
                contact = await self.repository.get(contact_id)
                if contact and contact.user_id == user_id:
                    await self.repository.update(contact_id, {"status": new_status})
                    updated += 1
                else:
                    failed.append(contact_id)
            except Exception as e:
                failed.append(f"{contact_id}: {str(e)}")

        return {
            "updated": updated,
            "failed": len(failed),
            "failed_ids": failed,
        }
