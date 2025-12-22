# utils/sheet_updater.py
import json
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


# --------------------------------------------------
# Google Sheets client (ENV JSON)
# --------------------------------------------------
def _get_service():
    info = json.loads(os.environ["CLIENT_SECRET_JSON"])
    creds = Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=creds)


# --------------------------------------------------
# AUDIT ROW WRITER (FIXED)
# --------------------------------------------------
def write_audit_row(
    tab_name: str,
    audit_row: dict
):
    service = _get_service()

    spreadsheet_id = os.environ.get("AUDIT_SHEET_ID")
    if not spreadsheet_id:
        raise RuntimeError("AUDIT_SHEET_ID env missing")

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [list(audit_row.values())]}
    ).execute()
