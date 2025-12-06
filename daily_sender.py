import os
from sheet_reader import read_rows
from logic_engine import run_level50
from email_builder import build_email
from email_sender import send_email


def send_daily_email():
    """
    Level-51 Daily Report Mail:
    - Summary
    - Autofix actions (Level-51)
    - Alerts
    """

    # Step 1: Read sheet
    rows = read_rows()

    # Step 2: Process logic engine
    result = run_level50(rows)

    summary = result.get("summary", {})
    sections = result.get("sections", {})
    autofix = result.get("autofix", [])
    alerts = result.get("alerts", [])

    # Step 3: Build HTML
    html = build_email(summary, sections, autofix, alerts)

    # Step 4: Send mail
    recipients = os.environ["EMAIL_RECIPIENTS"].split(",")
    return send_email(html, recipients)


def send_manual_reminder():
    """
    Manual trigger → same report as daily mail.
    """
    return send_daily_email()
