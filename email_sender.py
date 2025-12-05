# email_sender.py
# Final sendgrid wrapper — robust, minimal, explicit arguments.
import os
import json
from typing import Optional, Dict, Any

import sendgrid
from sendgrid.helpers.mail import Mail

def send_email(
    to: str,
    subject: str,
    body: str,
    is_html: bool = False,
    from_email: str = "sales@ventilengineering.com",
    from_name: str = "RFQ Automation System",
    reply_to: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send email using SendGrid.
    - to: single recipient email (string). If you need multiple, pass comma-separated and call split in router.
    - body: html or plain text depending on is_html.
    - reply_to: optional reply-to email address (string).
    Returns dict with status_code, body, headers for debugging.
    """

    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key:
        return {"status_code": 500, "error": "missing SENDGRID_API_KEY"}

    sg = sendgrid.SendGridAPIClient(api_key=api_key)

    # Build Mail object using template-friendly inputs
    # Use raw strings for from/to — SendGrid helper accepts string addresses.
    # Put html_content when is_html True else plain_text_content.
    mail_kwargs = {
        "from_email": {"email": from_email, "name": from_name},
        "subject": subject,
        "personalizations": [
            {
                "to": [{"email": to}],
            }
        ]
    }

    if is_html:
        mail_kwargs["html_content"] = body
        mail_kwargs["plain_text_content"] = None
    else:
        mail_kwargs["plain_text_content"] = body
        mail_kwargs["html_content"] = None

    # Add optional reply_to
    if reply_to:
        mail_kwargs["reply_to"] = {"email": reply_to}

    # Construct Mail via raw dict to avoid mismatched helper signatures across sendgrid versions
    mail = Mail(**mail_kwargs)

    resp = sg.client.mail.send.post(request_body=mail.get())
    # Normalize response
    try:
        headers = dict(resp.headers)
    except Exception:
        headers = {}

    return {
        "status_code": getattr(resp, "status_code", None),
        "body": getattr(resp, "body", None) if getattr(resp, "body", None) else "",
        "headers": headers
    }
