import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(html, recipients):
    """
    Send email using Brevo SMTP.
    """

    smtp_server = os.environ["BREVO_SMTP_SERVER"]
    smtp_port = int(os.environ["BREVO_SMTP_PORT"])
    smtp_login = os.environ["BREVO_SMTP_LOGIN"]
    smtp_password = os.environ["BREVO_SMTP_PASSWORD"]

    sender = smtp_login  # Brevo: sender must be same as login ID

    for to_email in recipients:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Daily RFQ Reminder Report"
        msg["From"] = sender
        msg["To"] = to_email

        msg.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_login, smtp_password)
                server.sendmail(sender, to_email, msg.as_string())

        except Exception as e:
            return {"status": "error", "detail": str(e)}

    return {"status": "sent", "recipients": recipients}
