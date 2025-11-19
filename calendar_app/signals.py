from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import CalendarEvent
from .google_calendar import GoogleCalendarService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CalendarEvent)
def calendar_event_saved(sender, instance, created, **kwargs):
    """
    Triggered when a CalendarEvent is saved.
    Syncs the event to Google Calendar if sync is enabled.
    """
    if not instance.sync_enabled:
        return

    try:
        google_service = GoogleCalendarService()
        google_service.sync_event(instance)
    except Exception as e:
        logger.error(f"Error syncing event {instance.id} to Google Calendar: {e}")


@receiver(pre_delete, sender=CalendarEvent)
def calendar_event_deleted(sender, instance, **kwargs):
    """
    When a calendar event is deleted, delete it from Google Calendar too.
    """
    if not instance.sync_enabled or not instance.google_event_id:
        return

    try:
        google_service = GoogleCalendarService()
        google_service.delete_event(instance.google_event_id)
    except Exception as e:
        logger.error(f"Error deleting event {instance.id} from Google Calendar: {e}")
