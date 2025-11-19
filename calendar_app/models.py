from django.db import models
from store_collections.models import Collection


class CalendarEvent(models.Model):
    """
    Calendar events for tracking collection milestones
    Automatically created when collections are saved
    Synced with Google Calendar API
    """
    EVENT_TYPES = [
        ('modeling', 'Modeling'),
        ('pilot_piece', 'Pilot Piece'),
        ('test_piece', 'Test Piece'),
        ('production', 'Production'),
        ('preparation', 'Preparation'),
        ('transportation', 'Transportation'),
        ('launch', 'Launch'),
        ('custom', 'Custom Event'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='custom')

    # Date and time
    start_date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)

    # Location
    location = models.CharField(max_length=500, blank=True)

    # Collection relationship (if event is related to a collection)
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name='events',
        null=True,
        blank=True
    )

    # Google Calendar sync
    google_event_id = models.CharField(max_length=200, blank=True, help_text="ID from Google Calendar")
    last_synced = models.DateTimeField(null=True, blank=True)
    sync_enabled = models.BooleanField(default=True, help_text="Sync with Google Calendar")

    # Additional fields
    all_day = models.BooleanField(default=False)
    color = models.CharField(max_length=7, blank=True, help_text="Event color (hex code)")

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date', 'start_time']
        verbose_name = "Calendar Event"
        verbose_name_plural = "Calendar Events"

    def __str__(self):
        if self.collection:
            return f"{self.title} - {self.collection.name} ({self.start_date})"
        return f"{self.title} ({self.start_date})"

    @property
    def is_collection_milestone(self):
        """Returns True if this event is a collection milestone"""
        return self.event_type != 'custom' and self.collection is not None
