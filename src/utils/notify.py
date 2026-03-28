import smtplib
import os
import logging
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def send_pipeline_notification(subject: str, body: str):
    """
    Sends an email alert regarding the book generation pipeline status.
    """
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    recipient = os.getenv("EDITOR_EMAIL")

    if not all([smtp_user, smtp_pass, recipient]):
        logger.error("Email notification skipped: SMTP credentials missing in .env")
        return False

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = f"| Media Marson | {subject}"
    msg["From"] = smtp_user
    msg["To"] = recipient

    try:
        # Using Gmail's SSL port 465
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logger.info(f"Notification sent: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        return False

if __name__ == "__main__":
    # Test notification
    send_pipeline_notification("System Test", "The notification utility is online.")