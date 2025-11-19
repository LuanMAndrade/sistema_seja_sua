"""
Management command to sync calendar events with Google Calendar
"""
from django.core.management.base import BaseCommand
from calendar_app.models import CalendarEvent
from calendar_app.google_calendar import GoogleCalendarService


class Command(BaseCommand):
    help = 'Sync calendar events with Google Calendar API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sync all events (not just pending ones)',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        sync_all = options.get('all', False)

        self.stdout.write(self.style.WARNING('Starting calendar sync with Google Calendar...'))

        google_service = GoogleCalendarService()

        if not google_service.service:
            self.stdout.write(
                self.style.ERROR('Google Calendar service not available. Please configure credentials.')
            )
            return

        # Get events to sync
        if sync_all:
            events = CalendarEvent.objects.filter(sync_enabled=True)
        else:
            # Only sync events that haven't been synced or need updating
            events = CalendarEvent.objects.filter(
                sync_enabled=True,
                google_event_id=''
            )

        total_events = events.count()
        synced_count = 0
        error_count = 0

        for event in events:
            try:
                success = google_service.sync_event(event)
                if success:
                    synced_count += 1
                    if verbose:
                        self.stdout.write(f"  ✓ Synced: {event.title}")
                else:
                    error_count += 1
                    if verbose:
                        self.stdout.write(f"  ✗ Failed: {event.title}")
            except Exception as e:
                error_count += 1
                if verbose:
                    self.stdout.write(f"  ✗ Error syncing {event.title}: {e}")

        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(
                    f'Sync completed with errors: {synced_count}/{total_events} synced, {error_count} errors'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Sync completed successfully: {synced_count}/{total_events} events synced'
                )
            )
