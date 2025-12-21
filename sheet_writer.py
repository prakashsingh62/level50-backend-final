import os
import json
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

from utils.time_ist import ist_date, ist_time
from utils.turbo_engine import turbo_log
from utils.audit_logger import append_audit_with_alert

# ============================================================
# ENV CONFIG
# ============================================================
SHEET_ID = os.environ["SHEET_ID"]
TAB_NAME = os.environ.get("TAB_NAME", "RFQ TEST SHEET")

AUDIT_SHEET_ID = os.environ["AUDIT_SHEET_ID"]
AUDIT_TAB = os.environ.get("AUDIT_TAB", "audit_log")

# ============================================================
# GOOGLE CREDS (RAILWAY SAFE)
# ============================================================
service_account_info = json.loads(os.environ["CLIENT_SECRET_JSON"])

creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

service = build("sheets", "v4", credentials=creds)

# ============================================================
# WRITE + AUDIT (REAL EXECUTED FUNCTION)
# ============================================================
def write_sheet(row_number, updates, rfq_no="", uid_no=""):
    """
    row_number : sheet row (1-based)
    updates    : list of dicts
                 [{ "col": 33, "value": "OFFER RECEIVED", "name": "Vendor Status" }]
    """

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
                        "userEnteredValue": {"stringValue": str(u["value"])}
                    }]
                }],
                "fields": "userEnteredValue"
            }
        })

    # ---------------- MAIN SHEET UPDATE ----------------
    service.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"requests": requests}
    ).execute()

    # ---------------- AUDIT (PER COLUMN) ----------------
    for u in updates:
        audit_row = [
            f"{ist_date()} {ist_time()}",  # TIMESTAMP_IST
            ist_date(),                    # DATE
            ist_time(),                    # TIME
            rfq_no,                        # RFQ_NO
            uid_no,                        # UID_NO
            "RFQ TEST SHEET",              # SHEET_NAME
            TAB_NAME,                      # TAB_NAME
            row_number,                    # ROW_NUMBER
            u["name"],                     # COLUMN_NAME
            "",                            # OLD_VALUE (turbo mode)
            u["value"],                    # NEW_VALUE
            "UPDATE",                      # ACTION_TYPE
            "AI",                          # TRIGGER_SOURCE
            "LEVEL_80_ENGINE",             # ACTOR
            "SUCCESS",                     # STATUS
            "AUTO UPDATE",                 # REASON
            "AUTO",                        # REQUEST_ID
            "RUN_AUTO"                     # RUN_ID
        ]

        append_audit_with_alert(
            creds=creds,
            sheets_service=service,
            spreadsheet_id=AUDIT_SHEET_ID,
            tab_name=AUDIT_TAB,
            audit_row=audit_row,
            run_id="RUN_AUTO",
            request_id="AUTO"
        )

    turbo_log("SHEET + AUDIT WRITE DONE")
