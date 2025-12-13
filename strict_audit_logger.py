# =========================================
# strict_audit_logger.py
# Level-80 Audit → Google Sheet (FINAL / STABLE)
# =========================================

import os
import json
import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------
# ENV CONFIG
# -------------------------------------------------
SHEET_ID = os.getenv("PROD_SHEET_ID")
TAB_NAME = os.getenv("PROD_TAB")
CLIENT_SECRET_JSON = os.getenv("CLIENT_SECRET_JSON")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


# -------------------------------------------------
# TIME (IST)
# -------------------------------------------------
def _now_ist():
    return (
        datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=5, minutes=30)
    ).strftime("%d/%m/%Y %H:%M:%S IST")


# -------------------------------------------------
# GOOGLE AUTH
# -------------------------------------------------
def _load_credentials():
    if not CLIENT_SECRET_JSON:
        raise RuntimeError("CLIENT_SECRET_JSON missing")

    data = json.loads(CLIENT_SECRET_JSON)
    return Credentials.from_service_account_info(data, scopes=SCOPES)


# -------------------------------------------------
# APPEND ROW
# -------------------------------------------------
def _append_row(values: list):
    creds = _load_credentials()
    service = build("sheets", "v4", credentials=creds)

    body = {"values": [values]}

    service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=f"{TAB_NAME}!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()


# -------------------------------------------------
# CORE LOGGER
# -------------------------------------------------
def _log_post_update(rows_written, affected_rows, updater, event_type="POST_UPDATE"):
    _append_row([
        _now_ist(),
        "",                     # RFQ NO (future use)
        "",                     # UID (future use)
        event_type,
        "SUCCESS",
        rows_written,
        updater,
        f"Rows updated: {affected_rows}",
    ])


# -------------------------------------------------
# STRICT MODE ENTRY POINT (DO NOT CHANGE NAME)
# -------------------------------------------------
def write_audit(**payload):
    """
    SAFE ENTRY POINT
    Accepts ANY future keys without crashing.

    Known keys:
    - rows_written
    - affected_rows
    - updater
    - event_type
    """

    rows_written = payload.get("rows_written", 0)
    affected_rows = payload.get("affected_rows", [])
    updater = payload.get("updater", "SYSTEM")
    event_type = payload.get("event_type", "POST_UPDATE")

    _log_post_update(
        rows_written=rows_written,
        affected_rows=affected_rows,
        updater=updater,
        event_type=event_type,
    )
