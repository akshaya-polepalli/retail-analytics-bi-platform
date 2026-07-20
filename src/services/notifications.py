import smtplib
from email.message import EmailMessage

import requests

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def send_slack_message(message: str) -> None:
    if not settings.SLACK_WEBHOOK_URL:
        logger.info("Slack webhook not configured; skipping notification")
        return

    response = requests.post(
        settings.SLACK_WEBHOOK_URL,
        json={"text": message},
        timeout=10,
    )
    response.raise_for_status()


def send_email_report(subject: str, body: str) -> None:
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.REPORT_EMAIL_TO]):
        logger.info("Email settings not configured; skipping notification")
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.SMTP_USER
    message["To"] = settings.REPORT_EMAIL_TO
    message.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, int(settings.SMTP_PORT or 587)) as server:
        server.starttls()
        if settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(message)
