import os
from enum import Enum
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from notion_client import Client

class TaskStatus(Enum):
    NOT_STARTED = "Not started"
    IN_PROGRESS = "In progress"
    COMPLETED = "Done"

class AddTaskInTodoListInput(BaseModel):
    task: str = Field(description="Task to be added")
    date: str = Field(description="Date and time for the task (YYYY-MM-DD) (HH:MM)")

@tool("AddTaskInTodoList", args_schema=AddTaskInTodoListInput)
@traceable(run_type="tool", name="AddTaskInTodoList")
def add_task_in_todo_list(task: str, date: str):
    "Use this to add a new task to my todo list"
    try:
        # Initialize the Notion client
        notion = Client(auth=os.getenv("NOTION_TOKEN"))

        # Create new task
        new_task = {
            "Title": {"title": [{"text": {"content": task}}]},
            "Status": {"status": {"name": TaskStatus.NOT_STARTED.value}},
        }
        if date:
            new_task["Date"] = {"date": {"start": date}}

        # Add task to Notion
        notion.pages.create(
            parent={"database_id": os.getenv("NOTION_DATABASE_ID")}, # Your database ID
            properties=new_task
        )

        return f"Task '{task}' added successfully to Todo list for {date}."
    except Exception as e:
        return f"An error occurred: {str(e)}"