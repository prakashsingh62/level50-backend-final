# =========================================
# audit_report_api.py
# Level-80 Audit Report API (READ ONLY)
# =========================================

import os
import json
from fastapi import APIRouter
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/api/audit",
    tags=["Audit Report"]
)

# -------------------------------------------------
# ENV
# -------------------------------------------------
SHEET_ID = os.getenv("PROD_SHEET_ID")
TAB_NAME = os.getenv("PROD_TAB")
CLIENT_SECRET_JSON = os.getenv("CLIENT_SECRET_JSON")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _get_service():
    data = json.loads(CLIENT_SECRET_JSON)
    creds = Credentials.from_service_account_info(data, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


@router.get("/report")
def get_audit_report(limit: int = 100):
    """
    Returns last N audit rows (latest first)
    """
    service = _get_service()

    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"{TAB_NAME}!A1:Z"
    ).execute()

    rows = result.get("values", [])

    if not rows:
        return {"rows": []}

    header = rows[0]
    data = rows[1:]

    data.reverse()
    data = data[:limit]

    output = []
    for r in data:
        row = {}
        for i, col in enumerate(header):
            row[col] = r[i] if i < len(r) else ""
        output.append(row)

    return {
        "count": len(output),
        "rows": output
    }
