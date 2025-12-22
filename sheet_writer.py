import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from utils.time_ist import ist_now

# =========================================================
# CONFIG
# =========================================================

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
PROD_SHEET_ID = os.environ.get("PROD_SHEET_ID")
PROD_RFQ_TAB = os.environ.get("PROD_RFQ_TAB")


# =========================================================
# INTERNAL HELPERS
# =========================================================

def _error(msg: str):
    return {
        "status": "ERROR",
        "message": msg,
        "time": ist_now()
    }


def _get_service():
    try:
        info = json.loads(SERVICE_ACCOUNT_JSON)
        creds = Credentials.from_service_account_info(
            info,
            scopes=SCOPES
        )
        return build("sheets", "v4", credentials=creds)
    except Exception as e:
        return None, str(e)


# =========================================================
# PUBLIC FUNCTION
# =========================================================

def write_sheet(payload: dict):
    """
    Safe writer:
    - NEVER crashes FastAPI
    - Always returns JSON
    """

    # ---------- ENV VALIDATION ----------
    if not SERVICE_ACCOUNT_JSON:
        return _error("Missing GOOGLE_SERVICE_ACCOUNT_JSON")

    if not PROD_SHEET_ID:
        return _error("Missing PROD_SHEET_ID")

    if not PROD_RFQ_TAB:
        return _error("Missing PROD_RFQ_TAB")

    # ---------- SERVICE ----------
    try:
        service = build(
            "sheets",
            "v4",
            credentials=Credentials.from_service_account_info(
                json.loads(SERVICE_ACCOUNT_JSON),
                scopes=SCOPES
            )
        )
    except Exception as e:
        return _error(f"Google auth failed: {str(e)}")

    # ---------- DATA ----------
    row = [
        ist_now(),
        payload.get("source", "unknown"),
        payload.get("note", ""),
        json.dumps(payload)
    ]

    body = {
        "values": [row]
    }

    range_name = f"{PROD_RFQ_TAB}!A1"

    # ---------- WRITE ----------
    try:
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=PROD_SHEET_ID,
                range=range_name,
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body=body
            )
            .execute()
        )

        return {
            "status": "OK",
            "updatedRange": result.get("updates", {}).get("updatedRange"),
            "time": ist_now()
        }

    except Exception as e:
        return _error(f"Sheet write failed: {str(e)}")
