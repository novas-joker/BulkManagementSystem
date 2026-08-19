"""
Celery worker entry point.
Run with: celery -A app.workers.celery_worker worker --loglevel=info
"""
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import celery app
from app.core.celery import celery_app
from app.tasks import *  # noqa: F401, F403

logger.info("Celery worker initialized and ready to process tasks")

if __name__ == "__main__":
    sys.argv[0] = "celery"
    celery_app.start()
