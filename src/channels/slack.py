import os
import requests
from datetime import datetime

class SlackChannel():
    def __init__(self):
        self.token = os.getenv("SLACK_BOT_TOKEN")
        self.channel_id = os.getenv("SLACK_CHANNEL_ID")

    def send_message(self, text):
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "channel": self.channel_id,
            "text": text
        }
        response = requests.post(url, json=payload, headers=headers).json()
        if not response.get("ok"):
            return "Failed to send message"
        return "Message sent successfully on Slack"

    def receive_messages(self, after_timestamp):
        url = "https://slack.com/api/conversations.history"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            "channel": self.channel_id,
            "oldest": after_timestamp
        }
        response = requests.get(url, headers=headers, params=params).json()
        if not response.get("ok"):
            return []

        new_messages = []
        for message in response.get("messages", []):
            if float(message["ts"]) > after_timestamp:
                new_messages.append({
                    "text": message["text"],
                    "date": datetime.fromtimestamp(float(message["ts"])).strftime("%Y-%m-%d %H:%M")
                })

        return new_messages