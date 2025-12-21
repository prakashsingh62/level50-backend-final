import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from strict_audit_logger import log_audit_event
from utils.time_ist import ist_now

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CLIENT_SECRET_JSON = os.environ["CLIENT_SECRET_JSON"]
MAIN_SHEET_ID = os.environ["PROD_SHEET_ID"]
MAIN_TAB = os.environ["PROD_RFQ_TAB"]

def _service():
    creds = Credentials.from_service_account_info(
        eval(CLIENT_SECRET_JSON),
        scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)

def write_sheet(rfq: dict):
    service = _service()
    sheet = service.spreadsheets()

    row = rfq["row_number"]
    col = rfq["target_col"]
    value = rfq["value"]

    sheet.values().update(
        spreadsheetId=MAIN_SHEET_ID,
        range=f"{MAIN_TAB}!{col}{row}",
        valueInputOption="RAW",
        body={"values": [[value]]}
    ).execute()

    return 1
