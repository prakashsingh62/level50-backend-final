"""
sheet_reader.py
Level-80 RFQ Reader
Single-source reader for pipeline_engine
"""

import os
import json
from typing import List, Dict
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

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


def _build_range(tab_name: str) -> str:
    """
    Google Sheets range builder
    Quotes ONLY if space exists
    """
    if " " in tab_name:
        return f"'{tab_name}'!A1:Z"
    return f"{tab_name}!A1:Z"


def read_rfqs() -> List[Dict]:
    """
    REAL RFQ reader used by pipeline_engine
    """

    sheet_id = os.getenv("PROD_SHEET_ID")
    rfq_tab = os.getenv("PROD_RFQ_TAB")

    if not sheet_id or not rfq_tab:
        return []

    service = _get_service()

    range_name = _build_range(rfq_tab)

    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=range_name
    ).execute()

    rows = result.get("values", [])
    if len(rows) < 2:
        return []

    headers = rows[0]
    data_rows = rows[1:]

    rfqs: List[Dict] = []

    for row in data_rows:
        record = dict(zip(headers, row))

        rfqs.append({
            "rfq_no": record.get("RFQ NO"),
            "uid": record.get("UID NO"),
            "customer": record.get("CUSTOMER"),
            "vendor": record.get("VENDOR"),
            "vendor_email": record.get("VENDOR EMAIL"),
            "send_mail": str(record.get("SEND MAIL", "")).strip().upper() == "YES",
        })

    return rfqs
