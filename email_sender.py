import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(subject, body):
    """
    Level-50 SendGrid Email Sender
    Uses API Key + Verified Sender (no SMTP)
    Sends to MULTIPLE recipients from ENV
    """

    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("SENDGRID_FROM_EMAIL")
    recipients_env = os.getenv("EMAIL_RECIPIENTS", "")

    if not api_key:
        raise RuntimeError("Missing SENDGRID_API_KEY in environment variables")

    if not from_email:
        raise RuntimeError("Missing SENDGRID_FROM_EMAIL in environment variables")

    recipients = [r.strip() for r in recipients_env.split(",") if r.strip()]

    if not recipients:
        raise RuntimeError("EMAIL_RECIPIENTS is empty — cannot send email")

    message = Mail(
        from_email=from_email,
        to_emails=recipients,
        subject=subject,
        plain_text_content=body,
    )

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(f"SendGrid Email Status: {response.status_code}")
        return True

    except Exception as e:
        print(f"SendGrid Error: {e}")
        raise RuntimeError("Failed to send email via SendGrid")
