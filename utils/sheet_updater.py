# ------------------------------------------------------------
# LEVEL 80 – TURBO + AUDIT (FINAL PRODUCTION SAFE VERSION)
# ------------------------------------------------------------
# GUARANTEES:
# - No local credential file dependency
# - Audit NEVER blocks main update
# - Correct sheetId resolution
# - Retry queue ONLY for main update
# - Railway / Cloud safe
# ------------------------------------------------------------

import os
import json
from datetime import datetime

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

from utils.turbo_engine import turbo_log
from utils.audit_logger import append_audit_with_alert
from utils.time_ist import ist_date, ist_time

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
SHEET_ID = "1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo"
TAB_NAME = "RFQ TEST SHEET"

AUDIT_SHEET_ID = "1g4BXp2wa6-vZPxSokAv3v8hwoFir39fb2bmVNi_y0Mc"
AUDIT_TAB = "audit_log"

COL_VENDOR_STATUS = 33
COL_QUOTATION_DATE = 19
COL_REMARKS = 34
COL_FOLLOWUP_DATE = 35

# ------------------------------------------------------------
# GOOGLE CREDS (RAILWAY SAFE)
# ------------------------------------------------------------
creds = Credentials.from_service_account_info(
    json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]),
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

service = build("sheets", "v4", credentials=creds)

# ------------------------------------------------------------
# RESOLVE SHEET ID (NO HARD-CODED 0)
# ------------------------------------------------------------
def get_sheet_id(spreadsheet_id: str, tab_name: str) -> int:
    meta = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id
    ).execute()

    for s in meta["sheets"]:
        if s["properties"]["title"] == tab_name:
            return s["properties"]["sheetId"]

    raise Exception(f"Sheet tab not found: {tab_name}")

RFQ_SHEET_ID = get_sheet_id(SHEET_ID, TAB_NAME)

# ------------------------------------------------------------
# DATE NORMALIZER
# ------------------------------------------------------------
def normalize_date(v: str) -> str:
    if not v:
        return ""
    v = v.replace("-", "/").strip()
    try:
        return datetime.strptime(v, "%d/%m/%Y").strftime("%d/%m/%Y")
    except Exception:
        return ""

# ------------------------------------------------------------
# TURBO CELL WRITER
# ------------------------------------------------------------
def write_cell(row: int, col: int, value: str) -> dict:
    return {
        "updateCells": {
            "range": {
                "sheetId": RFQ_SHEET_ID,
                "startRowIndex": row,
                "endRowIndex": row + 1,
                "startColumnIndex": col,
                "endColumnIndex": col + 1,
            },
            "rows": [
                {
                    "values": [
                        {"userEnteredValue": {"stringValue": value}}
                    ]
                }
            ],
            "fields": "userEnteredValue",
        }
    }

# ------------------------------------------------------------
# MAIN UPDATE + AUDIT (FINAL)
# ------------------------------------------------------------
def update_rfq_row(matched_row: int, ai_output: dict) -> dict:
    start = datetime.now()
    row_index = matched_row - 1

    rfq_no = ai_output.get("rfq_no", "").strip()
    uid_no = ai_output.get("uid_no", "").strip()

    vendor_status = ai_output.get("vendor_status", "").strip()
    quotation_date = normalize_date(ai_output.get("quotation_date", ""))
    remarks = ai_output.get("remarks", "").strip()
    followup_date = normalize_date(ai_output.get("followup_date", ""))

    updates = [
        ("Vendor Status", COL_VENDOR_STATUS, vendor_status),
        ("Quotation Date", COL_QUOTATION_DATE, quotation_date),
        ("Remarks", COL_REMARKS, remarks),
        ("Followup Date", COL_FOLLOWUP_DATE, followup_date),
    ]

    requests = []
    audit_payload = []

    for col_name, col_index, value in updates:
        if not value:
            continue
        requests.append(write_cell(row_index, col_index, value))
        audit_payload.append((col_name, value))

    if not requests:
        turbo_log("No fields to update")
        return {"status": "no_fields", "row": matched_row}

    # ---------------- MAIN SHEET UPDATE ----------------
    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={"requests": requests}
        ).execute()

    except Exception as e:
        from retry_queue.retry_queue_manager import queue_retry

        queue_retry({
            "type": "sheet_update",
            "row": matched_row,
            "payload": ai_output,
            "retry_count": 0,
        })

        turbo_log(f"MAIN UPDATE FAILED → RETRY QUEUED → {e}")
        raise

    # ---------------- AUDIT (NON-BLOCKING) ----------------
    for column_name, new_value in audit_payload:
        audit_row = [
            f"{ist_date()} {ist_time()}",
            ist_date(),
            ist_time(),
            rfq_no,
            uid_no,
            TAB_NAME,
            TAB_NAME,
            matched_row,
            column_name,
            "",
            new_value,
            "UPDATE",
            "AI",
            "LEVEL_80_ENGINE",
            "SUCCESS",
            "Turbo batch update",
            "AUTO",
            "RUN_AUTO",
        ]

        try:
            append_audit_with_alert(
                creds=creds,
                sheets_service=service,
                spreadsheet_id=AUDIT_SHEET_ID,
                tab_name=AUDIT_TAB,
                audit_row=audit_row,
                run_id="RUN_AUTO",
                request_id="AUTO",
            )
        except Exception as e:
            turbo_log(f"AUDIT FAILED (NON-BLOCKING): {e}")

    runtime = (datetime.now() - start).total_seconds()
    turbo_log(f"Sheet + Audit completed in {runtime:.3f}s")

    return {
        "status": "updated_turbo_with_audit",
        "row": matched_row,
        "seconds": runtime,
    }
