import os
import requests
import asyncio
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError

class TelegramChannel:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("CHAT_ID")
        self.bot = Bot(token=self.token)

    def send_message(self, text):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)
            )
            return "Message sent successfully on Telegram"
        except TelegramError as e:
            return f"Failed to send message: {str(e)}"

    def receive_messages(self, after_timestamp):
        try:
            loop = asyncio.get_event_loop()
            updates = loop.run_until_complete(self.bot.get_updates())
            new_messages = []
            for update in updates:
                if isinstance(update, Update) and update.message:
                    message = update.message
                    if message.date.timestamp() > after_timestamp:
                        new_messages.append({
                            "text": message.text,
                            "date": message.date.strftime("%Y-%m-%d %H:%M"),
                        })
            return new_messages
        except TelegramError as e:
            return f"Failed to retrieve messages: {str(e)}"
