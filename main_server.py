from fastapi import FastAPI
from logic_engine import classify_rows
from email_builder import build_email_html
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import sendgrid
from sendgrid.helpers.mail import Mail
from datetime import date

app = FastAPI()

# UPDATED: New test sheet
SHEET_ID = "1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo"
TAB_RANGE = "RFQ TEST SHEET!A1:AO5000"

# PERMANENT FIX — file must exist in repo root
SERVICE_ACCOUNT_FILE = "service_account.json"

scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)

def read_sheet():
    service = build("sheets", "v4", credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=TAB_RANGE
    ).execute()

    rows = result.get("values", [])
    if not rows:
        return []

    headers = rows[0]
    data = []
    for r in rows[1:]:
        row_dict = {headers[i]: r[i] if i < len(r) else "" for i in range(len(headers))}
        data.append(row_dict)

    return data


def send_mail(html):
    sg = sendgrid.SendGridAPIClient(api_key="YOUR_SENDGRID_KEY")

    msg = Mail(
        from_email="sales@ventilengineering.com",
        to_emails="sales@ventilengineering.com",
        subject=f"Daily RFQ Reminder — RFQ TEST SHEET — {date.today():%d-%b-%Y}",
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
