from fastapi import FastAPI
from pydantic import BaseModel
from logic_engine import classify_rows
from email_builder import build_email_html
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import sendgrid
from sendgrid.helpers.mail import Mail

app = FastAPI()

SHEET_ID = "1x60zesQY67FViw4F-SzrWnbU00kJq5QdBrcoRrmmTVw"
SERVICE_ACCOUNT_FILE = "service_account.json"

scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)

def read_sheet():
    service = build("sheets", "v4", credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range="DOMESTIC REGISTER 2025-26!A1:AO5000"
    ).execute()
    rows = result.get("values", [])
    headers = rows[0]
    data = []
    for r in rows[1:]:
        d = {}
        for i, h in enumerate(headers):
            d[h] = r[i] if i < len(r) else ""
        data.append(d)
    return data

def send_mail(html):
    sg = sendgrid.SendGridAPIClient(api_key="YOUR_SENDGRID_KEY")
    msg = Mail(
        from_email="sales@ventilengineering.com",
        to_emails=["sales@ventilengineering.com"],
        subject=f"Daily RFQ Reminder — DOMESTIC REGISTER 2025-2026 — {__import__('datetime').date.today():%d-%b-%Y}",
        html_content=html
    )
    sg.send(msg)

@app.post("/run")
def run(debug: bool = False):
    rows = read_sheet()
    summary, sections = classify_rows(rows)
    html = build_email_html(summary, sections)

    if debug:
        return {"status": "debug_ok", "email_preview": html}

    send_mail(html)
    return {"status": "email_sent"}
