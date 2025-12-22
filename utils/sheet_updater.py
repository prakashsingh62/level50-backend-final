# utils/sheet_updater.py
import json
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


# --------------------------------------------------
# Google Sheets client (ENV JSON)
# --------------------------------------------------
def _get_service():
    info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=creds)


# --------------------------------------------------
# AUDIT ROW WRITER (THIS WAS MISSING)
# --------------------------------------------------
def write_audit_row(
    spreadsheet_id: str,
    tab_name: str,
    audit_row: list
):
    service = _get_service()

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [audit_row]}
    ).execute()
