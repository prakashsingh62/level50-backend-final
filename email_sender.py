import os
import requests

def send_email(html, recipients):
    api_key = os.environ["BREVO_API_KEY"]
    sender = {"email": os.environ["BREVO_FROM_EMAIL"]}

    data = {
        "sender": sender,
        "to": [{"email": r} for r in recipients],
        "subject": "Level-50 Report",
        "htmlContent": html
    }

    res = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        json=data,
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
    )

    if res.status_code >= 400:
        return {"status": "error", "detail": res.text}

    return {"status": "sent", "detail": res.json()}
