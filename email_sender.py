import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body):
    """
    Level-50 email sender
    Sends to MULTIPLE recipients (from ENV)
    Uses Gmail SMTP + App Password (stable on Railway)
    """

    sender = os.getenv("SMTP_EMAIL")  # your Gmail address
    app_password = os.getenv("SMTP_APP_PASSWORD")  # 16-char Gmail app password

    if not sender or not app_password:
        raise RuntimeError("Missing SMTP_EMAIL or SMTP_APP_PASSWORD environment variables")

    # Recipients list (comma separated)
    recipients_env = os.getenv("EMAIL_RECIPIENTS", "")
    recipients = [r.strip() for r in recipients_env.split(",") if r.strip()]

    if not recipients:
        raise RuntimeError("EMAIL_RECIPIENTS is empty — cannot send")

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, app_password)
        server.sendmail(sender, recipients, msg.as_string())

    return True
