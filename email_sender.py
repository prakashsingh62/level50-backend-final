import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, ReplyTo


def send_email(to, subject, body_html, is_html=False):
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))

    # 1) Plain text fallback (massively improves inbox rate)
    plain_fallback = "Your RFQ reminder summary is available. Please view HTML version."

    # 2) Footer for compliance (required for inbox placement)
    footer_html = """
        <br><br>
        <hr>
        <p style="font-size:12px; color:#888;">
            Ventil Engineering Pvt. Ltd.<br>
            Automated RFQ Reminder System<br>
            If you no longer want to receive reminder emails, reply STOP.
        </p>
    """

    body_html = body_html + footer_html

    # 3) Verified FROM address (SendGrid-owned domain)
    verified_sender = "rfq-system@sendgrid.me"

    message = Mail(
        from_email=Email(verified_sender, "RFQ Automation System"),
        to_emails=To(to),
        subject=subject,
        reply_to=ReplyTo("sales@ventilengineering.com")  # When someone replies → goes to sales email
    )

    # Attach content properly
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
