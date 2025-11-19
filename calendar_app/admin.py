from django.contrib import admin
from .models import CalendarEvent


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'event_type',
        'start_date',
        'start_time',
        'collection',
        'location',
        'sync_enabled',
        'last_synced'
    ]
    search_fields = ['title', 'description', 'location']
    list_filter = ['event_type', 'sync_enabled', 'all_day', 'start_date']
    readonly_fields = ['google_event_id', 'last_synced', 'created_at', 'updated_at', 'is_collection_milestone']
    date_hierarchy = 'start_date'

    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'event_type', 'collection', 'is_collection_milestone')
        }),
        ('Date & Time', {
            'fields': ('start_date', 'start_time', 'end_date', 'end_time', 'all_day')
        }),
        ('Location', {
            'fields': ('location',)
        }),
        ('Google Calendar Sync', {
            'fields': ('sync_enabled', 'google_event_id', 'last_synced'),
            'classes': ('collapse',)
        }),
        ('Display', {
            'fields': ('color',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Make collection-milestone events readonly for certain fields"""
        readonly = list(self.readonly_fields)
        if obj and obj.is_collection_milestone:
            # If it's a collection milestone, prevent editing dates
            readonly.extend(['start_date', 'end_date', 'event_type'])
        return readonly
