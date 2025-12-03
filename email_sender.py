import os
import requests

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM", "sales@ventilengineering.com")
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "")

def send_email(subject, body):
    if not SENDGRID_API_KEY:
        raise RuntimeError("SENDGRID_API_KEY is missing")

    if not EMAIL_RECIPIENTS:
        raise RuntimeError("EMAIL_RECIPIENTS is empty")

    recipients = [x.strip() for x in EMAIL_RECIPIENTS.split(",") if x.strip()]

    url = "https://api.sendgrid.com/v3/mail/send"

    data = {
        "personalizations": [{
            "to": [{"email": r} for r in recipients]
        }],
        "from": {
            "email": EMAIL_FROM,
            "name": "VENTIL ENGINEERING"
        },
        "subject": subject,
        "content": [{
            "type": "text/html",
            "value": body
        }]
    }

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code not in (200, 202):
        raise RuntimeError(f"SendGrid error: {response.status_code}, {response.text}")

    return {"status": "email_sent"}
