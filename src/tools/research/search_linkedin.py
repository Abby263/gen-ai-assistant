import json
import os
import re
import requests
import html2text
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from src.utils import get_llm_by_provider

def invoke_llm(system_prompt, user_message, model="openai/gpt-4o-mini"):
    # Get the LLM instance by provider
    llm = get_llm_by_provider(model, temperature=0.1)
    
    # Define the prompt template
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ])
    
    # Create and run the LLM chain
    chain = prompt_template | llm
    response = chain.invoke({})
    return response.content

def google_search(query):
    """
    Performs a Google search using the provided query.
    """
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': os.environ['SERPER_API_KEY'],
        'content-type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    results = response.json().get('organic', [])[:5] # Keep only 5 results
    
    # Extract only the title and link
    return [{"title": result["title"], "link": result["link"]} for result in results]

def extract_linkedin_url(search_results):
    EXTRACT_LINKEDIN_URL_PROMPT = """
    **Role:**  
    You are an expert in extracting LinkedIn URLs from Google search results, specializing in finding the correct personal LinkedIn URL.

    **Instructions:** 
    1. Find the LinkedIn URL of a specific person working at a specific company. 
    2. Output **only** the correct LinkedIn URL if found, nothing else.  
    3. If no valid URL exists, output **only** an empty string.  
    4. Only consider URLs with `"/in"`. Ignore those with `"/posts"` or `"/company"`.  
    """
    
    result = invoke_llm(
        system_prompt=EXTRACT_LINKEDIN_URL_PROMPT, 
        user_message=str(search_results)
    )
    return result

def scrape_linkedin(linkedin_url):
    """
    Scrapes the LinkedIn profile page and returns the HTML content.
    """
    # Set up the Chrome WebDriver with headless mode
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    
    # Launch Chrome
    driver = webdriver.Chrome(service=service, options=options)
    
    # Log in to LinkedIn
    driver.get("https://www.linkedin.com/login")
    time.sleep(5)
    username = driver.find_element(By.ID, "username")
    password = driver.find_element(By.ID, "password")
    username.send_keys(os.getenv("LINKEDIN_USERNAME"))  # Replace with your email
    password.send_keys(os.getenv("LINKEDIN_PASSWORD"))  # Replace with your password
    password.send_keys(Keys.RETURN)
    time.sleep(5)  # Wait for the login to complete

    # Go to a person's profile
    driver.get(linkedin_url)
    driver.implicitly_wait(5)
    
    # Get the page source
    html_content = driver.page_source
    
    driver.quit()
    
    # Convert HTML to markdown
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_tables = True
    markdown_content = h.handle(html_content)

    # Clean up excess newlines
    markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)
    markdown_content = markdown_content.strip()
    
    SUMMARIZE_LINKEDIN_PROFILE_PROMPT = """
    **Role:**  
    You are an expert at summarizing LinkedIn profiles, extracting the most relevant information.
    **Instructions:** 
    From the provided LinkedIn profile content, extract the following information: 
    1. Extract the information and summarize it in a clear and concise format.
    2. If some information is not available, omit it from the summary.
    """
    
    summary = invoke_llm(
        system_prompt=SUMMARIZE_LINKEDIN_PROFILE_PROMPT, 
        user_message=markdown_content
    )
    return summary

class SearchLinkedinInput(BaseModel):
    person_name: str = Field(
        default=None,
        description="The name of the person to search for on LinkedIn. Optional."
    )
    company_name: str = Field(
        description="The company name to search on LinkedIn."
    )

@tool("SearchLinkedin", args_schema=SearchLinkedinInput)
@traceable(run_type="tool", name="SearchLinkedin")
def search_linkedin_tool(person_name: str = None, company_name: str = ""):
    """
    Use this tool to search for a person or a company on LinkedIn.
    """
    if person_name:
        search_query = f"{person_name} {company_name} site:linkedin.com"
    else:
        search_query = f"{company_name} site:linkedin.com"

    search_results = google_search(search_query)
    linkedin_url = extract_linkedin_url(search_results)

    if linkedin_url:
        return scrape_linkedin(linkedin_url)
    else:
        return "LinkedIn profile not found."