from datetime import datetime, timezone
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.utils import get_credentials

class GetCalendarEventsInput(BaseModel):
    start_date: str = Field(description="Start date for fetching events")
    end_date: str = Field(description="End date for fetching events")

@tool("GetCalendarEvents", args_schema=GetCalendarEventsInput)
@traceable(run_type="tool", name="GetCalendarEvents")
def get_calendar_events(start_date: str, end_date: str):
    "Use this to get all calendars events between 2 time periods"
    try:
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)

        # Convert string times to datetime objects and ensure they're in UTC
        start_datetime = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
        end_datetime = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)

        # Format date-times in RFC3339 format
        start_rfc3339 = start_datetime.isoformat().replace('+00:00', 'Z')
        end_rfc3339 = end_datetime.isoformat().replace('+00:00', 'Z')

        events = service.events().list(
            calendarId='primary',
            timeMin=start_rfc3339,
            timeMax=end_rfc3339,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        if not events:
            return "No events found in the specified time range."

        event_list = []
        for event in events['items']:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_list.append(f"Event: {event['summary']}, Description: {event['description']}, Start: {start}")

        if event_list:
            return "\n".join(event_list)
        return "No event found for this dates"

    except HttpError as error:
        return f"An error occurred: {error}"