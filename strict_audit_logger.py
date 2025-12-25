import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import (
    CLIENT_SECRET_JSON,
    AUDIT_SHEET_ID,
    AUDIT_TAB
)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _load_service_account():
    if isinstance(CLIENT_SECRET_JSON, dict):
        return CLIENT_SECRET_JSON

    if isinstance(CLIENT_SECRET_JSON, str):
        import json
        try:
            return json.loads(CLIENT_SECRET_JSON)
        except Exception:
            cleaned = CLIENT_SECRET_JSON.replace('\\"', '"')
            return json.loads(cleaned)

    raise ValueError("Invalid CLIENT_SECRET_JSON")


def _sanitize(value):
    """
    Google Sheets rejects NULL_VALUE.
    Convert None → empty string.
    """
    if value is None:
        return ""
    return value


def log_audit_event(
    *,
    mode: str,
    run_id: str,
    status: str,
    rfq_no: str = None,
    uid_no: str = None,
    customer: str = None,
    message: str = None
):
    """
    STRICT RULES (LOCKED):
    1) mode == 'ping' MUST NEVER touch Google Sheets
    2) All values sanitized before append
    """

    # RULE-1: Ping must never write audit
    if mode == "ping":
        return

    service_info = _load_service_account()

    credentials = service_account.Credentials.from_service_account_info(
        service_info,
        scopes=SCOPES
    )

    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    row = [
        _sanitize(timestamp),
        _sanitize(run_id),
        _sanitize(status),
        _sanitize(rfq_no),
        _sanitize(uid_no),
        _sanitize(customer),
        _sanitize(message),
    ]

    sheet.values().append(
        spreadsheetId=AUDIT_SHEET_ID,
        range=f"{AUDIT_TAB}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()
