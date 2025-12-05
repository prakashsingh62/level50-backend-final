# daily_sender.py
# FINAL DAILY REMINDER SENDER — HTML IDENTICAL TO MANUAL REMINDER

from sheet_reader import read_rows
from logic_engine import process_sheet
from router_email import build_email_html_from_engine_result
from email_sender import send_email
import traceback


def send_daily_reminder():
    """
    Runs every morning at 8 AM (Railway cron or external scheduler).
    Generates DAILY RFQ REMINDER in FULL HTML format,
    identical to the manual reminder email template.
    """
    try:
        # 1) Read sheet
        rows = read_rows()

        # 2) Run logic engine
        result = process_sheet(rows)

        # 3) Build HTML email (SAME function used by manual reminder)
        html_body = build_email_html_from_engine_result(result)

        # 4) Send email
        send_result = send_email(
            to="sales@ventilengineering.com",
            subject="Daily RFQ Reminder — Level 50",
            body=html_body,
            is_html=True
        )

        return {
            "status": "success",
            "email_status": send_result,
            "summary": result.get("summary", {})
        }

    except Exception as e:
        return {
            "status": "error",
            "exception": str(e),
            "trace": traceback.format_exc()
        }
