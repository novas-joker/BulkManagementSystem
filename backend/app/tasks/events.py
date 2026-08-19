"""
Celery tasks for engagement event tracking and cleanup.
Handles open tracking, click tracking, and unsubscribe events.
"""
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, and_

from app.core.celery import celery_app
from app.core.config import settings
from app.infrastructure.database.models import EmailEvent, CampaignRecipient

logger = logging.getLogger(__name__)


async def get_async_session():
    """Create async database session for Celery tasks."""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        return session


@celery_app.task(name="app.tasks.events.log_email_open")
def log_email_open_task(campaign_recipient_id: str, user_agent: str = "", ip_address: str = ""):
    """
    Asynchronous task to log an email open event.
    
    Args:
        campaign_recipient_id: UUID of the campaign recipient
        user_agent: User agent string from the request
        ip_address: IP address from which the pixel was fetched
    """
    import asyncio
    
    async def _log():
        async_session = await get_async_session()
        try:
            # Fetch the campaign recipient
            result = await async_session.execute(
                select(CampaignRecipient).where(CampaignRecipient.id == campaign_recipient_id)
            )
            recipient = result.scalars().first()
            
            if not recipient:
                logger.warning(f"Campaign recipient not found: {campaign_recipient_id}")
                return {"status": "failed", "reason": "Recipient not found"}
            
            # Create email event
            event = EmailEvent(
                campaign_recipient_id=campaign_recipient_id,
                event_type="open",
                occurred_at=datetime.now(timezone.utc),
                user_agent=user_agent,
                ip_address=ip_address,
            )
            async_session.add(event)
            
            # Mark recipient as opened (if not already)
            if not recipient.opened_at:
                recipient.opened_at = datetime.now(timezone.utc)
            
            await async_session.commit()
            logger.info(f"Logged open event for {campaign_recipient_id}")
            return {"status": "success", "event_type": "open"}
        except Exception as exc:
            logger.exception(f"Error logging open event: {exc}")
            await async_session.rollback()
            return {"status": "failed", "error": str(exc)}
        finally:
            await async_session.close()
    
    return asyncio.run(_log())


@celery_app.task(name="app.tasks.events.log_email_click")
def log_email_click_task(campaign_recipient_id: str, clicked_url: str, user_agent: str = "", ip_address: str = ""):
    """
    Asynchronous task to log an email click event.
    
    Args:
        campaign_recipient_id: UUID of the campaign recipient
        clicked_url: The original URL that was clicked
        user_agent: User agent string from the request
        ip_address: IP address from which the click was made
    """
    import asyncio
    
    async def _log():
        async_session = await get_async_session()
        try:
            # Fetch the campaign recipient
            result = await async_session.execute(
                select(CampaignRecipient).where(CampaignRecipient.id == campaign_recipient_id)
            )
            recipient = result.scalars().first()
            
            if not recipient:
                logger.warning(f"Campaign recipient not found: {campaign_recipient_id}")
                return {"status": "failed", "reason": "Recipient not found"}
            
            # Create email event
            event = EmailEvent(
                campaign_recipient_id=campaign_recipient_id,
                event_type="click",
                occurred_at=datetime.now(timezone.utc),
                user_agent=user_agent,
                ip_address=ip_address,
                metadata={"clicked_url": clicked_url},
            )
            async_session.add(event)
            
            # Mark recipient as clicked (if not already)
            if not recipient.clicked_at:
                recipient.clicked_at = datetime.now(timezone.utc)
            
            await async_session.commit()
            logger.info(f"Logged click event for {campaign_recipient_id} on {clicked_url}")
            return {"status": "success", "event_type": "click", "url": clicked_url}
        except Exception as exc:
            logger.exception(f"Error logging click event: {exc}")
            await async_session.rollback()
            return {"status": "failed", "error": str(exc)}
        finally:
            await async_session.close()
    
    return asyncio.run(_log())


@celery_app.task(name="app.tasks.events.log_unsubscribe")
def log_unsubscribe_task(campaign_recipient_id: str, reason: str = ""):
    """
    Asynchronous task to log an unsubscribe event.
    
    Args:
        campaign_recipient_id: UUID of the campaign recipient
        reason: Reason for unsubscribe (optional)
    """
    import asyncio
    
    async def _log():
        async_session = await get_async_session()
        try:
            # Fetch the campaign recipient
            result = await async_session.execute(
                select(CampaignRecipient).where(CampaignRecipient.id == campaign_recipient_id)
            )
            recipient = result.scalars().first()
            
            if not recipient:
                logger.warning(f"Campaign recipient not found: {campaign_recipient_id}")
                return {"status": "failed", "reason": "Recipient not found"}
            
            # Create email event
            event = EmailEvent(
                campaign_recipient_id=campaign_recipient_id,
                event_type="unsubscribe",
                occurred_at=datetime.now(timezone.utc),
                metadata={"reason": reason} if reason else None,
            )
            async_session.add(event)
            
            # Mark contact as unsubscribed
            recipient.unsubscribed = True
            recipient.unsubscribed_at = datetime.now(timezone.utc)
            
            await async_session.commit()
            logger.info(f"Logged unsubscribe event for {campaign_recipient_id}")
            return {"status": "success", "event_type": "unsubscribe"}
        except Exception as exc:
            logger.exception(f"Error logging unsubscribe event: {exc}")
            await async_session.rollback()
            return {"status": "failed", "error": str(exc)}
        finally:
            await async_session.close()
    
    return asyncio.run(_log())


@celery_app.task(name="app.tasks.events.cleanup_old_engagement_events")
def cleanup_old_engagement_events_task():
    """
    Celery Beat scheduled task to clean up old engagement events.
    Removes events older than 90 days to maintain database performance.
    """
    import asyncio
    
    async def _cleanup():
        async_session = await get_async_session()
        try:
            # Calculate cutoff date (90 days ago)
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
            
            # Delete old events
            result = await async_session.execute(
                delete(EmailEvent).where(EmailEvent.occurred_at < cutoff_date)
            )
            await async_session.commit()
            
            deleted_count = result.rowcount
            logger.info(f"Cleaned up {deleted_count} old engagement events before {cutoff_date}")
            return {"status": "success", "deleted_count": deleted_count}
        except Exception as exc:
            logger.exception(f"Error cleaning up events: {exc}")
            await async_session.rollback()
            return {"status": "failed", "error": str(exc)}
        finally:
            await async_session.close()
    
    return asyncio.run(_cleanup())
