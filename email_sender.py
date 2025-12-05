import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, ReplyTo


def send_email(to, subject, body_html, is_html=False):
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))

    # Plain text fallback
    plain_fallback = "Your RFQ reminder is available. Please check HTML format."

    # Verified SendGrid sender
    verified_sender = "rfq-system@sendgrid.me"

    # Create message WITHOUT reply_to inside constructor
    message = Mail(
        from_email=Email(verified_sender, "RFQ Automation System"),
        to_emails=To(to),
        subject=subject,
    )

    # NOW add reply_to properly (this works on all versions)
    message.reply_to = ReplyTo("sales@ventilengineering.com")

    # Add content
    message.add_content(Content("text/plain", plain_fallback))
    if is_html:
        message.add_content(Content("text/html", body_html))
    else:
        message.add_content(Content("text/plain", body_html))

    response = sg.client.mail.send.post(request_body=message.get())
    return {
        "status_code": response.status_code,
        "body": str(response.body),
        "headers": dict(response.headers)
    }
