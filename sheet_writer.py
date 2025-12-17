"""
sheet_writer.py
Level-80 Sheet Writer
Single-source adapter for pipeline_engine
"""

import os
import json
from typing import Dict
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


# =====================================================
# ✅ THIS IS WHAT pipeline_engine IMPORTS
# =====================================================
def write_sheet(rfq: Dict) -> int:
    """
    Adapter expected by pipeline_engine
    MUST return number of rows written
    MUST NOT crash pipeline
    """

    if not isinstance(rfq, dict):
        return 0

    sheet_id = os.getenv("PROD_SHEET_ID")
    tab_name = os.getenv("PROD_AUDIT_TAB")

    if not sheet_id or not tab_name:
        # Hard safety — no env, no write
        return 0

    service = _get_service()

    values = [[
        rfq.get("rfq_no"),
        rfq.get("uid"),
        rfq.get("customer"),
        rfq.get("vendor"),
        rfq.get("status", "OK"),
    ]]

    body = {"values": values}

    result = service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=f"{tab_name}!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

    return result.get("updates", {}).get("updatedRows", 0)
