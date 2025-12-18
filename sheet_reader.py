"""
sheet_reader.py
Level-80 RFQ Reader
Single-source reader for pipeline_engine & RFQ filtering
FULL ROW MODE (Step-1.5)
"""

import os
import json
from typing import List, Dict
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Scope: read/write allowed (existing setup preserved)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_service():
    service_json = os.getenv("CLIENT_SECRET_JSON")
    if not service_json:
        raise RuntimeError("CLIENT_SECRET_JSON missing")

    creds = Credentials.from_service_account_info(
        json.loads(service_json),
        scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def read_rfqs() -> List[Dict]:
    """
    REAL RFQ reader (FULL ROW MODE)

    Returns:
    - Each RFQ as a dict
    - Keys EXACTLY same as Google Sheet headers
    - No trimming, no renaming, no filtering
    """

    sheet_id = os.getenv("PROD_SHEET_ID")
    rfq_tab = os.getenv("PROD_RFQ_TAB")

    if not sheet_id or not rfq_tab:
        return []

    service = _get_service()

    # IMPORTANT: AT range is required for your sheet
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"'{rfq_tab}'!A1:AT"
    ).execute()

    rows = result.get("values", [])
    if len(rows) < 2:
        return []

    headers = rows[0]
    data_rows = rows[1:]

    rfqs: List[Dict] = []

    for row in data_rows:
        # zip auto-handles short rows
        record = dict(zip(headers, row))
        rfqs.append(record)

    return rfqs
