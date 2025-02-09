import os 
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/contacts.readonly",
    'https://www.googleapis.com/auth/gmail.readonly'
]

def get_current_date_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M")
        
def get_credentials():
    """
    Get and refresh Google Contacts API credentials
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def extract_provider_and_model(model_string: str):
    return model_string.split("/", 1)

def get_llm_by_provider(model_string, temperature=0.1):
    llm_provider, model = extract_provider_and_model(model_string)
    # Else find provider
    if llm_provider == "openai":
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model=model, temperature=temperature)
    elif llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        llm = ChatAnthropic(model=model, temperature=temperature)  # Use the correct model name
    elif llm_provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)  # Correct model name
    elif llm_provider == "groq":
        from langchain_groq import ChatGroq
        llm = ChatGroq(model=model, temperature=temperature)
    # ... add elif blocks for other providers ...
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")
    return llm