from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

from utils.time_ist import ist_date, ist_time
from utils.audit_logger import append_audit_with_alert

# =========================
# CONFIG
# =========================
MAIN_SHEET_ID = os.environ["MAIN_SHEET_ID"]
AUDIT_SHEET_ID = os.environ["AUDIT_SHEET_ID"]
AUDIT_TAB = os.environ.get("AUDIT_TAB", "audit_log")

creds = Credentials.from_service_account_info(
    eval(os.environ["CLIENT_SECRET_JSON"]),
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

service = build("sheets", "v4", credentials=creds)

# =========================
# REAL WRITE FUNCTION
# =========================
def write_sheet(rfq: dict):
    """
    REAL production writer
    + HARD audit (cannot be skipped)
    """

    row_number = rfq["row"]
    rfq_no = rfq.get("rfq_no", "")
    uid_no = rfq.get("uid", "")

    updates = rfq.get("updates", [])
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

    # -------- MAIN UPDATE --------
    service.spreadsheets().batchUpdate(
        spreadsheetId=MAIN_SHEET_ID,
        body={"requests": requests}
    ).execute()

    # -------- AUDIT (UNCONDITIONAL) --------
    for u in updates:
        audit_row = [
            f"{ist_date()} {ist_time()}",
            ist_date(),
            ist_time(),
            rfq_no,
            uid_no,
            "RFQ MAIN SHEET",
            "ACTIVE_TAB",
            row_number,
            u.get("name", ""),
            "",
            str(u["value"]),
            "UPDATE",
            "PIPELINE",
            "LEVEL_80_ENGINE",
            "SUCCESS",
            "WRITE_SHEET",
            "AUTO",
            "RUN_PHASE11"
        ]

        append_audit_with_alert(
            creds=creds,
            sheets_service=service,
            spreadsheet_id=AUDIT_SHEET_ID,
            tab_name=AUDIT_TAB,
            audit_row=audit_row,
            run_id="RUN_PHASE11",
            request_id="AUTO"
        )

    return len(updates)
