# =========================================
# strict_audit_logger.py
# Level-80 Audit → Google Sheet (FINAL)
# =========================================

import os
import json
import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
load_dotenv()

# -------------------------------------------------
# ENV CONFIG (ALREADY USED BY PROJECT)
# -------------------------------------------------
SHEET_ID = os.getenv("PROD_SHEET_ID")
TAB_NAME = os.getenv("PROD_TAB")
CLIENT_SECRET_JSON = os.getenv("CLIENT_SECRET_JSON")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


import datetime

def _now_ist():
    return (
        datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=5, minutes=30)
    ).strftime("%d/%m/%Y %H:%M:%S IST")


def _load_credentials():
    data = json.loads(CLIENT_SECRET_JSON)
    return Credentials.from_service_account_info(data, scopes=SCOPES)


def _append_row(values: list):
    creds = _load_credentials()
    service = build("sheets", "v4", credentials=creds)

    body = {"values": [values]}

    service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=f"{TAB_NAME}!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()


# -------------------------------------------------
# LEVEL-80 POST UPDATE SNAPSHOT (CORE)
# -------------------------------------------------
def log_post_update_snapshot(rows_written: int, affected_rows: list, updater: str):
    _append_row([
        _now_ist(),
        "",                     # rfq_no
        "",                     # uid
        "POST_UPDATE",
        "SUCCESS",
        rows_written,
        updater,
        f"Rows updated: {affected_rows}",
    ])
