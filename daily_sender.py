import os
from sheet_reader import read_rows
from logic_engine import run_level50
from email_builder import build_email_content
from email_sender import send_email

def send_daily_email():
    rows = read_rows()
    sections = process_rfq_rows(rows)
    html = build_email_content(sections)

    recipients = os.environ["EMAIL_RECIPIENTS"].split(",")
    return send_email(html, recipients)

def send_manual_reminder():
    return send_daily_email()
