import os
import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

from utils.audit_logger import append_audit_with_alert
from utils.time_ist import ist_date, ist_time

# ============================================================
# ENV
# ============================================================
SHEET_ID = os.environ["SHEET_ID"]
TAB_NAME = os.environ.get("TAB_NAME", "RFQ TEST SHEET")

AUDIT_SHEET_ID = os.environ["AUDIT_SHEET_ID"]
AUDIT_TAB = os.environ.get("AUDIT_TAB", "audit_log")

# ============================================================
# GOOGLE CREDS
# ============================================================
creds = Credentials.from_service_account_info(
    json.loads(os.environ["CLIENT_SECRET_JSON"]),
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

service = build("sheets", "v4", credentials=creds)

# ============================================================
# MAIN ENTRY — PIPELINE COMPATIBLE
# ============================================================
def write_sheet(rfq: dict):
    """
    Called directly from pipeline_engine.py
    """

    row_number = rfq["row_number"]      # MUST exist
    rfq_no = rfq.get("rfq_no", "")
    uid_no = rfq.get("uid", "")

    updates = rfq.get("sheet_updates", [])
    if not updates:
        return 0

    row_index = row_number - 1
    requests = []

    for u in updates:
        requests.append({
            "updateCells": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": row_index,
                    "endRowIndex": row_index + 1,
                    "startColumnIndex": u["col"],
                    "endColumnIndex": u["col"] + 1,
                },
                "rows": [{
                    "values": [{
                        "userEnteredValue": {
                            "stringValue": str(u["value"])
                        }
                    }]
                }],
                "fields": "userEnteredValue"
            }
        })

    # ---------------- SHEET UPDATE ----------------
    service.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"requests": requests}
    ).execute()

    # ---------------- AUDIT PER COLUMN ----------------
    for u in updates:
        audit_row = [
            f"{ist_date()} {ist_time()}",
            ist_date(),
            ist_time(),
            rfq_no,
            uid_no,
            "RFQ TEST SHEET",
            TAB_NAME,
            row_number,
            u["name"],
            "",
            u["value"],
            "UPDATE",
            "PIPELINE",
            "LEVEL_80_ENGINE",
            "SUCCESS",
            "AUTO",
            "RUN",
            "RUN"
        ]

        append_audit_with_alert(
            creds=creds,
            sheets_service=service,
            spreadsheet_id=AUDIT_SHEET_ID,
            tab_name=AUDIT_TAB,
            audit_row=audit_row,
            run_id="RUN",
            request_id="AUTO"
        )

    return len(updates)
