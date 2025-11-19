"""
Google Calendar API Integration
"""
import os
import logging
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarService:
    """
    Service for syncing events with Google Calendar
    """

    def __init__(self):
        self.creds = None
        self.service = None
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        token_path = 'token.json'
        credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')

        # The file token.json stores the user's access and refresh tokens
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # If there are no (valid) credentials available, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {e}")
                    self.creds = None

            if not self.creds and os.path.exists(credentials_path):
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                except Exception as e:
                    logger.error(f"Error authenticating with Google Calendar: {e}")
                    return

            # Save the credentials for the next run
            if self.creds:
                with open(token_path, 'w') as token:
                    token.write(self.creds.to_json())

        if self.creds:
            try:
                self.service = build('calendar', 'v3', credentials=self.creds)
                logger.info("Google Calendar service authenticated successfully")
            except Exception as e:
                logger.error(f"Error building Google Calendar service: {e}")
        else:
            logger.warning("Google Calendar credentials not configured")

    def create_event(self, calendar_event):
        """
        Create an event in Google Calendar
        Returns the Google event ID or None if failed
        """
        if not self.service:
            logger.error("Google Calendar service not available")
            return None

        try:
            # Build event data
            event_data = {
                'summary': calendar_event.title,
                'description': calendar_event.description,
                'start': {},
                'end': {},
            }

            # Handle all-day events vs timed events
            if calendar_event.all_day:
                event_data['start']['date'] = calendar_event.start_date.isoformat()
                end_date = calendar_event.end_date if calendar_event.end_date else calendar_event.start_date
                # For all-day events, end date is exclusive, so add 1 day
                end_date_exclusive = end_date + timedelta(days=1)
                event_data['end']['date'] = end_date_exclusive.isoformat()
            else:
                # Combine date and time for datetime events
                start_datetime = datetime.combine(
                    calendar_event.start_date,
                    calendar_event.start_time or datetime.min.time()
                )
                event_data['start']['dateTime'] = start_datetime.isoformat()
                event_data['start']['timeZone'] = 'America/Sao_Paulo'

                if calendar_event.end_date and calendar_event.end_time:
                    end_datetime = datetime.combine(calendar_event.end_date, calendar_event.end_time)
                else:
                    end_datetime = start_datetime + timedelta(hours=1)

                event_data['end']['dateTime'] = end_datetime.isoformat()
                event_data['end']['timeZone'] = 'America/Sao_Paulo'

            # Add location if provided
            if calendar_event.location:
                event_data['location'] = calendar_event.location

            # Create the event
            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event_data
            ).execute()

            logger.info(f"Created Google Calendar event: {event.get('id')}")
            return event.get('id')

        except HttpError as e:
            logger.error(f"Error creating Google Calendar event: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating Google Calendar event: {e}")
            return None

    def update_event(self, google_event_id, calendar_event):
        """
        Update an event in Google Calendar
        Returns True if successful, False otherwise
        """
        if not self.service:
            logger.error("Google Calendar service not available")
            return False

        try:
            # Build event data (same as create_event)
            event_data = {
                'summary': calendar_event.title,
                'description': calendar_event.description,
                'start': {},
                'end': {},
            }

            if calendar_event.all_day:
                event_data['start']['date'] = calendar_event.start_date.isoformat()
                end_date = calendar_event.end_date if calendar_event.end_date else calendar_event.start_date
                end_date_exclusive = end_date + timedelta(days=1)
                event_data['end']['date'] = end_date_exclusive.isoformat()
            else:
                start_datetime = datetime.combine(
                    calendar_event.start_date,
                    calendar_event.start_time or datetime.min.time()
                )
                event_data['start']['dateTime'] = start_datetime.isoformat()
                event_data['start']['timeZone'] = 'America/Sao_Paulo'

                if calendar_event.end_date and calendar_event.end_time:
                    end_datetime = datetime.combine(calendar_event.end_date, calendar_event.end_time)
                else:
                    end_datetime = start_datetime + timedelta(hours=1)

                event_data['end']['dateTime'] = end_datetime.isoformat()
                event_data['end']['timeZone'] = 'America/Sao_Paulo'

            if calendar_event.location:
                event_data['location'] = calendar_event.location

            # Update the event
            self.service.events().update(
                calendarId=self.calendar_id,
                eventId=google_event_id,
                body=event_data
            ).execute()

            logger.info(f"Updated Google Calendar event: {google_event_id}")
            return True

        except HttpError as e:
            logger.error(f"Error updating Google Calendar event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating Google Calendar event: {e}")
            return False

    def delete_event(self, google_event_id):
        """
        Delete an event from Google Calendar
        Returns True if successful, False otherwise
        """
        if not self.service:
            logger.error("Google Calendar service not available")
            return False

        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=google_event_id
            ).execute()

            logger.info(f"Deleted Google Calendar event: {google_event_id}")
            return True

        except HttpError as e:
            logger.error(f"Error deleting Google Calendar event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting Google Calendar event: {e}")
            return False

    def sync_event(self, calendar_event):
        """
        Sync a CalendarEvent to Google Calendar
        Creates if doesn't exist, updates if exists
        Returns True if successful, False otherwise
        """
        if not calendar_event.sync_enabled:
            logger.info(f"Sync disabled for event: {calendar_event.title}")
            return False

        try:
            if calendar_event.google_event_id:
                # Update existing event
                success = self.update_event(calendar_event.google_event_id, calendar_event)
            else:
                # Create new event
                google_event_id = self.create_event(calendar_event)
                if google_event_id:
                    calendar_event.google_event_id = google_event_id
                    calendar_event.last_synced = datetime.now()
                    calendar_event.save(update_fields=['google_event_id', 'last_synced'])
                    success = True
                else:
                    success = False

            if success:
                calendar_event.last_synced = datetime.now()
                calendar_event.save(update_fields=['last_synced'])

            return success

        except Exception as e:
            logger.error(f"Error syncing event {calendar_event.id}: {e}")
            return False
