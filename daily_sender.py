import os
from sheet_reader import read_rows
from logic_engine import run_level50
from email_builder import build_email_content
from email_sender import send_email


def send_daily_email():
    rows = read_rows()

    # Run Level-50 Logic Engine
    result = run_level50(rows)
    sections = result["sections"]

    # Build HTML email content
    html = build_email_content(sections)

    # Recipient list from environment variable
    recipients = os.environ["EMAIL_RECIPIENTS"].split(",")

    return send_email(html, recipients)


def send_manual_reminder():
    # Manual reminder uses the same daily email logic
    return send_daily_email()
