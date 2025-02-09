from datetime import datetime, timezone
from typing import Optional
from langsmith import traceable
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.utils import parsedate_to_datetime
from src.utils import get_credentials

class ReadEmailsInput(BaseModel):
    from_date: str = Field(description="From date for reading emails")
    to_date: str = Field(description="To date for reading emails. Always after from_date.")
    email: Optional[str] = Field(description="Email of the contact to read emails from")

@tool("ReadEmails", args_schema=ReadEmailsInput)
@traceable(run_type="tool", name="ReadEmails")
def read_emails(from_date: str, to_date: str, email: Optional[str] = None):
    "Use this to read emails from my inbox"
    try:
        creds = get_credentials()
        service = build('gmail', 'v1', credentials=creds)

        # Convert datetime objects to timestamps
        from_date = int(datetime.fromisoformat(from_date).timestamp())
        to_date = int(datetime.fromisoformat(to_date).timestamp())

        query = f'after:{from_date} before:{to_date}'
        if email:
            query += f' from:{email}'

        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])

        if not messages:
            return "No emails found in the specified time range."

        email_list = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()

            subject = next((header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject'), 'No Subject')
            from_email = next((header['value'] for header in msg['payload']['headers'] if header['name'] == 'From'), 'Unknown Sender')
            date = next((header['value'] for header in msg['payload']['headers'] if header['name'] == 'Date'), '')
            date_obj = parsedate_to_datetime(date)
            if date_obj.tzinfo is None:
                date_obj = date_obj.replace(tzinfo=timezone.utc)


            snippet = msg['snippet']
            email_list.append(f"From: {from_email}\nSubject: {subject}\nDate: {date}\nSnippet: {snippet}\n")

        return "\n".join(email_list)

    except HttpError as error:
        return f"An error occurred: {error}"