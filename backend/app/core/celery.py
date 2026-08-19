"""
Celery Application Configuration
Handles asynchronous task processing for email delivery, scheduling, and background jobs.
"""
from celery import Celery
from celery.schedules import crontab
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "mailforge",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Celery configuration
celery_app.conf.update(
    # Task configuration
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing and execution
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Retry policy
    task_default_retry_delay=60,
    task_max_retries=3,
    
    # Result backend configuration
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
        "retry_on_timeout": True,
    },
    
    # Beat scheduler configuration (for scheduled tasks)
    beat_scheduler="celery.beat:PersistentScheduler",
    
    # Logging
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
)

# Celery Beat Schedule - Scheduled Tasks
celery_app.conf.beat_schedule = {
    # Process queued campaigns every 5 minutes
    "process-queued-campaigns": {
        "task": "app.tasks.campaigns.process_queued_campaigns",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
        "options": {"queue": "default"},
    },
    # Retry failed emails every 10 minutes
    "retry-failed-emails": {
        "task": "app.tasks.campaigns.retry_failed_email_sends",
        "schedule": crontab(minute="*/10"),  # Every 10 minutes
        "options": {"queue": "default"},
    },
    # Cleanup old engagement events daily at 2 AM
    "cleanup-old-events": {
        "task": "app.tasks.events.cleanup_old_engagement_events",
        "schedule": crontab(hour=2, minute=0),  # 2:00 AM UTC daily
        "options": {"queue": "default"},
    },
}

if settings.is_development():
    logger.info("Celery configured in development mode with Redis broker")
else:
    logger.info("Celery configured in production mode")
