"""
sheet_reader.py
Level-80 RFQ Reader (METADATA RESOLVED — BULLETPROOF)
"""

import os
import json
from typing import List, Dict
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _get_service():
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not raw:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON missing")

    creds = Credentials.from_service_account_info(
        json.loads(raw),
        scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def _resolve_tab_title(service, spreadsheet_id: str, expected: str) -> str:
    """
    Resolve ACTUAL sheet title from metadata.
    Handles hidden spaces, unicode, rename issues.
    """
    expected_clean = expected.strip().lower()

    meta = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id
    ).execute()

    for sheet in meta.get("sheets", []):
        title = sheet["properties"]["title"]
        if title.strip().lower() == expected_clean:
            return title

    raise RuntimeError(
        f"Sheet tab '{expected}' not found. "
        f"Available tabs: {[s['properties']['title'] for s in meta.get('sheets', [])]}"
    )


# payload accepted for pipeline compatibility
def read_rfqs(payload=None) -> List[Dict]:
    sheet_id = os.getenv("PROD_SHEET_ID")
    tab_env = os.getenv("PROD_RFQ_TAB")

    if not sheet_id or not tab_env:
        return []

    service = _get_service()

    real_tab = _resolve_tab_title(service, sheet_id, tab_env)

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{real_tab}'!A1:AT"
        ).execute()
    except HttpError as e:
        raise RuntimeError(f"Google Sheets read failed: {e}")

    rows = result.get("values", [])
    if len(rows) < 2:
        return []

    headers = rows[0]
    data_rows = rows[1:]

    # ✅ ONLY list[dict] returned
    return [dict(zip(headers, row)) for row in data_rows]
