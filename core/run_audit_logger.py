# core/run_audit_logger.py

import json
from datetime import datetime, timezone, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

from config import AUDIT_SHEET_ID, CLIENT_SECRET_JSON

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
IST = timezone(timedelta(hours=5, minutes=30))


def _now_ist():
    return datetime.now(IST).isoformat()


def _append_row(sheet_id: str, tab: str, row: list):
    creds = service_account.Credentials.from_service_account_info(
        CLIENT_SECRET_JSON, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=creds)

    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=f"{tab}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()


def log_run_start(trace_id: str, phase: str, mode: str):
    _append_row(
        AUDIT_SHEET_ID,
        "audit_log",
        [
            _now_ist(),
            trace_id,
            phase,
            mode,
            "RUNNING",
            "",
            "",
            "",
            json.dumps({"event": "START"}),
        ],
    )


def log_run_success(trace_id: str, phase: str, mode: str, total: int, processed: int):
    _append_row(
        AUDIT_SHEET_ID,
        "audit_log",
        [
            _now_ist(),
            trace_id,
            phase,
            mode,
            "SUCCESS",
            total,
            processed,
            "",
            json.dumps({"status": "OK", "processed": processed}),
        ],
    )


def log_run_failure(trace_id: str, phase: str, mode: str, error: Exception):
    _append_row(
        AUDIT_SHEET_ID,
        "audit_log",
        [
            _now_ist(),
            trace_id,
            phase,
            mode,
            "FAILED",
            "",
            "",
            str(error),
            json.dumps({"error": str(error)}),
        ],
    )
