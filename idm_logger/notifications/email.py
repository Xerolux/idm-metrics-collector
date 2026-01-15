import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .base import NotificationProvider
from ..config import config

logger = logging.getLogger(__name__)

class EmailProvider(NotificationProvider):
    @property
    def name(self) -> str:
        return "email"

    def send(self, message: str, **kwargs) -> bool:
        if not config.get("email.enabled", False):
            return False

        smtp_server = config.get("email.smtp_server")
        smtp_port = config.get("email.smtp_port", 587)
        username = config.get("email.username")
        password = config.get("email.password")
        sender = config.get("email.sender", username)
        recipients = config.get("email.recipients")

        if not smtp_server or not recipients:
             logger.error("Email SMTP server or recipients not configured")
             return False

        if isinstance(recipients, str):
            recipients = [x.strip() for x in recipients.split(",") if x.strip()]

        try:
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = kwargs.get('subject', 'IDM Metrics Notification')
            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                if username and password:
                    server.login(username, password)
                server.send_message(msg)
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
