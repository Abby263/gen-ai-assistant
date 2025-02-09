import os
import smtplib
from langsmith import traceable
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class SendEmailInput(BaseModel):
    to: str = Field(description="Email of the recipient")
    subject: str = Field(description="Subject of the email")
    body: str = Field(description="Body of the email")

@tool("SendEmail", args_schema=SendEmailInput)
@traceable(run_type="tool", name="SendEmail")
def send_email(to: str, subject: str, body: str):
    "Use this to send an email to my contacts"
    try:
        sender_email = os.getenv("GMAIL_MAIL")
        app_password = os.getenv("GMAIL_APP_PASSWORD")

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, app_password)
        text = msg.as_string()
        server.sendmail(sender_email, to, text)
        server.quit()
        return "Email sent successfully."
    except Exception as e:
        return f"Email was not sent successfully, error: {e}"