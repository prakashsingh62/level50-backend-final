from fastapi import FastAPI
from logic_engine import classify_rows
from email_builder import build_email_html
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import date
import sendgrid
from sendgrid.helpers.mail import Mail
import json
from config import CLIENT_SECRET_JSON, PROD_SHEET_ID, PROD_TAB

app = FastAPI()

# Convert JSON string → Python dict
if isinstance(CLIENT_SECRET_JSON, str):
    SERVICE_INFO = json.loads(CLIENT_SECRET_JSON)
else:
    SERVICE_INFO = CLIENT_SECRET_JSON

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# Create credentials directly from Railway variable
creds = Credentials.from_service_account_info(SERVICE_INFO, scopes=SCOPES)


def read_sheet():
    service = build("sheets", "v4", credentials=creds)

    tab_range = f"{PROD_TAB}!A1:AO5000"

    result = service.spreadsheets().values().get(
        spreadsheetId=PROD_SHEET_ID,
        range=tab_range
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
        subject=f"Daily RFQ Reminder — {PROD_TAB} — {date.today():%d-%b-%Y}",
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
