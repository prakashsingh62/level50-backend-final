# =========================================
# strict_audit_logger.py
# Level-80 Audit → Google Sheet (FINAL FIXED)
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
# GOOGLE CREDS
# -------------------------------------------------
def _load_credentials():
    if not CLIENT_SECRET_JSON:
        raise RuntimeError("CLIENT_SECRET_JSON missing in env")

    data = json.loads(CLIENT_SECRET_JSON)
    return Credentials.from_service_account_info(
        data,
        scopes=SCOPES
    )


# -------------------------------------------------
# APPEND ROW TO AUDIT SHEET
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
        body=body
    ).execute()


# -------------------------------------------------
# CORE AUDIT LOGGER
# -------------------------------------------------
def log_post_update_snapshot(
    rows_written: int,
    affected_rows: list,
    updater: str
):
    _append_row([
        _now_ist(),                    # timestamp
        "POST_UPDATE",                 # status
        rows_written,                  # rows_written
        json.dumps(affected_rows),     # affected_rows
        updater,                       # updater
        "",                            # error_type
        "",                            # error_message
        0,                             # retry_count
        "OK"                           # remarks
    ])


# -------------------------------------------------
# STRICT MODE ENTRY POINT (IMPORTANT)
# -------------------------------------------------
def write_audit(
    *,
    event_type=None,
    rows_written=0,
    affected_rows=None,
    updater="SYSTEM",
    **kwargs
):
    """
    SAFE entry point.
    Accepts ANY keyword args from strict_mode_kernel.
    Never crashes on extra params.
    """

    if affected_rows is None:
        affected_rows = []

    log_post_update_snapshot(
        rows_written=rows_written,
        affected_rows=affected_rows,
        updater=updater
    )
