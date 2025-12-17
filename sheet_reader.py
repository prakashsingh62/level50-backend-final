"""
sheet_reader.py
Level-80 RFQ Reader
Safe adapter for pipeline_engine
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


def read_rfqs() -> List[Dict]:
    """
    Adapter expected by pipeline_engine
    MUST return list (empty allowed)
    MUST NOT crash pipeline
    """

    sheet_id = os.getenv("PROD_SHEET_ID")
    rfq_tab = os.getenv("PROD_RFQ_TAB")

    if not sheet_id or not rfq_tab:
        return []

    service = _get_service()

    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=rfq_tab
    ).execute()

    rows = result.get("values", [])
    if len(rows) < 2:
        return []

    headers = rows[0]
    data_rows = rows[1:]

    rfqs = []
    for row in data_rows:
        raw = dict(zip(headers, row))

        rfqs.append({
            "rfq_no": raw.get("RFQ NO"),
            "uid": raw.get("UID NO"),
            "customer": raw.get("CUSTOMER"),
            "vendor": raw.get("VENDOR"),
            "priority": raw.get("PRIORITY", "NORMAL"),
            "send_mail": raw.get("SEND MAIL") == "YES",
            "status": "OK",
        })

    return rfqs
