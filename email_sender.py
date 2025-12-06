import os
from sheet_reader import read_rows
from logic_engine import run_level50
from email_builder import build_email_content
from email_sender import send_email

# Env var for normal daily recipients
DAILY_RECIPIENTS_ENV = "EMAIL_RECIPIENTS"

# Single manual-recipient email
SALES_ONLY_EMAIL = "sales@ventilengineering.com"


def _build_html_from_sheet():
    """
    Shared helper:
    - reads rows from sheet
    - runs Level-51 logic_engine
    - builds final HTML for email
    """
    rows = read_rows()
    result = run_level50(rows)

    sections = result.get("sections", {})
    autofix = result.get("autofix", [])
    alerts = result.get("alerts", [])

    return build_email_content(sections, autofix, alerts)


def send_daily_email():
    """
    Normal daily reminder:
    - uses EMAIL_RECIPIENTS env list
    - this is what your scheduled cron should call
    """
    html = _build_html_from_sheet()

    recipients_env = os.environ.get(DAILY_RECIPIENTS_ENV, SALES_ONLY_EMAIL)
    recipients = [r.strip() for r in recipients_env.split(",") if r.strip()]

    return send_email(html, recipients)


def send_sales_only_email():
    """
    Manual reminder:
    - sends the same HTML
    - BUT only to sales@ventilengineering.com
    """
    html = _build_html_from_sheet()
    recipients = [SALES_ONLY_EMAIL]
    return send_email(html, recipients)


def send_manual_reminder():
    """
    Backward-compatible name.
    When anything calls send_manual_reminder(),
    it will now send ONLY to sales@ventilengineering.com.
    """
    return send_sales_only_email()


if __name__ == "__main__":
    """
    Allow running from Railway cron with different modes:

    - default (no LEVEL51_SEND_MODE)  -> daily mail to EMAIL_RECIPIENTS
    - LEVEL51_SEND_MODE=sales_only    -> manual mail only to sales@
    """
    mode = os.environ.get("LEVEL51_SEND_MODE", "daily").lower().strip()

    if mode == "sales_only":
        send_sales_only_email()
    else:
        # default behaviour: daily to full list
        send_daily_email()
