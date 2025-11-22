"""
Celery configuration for store_management project
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store_management.settings')

app = Celery('store_management')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule configuration
app.conf.beat_schedule = {
    'sync-stock-daily': {
        'task': 'store_collections.tasks.sync_stock_daily_task',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight (00:00)
        'options': {
            'expires': 3600,  # Task expires after 1 hour if not executed
        },
    },
}

# Timezone configuration
app.conf.timezone = 'America/Sao_Paulo'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
