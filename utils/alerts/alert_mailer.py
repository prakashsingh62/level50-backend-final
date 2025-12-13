# =========================================
# Failure Alert Mailer (Level-80)
# =========================================

import os
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone, timedelta

# -------- ENV (Railway-safe) --------
SMTP_HOST = os.getenv("ALERT_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("ALERT_SMTP_PORT", "587"))
ALERT_SENDER = os.getenv("ALERT_SENDER_EMAIL")
ALERT_PASSWORD = os.getenv("ALERT_SENDER_PASSWORD")
ALERT_RECIPIENTS = [
    e.strip() for e in os.getenv("ALERT_RECIPIENTS", "").split(",") if e.strip()
]

def _now_ist():
    return (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30))\
        .strftime("%d/%m/%Y %H:%M:%S IST")

def send_failure_alert(envelope: dict):
    """
    envelope keys used:
      run_id, status, rows_written, error_type, error_message,
      retry_count, next_retry_at, timestamp
    """
    if not (ALERT_SENDER and ALERT_PASSWORD and ALERT_RECIPIENTS):
        # Config missing → do NOT crash cron
        return

    subject = f"🚨 Level-80 DAILY FAILURE — {_now_ist().split()[0]}"

    body = f"""Level-80 Daily Automation FAILED

Run ID: {envelope.get('run_id')}
Timestamp: {envelope.get('timestamp')}
Status: {envelope.get('status')}

Error Type: {envelope.get('error_type')}
Error Message: {envelope.get('error_message')}

Rows Written: {envelope.get('rows_written')}
Retries Attempted: {envelope.get('retry_count')}
Next Retry At: {envelope.get('next_retry_at')}

System: Railway (Cron)
"""

    msg = EmailMessage()
    msg["From"] = ALERT_SENDER
    msg["To"] = ", ".join(ALERT_RECIPIENTS)
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(ALERT_SENDER, ALERT_PASSWORD)
        s.send_message(msg)
