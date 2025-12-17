import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

ADMIN_USER = os.getenv("GMAIL_ADMIN_USER")  # eg: sales@ventilengineering.com
CLIENT_SECRET_JSON = os.getenv("CLIENT_SECRET_JSON")


def _get_gmail_service():
    if not CLIENT_SECRET_JSON:
        raise RuntimeError("CLIENT_SECRET_JSON missing")

    info = json.loads(CLIENT_SECRET_JSON)

    creds = service_account.Credentials.from_service_account_info(
        info,
        scopes=SCOPES,
        subject=ADMIN_USER  # 👈 DOMAIN WIDE DELEGATION
    )

    return build("gmail", "v1", credentials=creds)


def send_vendor_email(rfq: dict):
    """
    Gmail API based vendor email sender
    MUST exist for pipeline_engine import
    """

    vendor_email = rfq.get("vendor_email")
    if not vendor_email:
        return "NO_VENDOR_EMAIL"

    subject = f"RFQ Follow-up | {rfq.get('rfq_no')}"
    body = f"""
RFQ No : {rfq.get('rfq_no')}
UID    : {rfq.get('uid')}
Customer: {rfq.get('customer')}

Please share your quotation / update.
"""

    message = f"""To: {vendor_email}
Subject: {subject}

{body}
"""

    raw = (
        message
        .encode("utf-8")
        .decode("utf-8")
    )

    service = _get_gmail_service()
    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

    return "MAIL_SENT"
