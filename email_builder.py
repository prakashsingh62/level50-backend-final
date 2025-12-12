import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -------------------------------------------------------------------
# LEVEL-70 EMAIL BUILDER WITH CONFIRMATION GATE
# -------------------------------------------------------------------
# This file has TWO responsibilities:
#
# 1) prepare_email(payload)  → ONLY prepares email (does NOT send)
# 2) send_email(prepared)    → Sends ONLY after user confirms "SEND NOW"
#
# No email is ever auto-sent. Full control stays with user.
# -------------------------------------------------------------------


# -------------------------------------------------------------------
# PREPARE EMAIL (SAFE MODE)
# -------------------------------------------------------------------

def prepare_email(mail_payload: dict):
    """
    mail_payload = {
        "to": "...",
        "subject": "...",
        "body": "...",
        "rfq": "123",
        "uid": "456"
    }

    RETURNS:
    {
        "status": "awaiting_confirmation",
        "email_ready": True,
        "payload": { ... }   <-- used later by send_email()
    }
    """

    required_fields = ["to", "subject", "body"]

    for f in required_fields:
        if f not in mail_payload or not mail_payload[f]:
            return {
                "status": "error",
                "email_ready": False,
                "error": f"Missing field: {f}",
                "payload": {}
            }

    # DO NOT SEND — JUST PREPARE
    return {
        "status": "awaiting_confirmation",
        "email_ready": True,
        "payload": mail_payload
    }


# -------------------------------------------------------------------
# SEND EMAIL (ONLY AFTER USER CONFIRMATION)
# -------------------------------------------------------------------

def send_email(prepared_email: dict, smtp_config: dict):
    """
    prepared_email = {
        "to": "...",
        "subject": "...",
        "body": "...",
        "rfq": "...",
        "uid": "..."
    }

    smtp_config = {
        "server": "...",
        "port": 587,
        "username": "...",
        "password": "..."
    }

    This function sends email ONLY after user says:
        → "SEND NOW"
    """

    to_addr = prepared_email.get("to", "")
    subject = prepared_email.get("subject", "")
    body = prepared_email.get("body", "")

    if not to_addr:
        return {
            "status": "error",
            "error": "Missing recipient email address"
        }

    msg = MIMEMultipart()
    msg["From"] = smtp_config["username"]
    msg["To"] = to_addr
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_config["server"], smtp_config["port"])
        server.starttls()
        server.login(smtp_config["username"], smtp_config["password"])
        server.sendmail(smtp_config["username"], to_addr, msg.as_string())
        server.quit()

        return {
            "status": "sent",
            "to": to_addr,
            "subject": subject
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
