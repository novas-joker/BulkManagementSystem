"""
Celery tasks for campaign management and email delivery.
Handles campaign dispatch, email sending, retries, and state management.
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.celery import celery_app
from app.core.config import settings
from app.application.services.campaign_service import CampaignService
from app.application.services.contact_import_service import ContactImportService
from app.infrastructure.repositories.campaign_repository import CampaignRepository
from app.infrastructure.repositories.contact_repository import ContactRepository
from app.infrastructure.email.providers.factory import EmailProviderFactory
from app.infrastructure.database.models import CampaignStatus, CampaignRecipient, Campaign, User
from sqlalchemy import select, and_

logger = logging.getLogger(__name__)


async def get_async_session():
    """Create async database session for Celery tasks."""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        return session


@celery_app.task(bind=True, name="app.tasks.campaigns.send_campaign_email", max_retries=3)
def send_campaign_email_task(self, campaign_recipient_id: str, campaign_id: str, user_id: str):
    """
    Asynchronous task to send an individual campaign email.
    
    Args:
        campaign_recipient_id: UUID of the campaign recipient record
        campaign_id: UUID of the campaign
        user_id: UUID of the campaign owner
    """
    import asyncio
    
    async def _send():
        async_session = await get_async_session()
        try:
            # Fetch campaign and recipient
            result = await async_session.execute(
                select(Campaign, CampaignRecipient).where(
                    and_(
                        Campaign.id == campaign_id,
                        CampaignRecipient.id == campaign_recipient_id,
                    )
                )
            )
            campaign_data, recipient = result.first()
            
            if not campaign_data or not recipient:
                logger.error(f"Campaign or recipient not found: {campaign_id}, {campaign_recipient_id}")
                return {"status": "failed", "reason": "Not found"}
            
            # Load campaign and template data
            campaign_repo = CampaignRepository(async_session)
            campaign = await campaign_repo.get_by_id(campaign_id)
            
            if not campaign or campaign.get("user_id") != user_id:
                logger.error(f"Unauthorized access to campaign {campaign_id}")
                return {"status": "failed", "reason": "Unauthorized"}
            
            # Get email provider (SMTP is default/fallback)
            provider_name = campaign.get("email_provider", "smtp")
            provider = EmailProviderFactory.get_provider(provider_name)
            
            # Prepare email content (from campaign template)
            email_data = {
                "to": recipient.contact_email,
                "subject": campaign.get("subject", ""),
                "html": campaign.get("html_content", ""),
                "text": campaign.get("text_content", ""),
                "from_name": campaign.get("from_name", "MailForge"),
                "from_email": campaign.get("from_email", "noreply@mailforge.local"),
                "reply_to": campaign.get("reply_to", ""),
                "tracking_pixel": f"/track/open/{recipient.tracking_token}",
            }
            
            # Attempt to send
            result = provider.send(email_data)
            
            if result["success"]:
                recipient.status = "sent"
                recipient.sent_at = datetime.now(timezone.utc)
                recipient.provider_message_id = result.get("message_id")
                logger.info(f"Email sent to {recipient.contact_email} via {provider_name}")
            else:
                recipient.status = "failed"
                recipient.error_message = result.get("error", "Unknown error")
                logger.warning(f"Email send failed for {recipient.contact_email}: {result.get('error')}")
            
            await async_session.commit()
            return {
                "status": result.get("status", "unknown"),
                "success": result.get("success", False),
                "provider": result.get("provider", provider_name),
            }
        except Exception as exc:
            logger.exception(f"Error in send_campaign_email_task: {exc}")
            await async_session.rollback()
            
            # Retry with exponential backoff
            try:
                raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
            except self.MaxRetriesExceededError:
                logger.error(f"Max retries exceeded for {campaign_recipient_id}")
                return {"status": "failed", "reason": "Max retries exceeded"}
        finally:
            await async_session.close()
    
    return asyncio.run(_send())


@celery_app.task(name="app.tasks.campaigns.process_queued_campaigns")
def process_queued_campaigns():
    """
    Celery Beat scheduled task to process campaigns in queued state.
    Dispatches queued campaigns to send emails in batches.
    """
    import asyncio
    
    async def _process():
        async_session = await get_async_session()
        try:
            # Query campaigns in queued status
            result = await async_session.execute(
                select(Campaign).where(Campaign.status == CampaignStatus.QUEUED.value)
            )
            queued_campaigns = result.scalars().all()
            
            logger.info(f"Processing {len(queued_campaigns)} queued campaigns")
            
            for campaign in queued_campaigns:
                # Update campaign status to sending
                campaign.status = CampaignStatus.SENDING
                campaign.started_at = datetime.now(timezone.utc)
                
                # Fetch all pending recipients
                recipients_result = await async_session.execute(
                    select(CampaignRecipient).where(
                        and_(
                            CampaignRecipient.campaign_id == campaign.id,
                            CampaignRecipient.status == "pending",
                        )
                    )
                )
                recipients = recipients_result.scalars().all()
                
                # Queue individual send tasks
                for recipient in recipients:
                    send_campaign_email_task.delay(
                        str(recipient.id),
                        str(campaign.id),
                        str(campaign.user_id),
                    )
                
                logger.info(f"Queued {len(recipients)} emails for campaign {campaign.id}")
                await async_session.commit()
                
        except Exception as exc:
            logger.exception(f"Error in process_queued_campaigns: {exc}")
            await async_session.rollback()
        finally:
            await async_session.close()
    
    return asyncio.run(_process())


@celery_app.task(name="app.tasks.campaigns.retry_failed_email_sends")
def retry_failed_email_sends():
    """
    Celery Beat scheduled task to retry failed email sends.
    Retries emails that failed with transient errors.
    """
    import asyncio
    
    async def _retry():
        async_session = await get_async_session()
        try:
            # Query failed recipients with retry count < max_retries
            result = await async_session.execute(
                select(CampaignRecipient).where(
                    and_(
                        CampaignRecipient.status == "failed",
                        CampaignRecipient.retry_count < 3,
                    )
                )
            )
            failed_recipients = result.scalars().all()
            
            logger.info(f"Retrying {len(failed_recipients)} failed email sends")
            
            for recipient in failed_recipients:
                recipient.retry_count += 1
                recipient.status = "pending"
                
                send_campaign_email_task.delay(
                    str(recipient.id),
                    str(recipient.campaign_id),
                    str(recipient.campaign.user_id) if recipient.campaign else "",
                )
                
                await async_session.commit()
                
        except Exception as exc:
            logger.exception(f"Error in retry_failed_email_sends: {exc}")
            await async_session.rollback()
        finally:
            await async_session.close()
    
    return asyncio.run(_retry())


@celery_app.task(bind=True, name="app.tasks.campaigns.import_contacts_async")
def import_contacts_async_task(self, import_session_id: str, user_id: str):
    """
    Asynchronous task to process CSV contact imports in the background.
    
    Args:
        import_session_id: Unique session ID for tracking import progress
        user_id: ID of the user initiating the import
    """
    import asyncio
    
    async def _import():
        async_session = await get_async_session()
        try:
            contact_repo = ContactRepository(async_session)
            import_service = ContactImportService(contact_repo)
            
            # Process the import
            result = await import_service.process_import(import_session_id, user_id)
            logger.info(f"Import {import_session_id} completed: {result}")
            return result
        except Exception as exc:
            logger.exception(f"Error importing contacts: {exc}")
            try:
                raise self.retry(exc=exc, countdown=120)
            except self.MaxRetriesExceededError:
                return {"status": "failed", "error": str(exc)}
        finally:
            await async_session.close()
    
    return asyncio.run(_import())
