import os
from datetime import datetime
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from notion_client import Client


class GetMyTodoListInput(BaseModel):
    date: str = Field(description="Date for which to retrieve tasks (YYYY-MM-DD)")

@tool("GetMyTodoList", args_schema=GetMyTodoListInput)
@traceable(run_type="tool", name="GetMyTodoList")
def get_my_todo_list(date: str):
    "Use this to get all tasks from my todo list"
    try:
        # Parse the target date string into a datetime object
        try:
            target_datetime = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print(f"Error: Invalid date format. Please use YYYY-MM-DD format.")
            return []

        # Set up the filter to get tasks due on the target date
        filter_params = {
            "filter": {
                "property": "Date",
                "date": {
                    "equals": date
                }
            }
        }
        
        # Initialize the Notion client
        notion = Client(auth=os.getenv("NOTION_TOKEN"))
        results = notion.databases.query(
            database_id=os.getenv("NOTION_DATABASE_ID"), # Your database ID
            **filter_params
        )
        tasks = []

        for page in results["results"]:
            due_date = page["properties"]["Date"]["date"]["start"]

            # Parse the due date from Notion
            due_datetime = datetime.fromisoformat(due_date.replace("Z", "+00:00"))

            # Check if the task is due on the target date
            if due_datetime.date() == target_datetime.date():
                task = {
                    "id": page["id"],
                    "title": page["properties"]["Title"]["title"][0]["text"]["content"],
                    "status": page["properties"]["Status"]["status"]["name"],
                    "due_date": due_date
                }
                tasks.append(task)

        if tasks:
            return f"Todo list for {target_datetime}:\n" + "\n".join([str(task) for task in tasks])
        else:
            return f"No tasks found in Todo list for {target_datetime}."

    except Exception as e:
        return f"An error occurred: {str(e)}"