from django.apps import AppConfig


class CalendarAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calendar_app'

    def ready(self):
        """Import signals when app is ready"""
        import calendar_app.signals
