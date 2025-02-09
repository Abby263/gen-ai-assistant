import os
from langsmith import traceable
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from tavily import TavilyClient

class SearchWebInput(BaseModel):
    query: str = Field(description="The search query string")

@tool("SearchWeb", args_schema=SearchWebInput)
@traceable(run_type="tool", name="SearchWeb")
def search_web(query: str, search_type: str = "basic", max_results: int = 5):
    """
    Use this tool to perform a web search based on the given query.
    """
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        search_response = client.search(query=query, search_depth=search_type, max_results=max_results)
        results = search_response["results"]

        if not results:
            return "No results found."

        formatted_output = ""
        for result in results:
            title = result.get('title', result.get('url', 'No Title'))
            url = result.get('url', 'No URL')
            content = result.get('content', 'No Content')

            formatted_output += f"Title: {title}\n"
            formatted_output += f"URL: {url}\n"
            formatted_output += f"Content: {content}\n"
            formatted_output += "-" * 20 + "\n"

        return formatted_output

    except Exception as e:
        return f"An error occurred: {e}"