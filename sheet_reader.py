import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SHEET_ID = os.getenv("PROD_SHEET_ID")
RFQ_TAB = os.getenv("PROD_RFQ_TAB")  # RFQ data tab name

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
def read_rfqs():
    """
    Reads RFQs from Google Sheet and returns list of dicts
    """
    service = _get_service()

    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=RFQ_TAB
    ).execute()

    rows = result.get("values", [])
    if not rows or len(rows) < 2:
        return []

    headers = rows[0]
    data_rows = rows[1:]

    rfqs = []
    for row in data_rows:
        rfq = dict(zip(headers, row))
        rfqs.append({
            "rfq_no": rfq.get("RFQ NO"),
            "uid": rfq.get("UID NO"),
            "customer": rfq.get("CUSTOMER"),
            "vendor": rfq.get("VENDOR"),
            "send_mail": rfq.get("SEND MAIL") == "YES"
        })

    return rfqs
