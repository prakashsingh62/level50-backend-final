import os
from sheet_reader import read_rows
from logic_engine import run_level50
from email_builder import build_email
from email_sender import send_email


def send_daily_email():
    """
    Sends FULL Level-51 Daily Report:
    - Summary (High, Medium, Low etc.)
    - Autofix actions
    - Alerts
    """

    # Read rows from Google Sheet
    rows = read_rows()

    # Run Level-51 logic pipeline
    result = run_level50(rows)

    summary = result.get("summary", {})
    sections = result.get("sections", {})
    autofix = result.get("autofix", [])
    alerts = result.get("alerts", [])

    # Build final HTML mail
    html = build_email(summary, sections, autofix, alerts)

    # Daily recipients from ENV
    recipients = os.environ["EMAIL_RECIPIENTS"].split(",")

    # Send mail using generic sender
    return send_email(html, recipients)


def send_manual_reminder():
    """
    Manual trigger API → same report, 
    goes only to sales@ventilengineering.com.
    """

    rows = read_rows()
    result = run_level50(rows)

    summary = result.get("summary", {})
    sections = result.get("sections", {})
    autofix = result.get("autofix", [])
    alerts = result.get("alerts", [])

    html = build_email(summary, sections, autofix, alerts)

    return send_email(html, ["sales@ventilengineering.com"])