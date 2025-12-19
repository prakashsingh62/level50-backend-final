"""
sheet_reader.py
Level-80 RFQ Reader
Single source of truth for RFQ data
FINAL SAFE VERSION (range parsing fixed)
"""

import os
import json
from typing import List, Dict

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Google Sheets scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_service():
    service_json = os.getenv("CLIENT_SECRET_JSON")
    if not service_json:
        raise RuntimeError("CLIENT_SECRET_JSON missing")

    try:
        service_info = json.loads(service_json)
    except Exception as e:
        raise RuntimeError(f"Invalid CLIENT_SECRET_JSON: {e}")

    creds = Credentials.from_service_account_info(
        service_info,
        scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def read_rfqs() -> List[Dict]:
    """
    Read FULL RFQ rows from Google Sheet.
    - Uses exact headers from sheet
    - No trimming / renaming
    - Safe range handling (NO manual quotes)
    """

    sheet_id = os.getenv("PROD_SHEET_ID")
    rfq_tab = os.getenv("PROD_RFQ_TAB")

    if not sheet_id:
        raise RuntimeError("PROD_SHEET_ID missing")

    if not rfq_tab:
        raise RuntimeError("PROD_RFQ_TAB missing")

    service = _get_service()

    # IMPORTANT: do NOT wrap sheet name in quotes
    range_name = f"{rfq_tab}!A1:AT"

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
    except Exception as e:
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
