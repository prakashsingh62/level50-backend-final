"""
sheet_reader.py
Level-80 RFQ Reader (SAFE + FUTURE PROOF)
"""

import os
import json
from typing import List, Dict
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _clean_tab_name(name: str) -> str:
    """
    Removes accidental quotes and trims spaces.
    Handles:
    RFQ TEST SHEET
    'RFQ TEST SHEET'
    "RFQ TEST SHEET"
    """
    if not name:
        return ""
    return name.strip().strip("'").strip('"')


def _get_service():
    raw = os.getenv("CLIENT_SECRET_JSON")
    if not raw:
        raise RuntimeError("CLIENT_SECRET_JSON missing")

    creds = Credentials.from_service_account_info(
        json.loads(raw),
        scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def read_rfqs() -> List[Dict]:
    sheet_id = os.getenv("PROD_SHEET_ID")
    raw_tab = os.getenv("PROD_RFQ_TAB")

    if not sheet_id or not raw_tab:
        return []

    tab = _clean_tab_name(raw_tab)

    service = _get_service()

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"{tab}!A1:AT"   # ✅ NO quotes here
        ).execute()
    except HttpError as e:
        raise RuntimeError(f"Google Sheets read failed: {e}")

    rows = result.get("values", [])
    if len(rows) < 2:
        return []

    headers = rows[0]
    data_rows = rows[1:]

    rfqs: List[Dict] = []

    for row in data_rows:
        record = dict(zip(headers, row))
        rfqs.append(record)

    return rfqs
