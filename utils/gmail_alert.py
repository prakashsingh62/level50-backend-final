import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build

ALERT_TO = ["sales@ventilengineering.com"]

def send_audit_failure_email(creds, subject: str, body: str):
    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(body)
    message["to"] = ", ".join(ALERT_TO)
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()
