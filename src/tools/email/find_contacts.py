import re
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.utils import get_credentials

class FindContactEmailInput(BaseModel):
    name: str = Field(description="Name of the contact")

@tool("FindContactEmail", args_schema=FindContactEmailInput)
@traceable(run_type="tool", name="FindContactEmail")
def find_contact_email(name: str):
    "Use this to get the a contact email from his name"
    try:
        creds = get_credentials()
        service = build('people', 'v1', credentials=creds)

        # Search for the contact
        results = service.people().searchContacts(
            query=name,
            readMask='names,phoneNumbers,emailAddresses'
        ).execute()

        connections = results.get('results', [])

        if not connections:
            return f"No contact found with the name: {name}"

        matching_contacts = []

        for connection in connections:
            contact = connection['person']
            names = contact.get('names', [])
            if names:
                unstructured_name = names[0].get('unstructuredName', '').lower()
                # Prepare regex to identify first and last names
                first_name_pattern = r'^(\w+)'  # Match first word
                last_name_pattern = r'(\w+)$'   # Match last word
                first_match = re.search(first_name_pattern, unstructured_name)
                last_match = re.search(last_name_pattern, unstructured_name)

                if (first_match and name.lower() == first_match.group(1)) or \
                    (last_match and name.lower() == last_match.group(1)) or \
                    (name.lower() == unstructured_name):
                    full_name = names[0].get('displayName', 'N/A')
                    phone_numbers = [phone.get('value', 'N/A') for phone in contact.get('phoneNumbers', [])]
                    emails = [email.get('value', 'N/A') for email in contact.get('emailAddresses', [])]

                    matching_contacts.append({
                        'name': full_name,
                        'phone_numbers': phone_numbers,
                        'emails': emails
                    })

        if not matching_contacts:
            return f"No contact found with the matching criteria: {name}"

        return str(matching_contacts)

    except HttpError as error:
        return f"An error occurred: {error}"