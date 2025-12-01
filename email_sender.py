import os
import base64
import json
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_gmail_service():
    client_secret = json.loads(os.environ["CLIENT_SECRET_JSON"])
    token_data = json.loads(os.environ["TOKEN_JSON"])

    creds = Credentials(
        token=token_data["token"],
        refresh_token=token_data["refresh_token"],
        token_uri=token_data["token_uri"],
        client_id=client_secret["client_id"],
        client_secret=client_secret["client_secret"],
        scopes=[
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.compose",
            "https://www.googleapis.com/auth/gmail.modify",
        ],
    )

    return build("gmail", "v1", credentials=creds)


def send_email(to_email, subject, body):
    """Send email using Gmail API"""
    service = get_gmail_service()

    msg = MIMEText(body, "plain")
    msg["to"] = to_email
    msg["subject"] = subject

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

    return True
