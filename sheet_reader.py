"""
sheet_reader.py
Level-80 RFQ Reader (FINAL SAFE VERSION)
"""

import os
import json
from typing import List, Dict
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _normalize_tab(name: str) -> str:
    """
    Always returns a SAFE tab name wrapped in SINGLE QUOTES.
    Handles:
    RFQ TEST SHEET
    'RFQ TEST SHEET'
    "RFQ TEST SHEET"
    """
    if not name:
        return ""

    clean = name.strip().strip("'").strip('"')
    return f"'{clean}'"


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
    tab_raw = os.getenv("PROD_RFQ_TAB")

    if not sheet_id or not tab_raw:
        return []

    tab = _normalize_tab(tab_raw)

    service = _get_service()

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"{tab}!A1:AT"
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
        rfqs.append(dict(zip(headers, row)))

    return rfqs
