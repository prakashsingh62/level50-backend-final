from fastapi import APIRouter
from sheet_reader import read_rows
from logic_engine import process_sheet
from email_builder import build_email_html
from email_sender import send_email

router = APIRouter()

# -----------------------------
# Manual Reminder Trigger
# -----------------------------
@router.post("/manual-reminder")
def manual_reminder():
    # 1) Read sheet
    rows = read_rows()

    # 2) Classify + prepare sections
    result = process_sheet(rows)
    summary = result["summary"]
    sections = result["sections"]

    # 3) Build HTML body
    html_body = build_email_html(summary, sections)

    # 4) Send mail
    send_result = send_email(
        to="sales@ventilengineering.com",
        subject="Manual RFQ Reminder (Triggered Manually)",
        body=html_body,
        is_html=True
    )

    return {
        "status": "manual reminder sent",
        "send_result": send_result
    }


# -----------------------------
# Daily Reminder Trigger
# -----------------------------
@router.post("/daily-reminder")
def daily_reminder():
    # 1) Read sheet
    rows = read_rows()

    # 2) Classify + prepare sections
    result = process_sheet(rows)
    summary = result["summary"]
    sections = result["sections"]

    # 3) Build HTML body
    html_body = build_email_html(summary, sections)

    # 4) Send mail
    send_result = send_email(
        to="sales@ventilengineering.com",
        subject="Daily RFQ Reminder (Automated 8AM)",
        body=html_body,
        is_html=True
    )

    return {
        "status": "daily reminder sent",
        "send_result": send_result
    }
