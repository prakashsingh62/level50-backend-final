import sendgrid
from sendgrid.helpers.mail import Mail
from config import SENDGRID_API_KEY, SENDGRID_FROM_EMAIL

def send_email(to_emails, subject, html_content):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

    email = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=to_emails,
        subject=subject,
        html_content=html_content
    )

    response = sg.send(email)
    return response.status_code
