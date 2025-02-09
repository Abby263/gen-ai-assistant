from datetime import datetime, timedelta
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.utils import get_credentials

class AddEventToCalendarInput(BaseModel):
    title: str = Field(description="Title of the event")
    description: str = Field(description="Description of the event")
    start_time: str = Field(description="Start time of the event")

@tool("AddEventToCalendar", args_schema=AddEventToCalendarInput)
@traceable(run_type="tool", name="AddEventToCalendar")
def add_event_to_calendar(title: str, description: str, start_time: str):
    "Use this to create a new event in my calendar"
    try:
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)

        # Convert the string to a datetime object
        event_datetime = datetime.fromisoformat(start_time)

        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': event_datetime.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (event_datetime + timedelta(hours=1)).isoformat(),
                'timeZone': 'UTC',
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created successfully. Event ID: {event.get('id')}"

    except HttpError as error:
        return f"An error occurred: {error}"