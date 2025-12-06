import os
from sheet_reader import read_rows
from logic_engine import run_level50
from email_builder import build_email
from email_sender import send_email


def send_daily_email():
    rows = read_rows()

    # Level-50 logic output
    result = run_level50(rows)
    sections = result["sections"]

    # No autofix + alerts for now (basic mode)
    autofix = []
    alerts = []

    # Build final HTML
    html = build_email(result["summary"], sections, autofix, alerts)

    # Recipients
    recipients = os.environ["EMAIL_RECIPIENTS"].split(",")

    return send_email(html, recipients)


def send_manual_reminder():
    """
    Sends email instantly to sales@ventilengineering.com only
    (NOT the full daily mail recipients list)
    """
    rows = read_rows()
    result = run_level50(rows)
    sections = result["sections"]

    # Basic placeholders
    autofix = []
    alerts = []

    html = build_email(result["summary"], sections, autofix, alerts)

    return send_email(html, ["sales@ventilengineering.com"])
