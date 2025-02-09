import os
import re
from langsmith import traceable
from pydantic import BaseModel
from langchain_core.tools import tool
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class GetMessagesInput(BaseModel):
    """Input schema for get_messages tool."""
    pass  # No input needed for this tool

@tool("GetSlackMessages", args_schema=GetMessagesInput)
@traceable(run_type="tool", name="GetSlackMessages")
def get_slack_messages():
    """
    Use this tool to retrieve unread messages from Slack.
    """
    try:
        messages = []
        # Get unread DMs
        client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        dms_response = client.conversations_list(types="im", exclude_archived=True)
        for channel in dms_response["channels"]:
          try:
            history = client.conversations_history(channel=channel["id"], unreads_only=True, include_all_metadata=True, limit=10)
            for message in history["messages"]:
              if message.get("unread_count", 0) > 0 or message.get("reply_count", 0) > 0:
                # Fetch user details including real name
                user_info = client.users_info(user=message["user"])
                user_name = user_info["user"]["real_name"] if user_info["user"]["real_name"] else user_info["user"]["name"]

                messages.append(
                  {
                      "channel": channel["id"],
                      "channel_type": "DM",
                      "user": user_name,
                      "user_id": message["user"],
                      "message": message["text"]
                  }
                )
          except SlackApiError as e:
            if e.response["error"] == "not_in_channel":
              pass
            else:
              print(f"Error fetching history for channel {channel['id']}: {e}")

        # Get unread mentions in channels
        channels_response = client.conversations_list(types="public_channel,private_channel", exclude_archived=True)
        for channel in channels_response["channels"]:
          try:
            history = client.conversations_history(channel=channel["id"], unreads_only=True, include_all_metadata=True, limit=10)
            for message in history["messages"]:
                if "unread_count" in message or "reply_count" in message:
                    mentions = re.findall(r"<@(\w+)>", message["text"])  # Find all mentions in the message
                    if mentions:
                        # Fetch user details including real name
                        user_info = client.users_info(user=message["user"])
                        user_name = user_info["user"]["real_name"] if user_info["user"]["real_name"] else user_info["user"]["name"]
                        messages.append(
                            {
                                "channel": channel["name"],
                                "channel_type": "channel",
                                "user": user_name,
                                "user_id": message["user"],
                                "message": message["text"],
                            }
                        )
          except SlackApiError as e:
            if e.response["error"] == "not_in_channel":
              pass
            else:
              print(f"Error fetching history for channel {channel['name'] or channel['id']}: {e}")
              
        if not messages:
          return "No messages found."

        return messages

    except SlackApiError as e:
        print(f"Error fetching messages: {e}")
        return f"Error fetching messages: {e}"