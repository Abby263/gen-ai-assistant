import os
from twilio.rest import Client


class WhatsAppChannel:
    def __init__(self):
        """
        Initializes the WhatsAppChannel with Twilio client.
        """
        self.client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

    def send_message(self, to_number, body):
        """
        Sends a WhatsApp message.
        """
        try:
            message = self.client.messages.create(
                body=body,
                from_=os.getenv('FROM_WHATSAPP_NUMBER'),  # Should be your Twilio WhatsApp number with 'whatsapp:' prefix
                to=to_number # Ensure to prefix the number with 'whatsapp:'
            )
            return f"Message sent successfully with SID: {message.sid}"
        except Exception as e:
            return f"Failed to send message: {e}"

    def receive_messages(self):
        """
        Receiving messages is handled via webhooks.

        This method is not implemented because incoming WhatsApp messages are typically received through a webhook configured in the Twilio account. 
        The webhook sends an HTTP request to our server when a message is received.
        """
        pass 