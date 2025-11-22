"""
Celery tasks for store_collections app
"""
from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_stock_daily_task(self):
    """
    Daily stock synchronization task
    Runs the management command to sync all pieces with Tiny ERP
    and record stock history
    """
    try:
        logger.info("Starting daily stock synchronization task...")

        # Call the management command
        call_command('sync_stock_daily', verbosity=1)

        logger.info("Daily stock synchronization completed successfully")
        return "Stock synchronization completed"

    except Exception as exc:
        logger.error(f"Error in daily stock synchronization: {exc}")
        # Retry after 5 minutes if failed
        raise self.retry(exc=exc, countdown=300)
