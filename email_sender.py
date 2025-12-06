import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(html, recipients):
    """
    Generic mail sender.
    No imports from daily_sender to avoid circular import.
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Level-51 RFQ Report"
    msg["From"] = "sales@ventilengineering.com"
    msg["To"] = ", ".join(recipients)

    part = MIMEText(html, "html")
    msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("sales@ventilengineering.com", "YOUR_APP_PASSWORD")
        server.sendmail(msg["From"], recipients, msg.as_string())

    return {"status": "sent"}