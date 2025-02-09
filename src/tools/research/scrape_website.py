import re
import html2text
import requests
from bs4 import BeautifulSoup
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class ScrapeWebsiteInput(BaseModel):
    url: str = Field(description="The URL of the website to scrape.")

@tool("ScrapeWebsite", args_schema=ScrapeWebsiteInput)
@traceable(run_type="tool", name="ScrapeWebsite")
def scrape_website_to_markdown(url: str) -> str:
    """
    Use this tool to scrape a website based on its URL.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate"
    }

    # Make the HTTP request
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the URL. Status code: {response.status_code}")

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")
    html_content = soup.prettify() 

    # Convert HTML to markdown
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.ignore_tables = True
    markdown_content = h.handle(html_content)

    # Clean up excess newlines
    markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)
    markdown_content = markdown_content.strip()

    return markdown_content