import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content


def send_email(to, subject, body, is_html=False):
    """
    Send email using SendGrid with support for both plain text and HTML.
    """

    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))

    # Select content type
    if is_html:
        content = Content("text/html", body)
    else:
        content = Content("text/plain", body)

    # Build email structure
    mail = Mail(
        from_email=Email("sales@ventilengineering.com", "RFQ Automation System"),
        to_emails=To(to),
        subject=subject,
        plain_text_content=None if is_html else body,
        html_content=body if is_html else None
    )

    # Send the email
    response = sg.client.mail.send.post(request_body=mail.get())

    # Return response for debugging
    return {
        "status_code": response.status_code,
        "body": str(response.body),
        "headers": dict(response.headers)
    }
