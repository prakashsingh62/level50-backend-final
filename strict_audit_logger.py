import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from utils.time_ist import ist_date, ist_time, ist_now

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

AUDIT_SHEET_ID = os.environ.get("AUDIT_SHEET_ID")
AUDIT_TAB = os.environ.get("AUDIT_TAB", "audit_log")
SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")

if not AUDIT_SHEET_ID:
    raise RuntimeError("Missing AUDIT_SHEET_ID")

if not SERVICE_ACCOUNT_JSON:
    raise RuntimeError("Missing GOOGLE_SERVICE_ACCOUNT_JSON")


def _get_service():
    try:
        info = json.loads(SERVICE_ACCOUNT_JSON)
    except Exception as e:
        raise RuntimeError("Invalid GOOGLE_SERVICE_ACCOUNT_JSON") from e

    creds = Credentials.from_service_account_info(
        info,
        scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def log_audit_event(run_id, stage, status, payload=None):
    service = _get_service()

    row = [
        ist_date(),
        ist_time(),
        ist_now(),
        run_id,
        stage,
        status,
        json.dumps(payload or {}, ensure_ascii=False),
    ]

    service.spreadsheets().values().append(
        spreadsheetId=AUDIT_SHEET_ID,
        range=f"{AUDIT_TAB}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]}
    ).execute()
