import os
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SendSlackMessageInput(BaseModel):
    channel: str = Field(..., description="The ID or name of the channel to send the message to.")
    message: str = Field(..., description="The message to send.")

@tool("SendSlackMessage", args_schema=SendSlackMessageInput)
@traceable(run_type="tool", name="SendSlackMessage")
def send_slack_message(channel: str, message: str):
    """
    Use this tool to send a message to a specific Slack channel.
    """
    try:
        client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        response = client.chat_postMessage(channel=channel, text=message)
        if response["ok"]:
            return f"Message sent to #{channel} successfully."
        else:
            return f"Error sending message: {response['error']}"
    except SlackApiError as e:
        print(f"Error sending message: {e}")
        return f"Error sending message: {e}"