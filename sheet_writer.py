import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SHEET_ID = os.getenv("PROD_SHEET_ID")
TAB_NAME = os.getenv("PROD_AUDIT_TAB")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_service():
    service_json = os.getenv("CLIENT_SECRET_JSON")
    if not service_json:
        raise RuntimeError("CLIENT_SECRET_JSON missing in env")

    creds = Credentials.from_service_account_info(
        json.loads(service_json),
        scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


# =====================================================
# ✅ THIS IS WHAT PIPELINE EXPECTS
# =====================================================
def write_sheet(rfq: dict):
    service = _get_service()

    values = [[
        rfq.get("rfq_no"),
        rfq.get("uid"),
        rfq.get("customer"),
        rfq.get("vendor"),
        rfq.get("status", "OK")
    ]]

    body = {"values": values}

    result = service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=f"{TAB_NAME}!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

    return result.get("updates", {}).get("updatedRows", 0)


# =====================================================
# OPTIONAL TEST (keep)
# =====================================================
def write_test_row():
    return write_sheet({
        "rfq_no": "TEST",
        "uid": "TEST",
        "customer": "TEST",
        "vendor": "TEST",
        "status": "SUCCESS"
    })
