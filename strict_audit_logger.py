import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from utils.time_ist import ist_date, ist_time, ist_now

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

AUDIT_SHEET_ID = os.environ["AUDIT_SHEET_ID"]
AUDIT_TAB = os.environ.get("AUDIT_TAB", "audit_log")
CLIENT_SECRET_JSON = (
    os.environ.get("CLIENT_SECRET_JSON")
    or os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
)

def _service():
    creds = Credentials.from_service_account_info(
        eval(CLIENT_SECRET_JSON),
        scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)

def log_audit_event(
    timestamp,
    run_id,
    status,
    rfq_no=None,
    uid_no=None,
    customer=None,
    vendor=None,
    step=None,
    remarks=None,
    error_type=None,
    error_message=None,
    rows_written=None
):
    service = _service()
    sheet = service.spreadsheets()

    values = [[
        timestamp.isoformat(),
        ist_date(),
        ist_time(),
        rfq_no,
        uid_no,
        "MAIN_SHEET",
        os.environ.get("PROD_RFQ_TAB"),
        None,
        None,
        None,
        None,
        status
    ]]

    sheet.values().append(
        spreadsheetId=AUDIT_SHEET_ID,
        range=f"{AUDIT_TAB}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": values}
    ).execute()
