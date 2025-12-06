import os
import requests

def send_email(html, recipients):
    api_key = os.environ["BREVO_API_KEY"]

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    for to_email in recipients:
        data = {
            "sender": {"name": "RFQ System", "email": "no-reply@ventilengineering.com"},
            "to": [{"email": to_email}],
            "subject": "Daily RFQ Report",
            "htmlContent": html
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code >= 300:
            return {
                "status": "error",
                "detail": response.text
            }

    return {"status": "sent", "recipients": recipients}
