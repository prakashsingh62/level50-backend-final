import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

def send_email(to, subject, body, is_html=False):
    """
    Simple SendGrid email wrapper.
    Works for BOTH manual reminder & daily reminder.
    """

    if SENDGRID_API_KEY is None:
        return {"error": "Missing SENDGRID_API_KEY"}

    from_email = Email("rfq@ventilengineering.com")

    # If HTML → set content type accordingly
    if is_html:
        content = Content("text/html", body)
    else:
        content = Content("text/plain", body)

    message = Mail(
        from_email=from_email,
        to_emails=[to],
        subject=subject,
        plain_text_content=None,
        html_content=body if is_html else None
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return {
            "status": "sent",
            "code": response.status_code
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
