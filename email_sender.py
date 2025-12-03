import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import SENDGRID_API_KEY, SENDGRID_FROM_EMAIL, EMAIL_RECIPIENTS
from logger import get_logger

logger = get_logger()

def send_email(subject, html_body):
    recipients = [x.strip() for x in EMAIL_RECIPIENTS.split(",") if x.strip()]

    if not recipients:
        logger.error("NO EMAIL RECIPIENTS FOUND — Email not sent.")
        return False

    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=recipients,
        subject=subject,
        html_content=html_body,
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Email sent → Status Code: {response.status_code}")
        return True

    except Exception as e:
        logger.error(f"send_email() failure: {str(e)}")
        return False
