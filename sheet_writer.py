import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from utils.time_ist import ist_now

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
PROD_SHEET_ID = os.environ.get("PROD_SHEET_ID")
PROD_RFO_TAB = os.environ.get("PROD_RFO_TAB")

if not SERVICE_ACCOUNT_JSON:
    raise RuntimeError("Missing GOOGLE_SERVICE_ACCOUNT_JSON")

if not PROD_SHEET_ID:
    raise RuntimeError("Missing PROD_SHEET_ID")

if not PROD_RFO_TAB:
    raise RuntimeError("Missing PROD_RFO_TAB")


def _get_service():
    info = json.loads(SERVICE_ACCOUNT_JSON)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def write_sheet_row(values: list):
    service = _get_service()
    service.spreadsheets().values().append(
        spreadsheetId=PROD_SHEET_ID,
        range=f"{PROD_RFO_TAB}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [values]}
    ).execute()
