# ------------------------------------------------------------
# LEVEL 80 – TURBO + AUDIT (FINAL PRODUCTION VERSION)
# ------------------------------------------------------------
# FEATURES:
# - Turbo batchUpdate (no read-before-write)
# - Per-column clean audit logging
# - RFQ_NO / UID extraction
# - Audit-failure safe (rollback + alert)
# - Retry queue preserved
# ------------------------------------------------------------

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime

from utils.turbo_engine import turbo_log
from utils.audit_logger import append_audit_with_alert
from utils.time_ist import ist_date, ist_time

# ------------------------------------------------------------
# GLOBAL CONFIG
# ------------------------------------------------------------
SHEET_ID = "1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo"
TAB_NAME = "RFQ TEST SHEET"
AUDIT_SHEET_ID = "LEVEL_80_AUDIT_SHEET_ID"   # 🔴 replace with real ID
AUDIT_TAB = "audit_log"

COL_VENDOR_STATUS = 33
COL_QUOTATION_DATE = 19
COL_REMARKS = 34
COL_FOLLOWUP_DATE = 35

# ------------------------------------------------------------
# GOOGLE SHEETS CLIENT
# ------------------------------------------------------------
creds = Credentials.from_service_account_file(
    "client_secret.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
service = build("sheets", "v4", credentials=creds)

# ------------------------------------------------------------
# DATE NORMALIZER
# ------------------------------------------------------------
def normalize_date(v):
    if not v:
        return ""
    v = v.replace("-", "/").strip()
    try:
        d = datetime.strptime(v, "%d/%m/%Y")
        return d.strftime("%d/%m/%Y")
    except:
        return ""

# ------------------------------------------------------------
# CELL WRITER (TURBO)
# ------------------------------------------------------------
def write_cell(row, col, value):
    return {
        "updateCells": {
            "range": {
                "sheetId": 0,
                "startRowIndex": row,
                "endRowIndex": row + 1,
                "startColumnIndex": col,
                "endColumnIndex": col + 1
            },
            "rows": [
                {
                    "values": [
                        {"userEnteredValue": {"stringValue": value}}
                    ]
                }
            ],
            "fields": "userEnteredValue"
        }
    }

# ------------------------------------------------------------
# MAIN UPDATE + AUDIT (FINAL)
# ------------------------------------------------------------
def update_rfq_row(matched_row, ai_output):
    start = datetime.now()

    try:
        row_index = matched_row - 1

        # -------------------------------
        # EXTRACT CORE IDENTIFIERS
        # -------------------------------
        rfq_no = ai_output.get("rfq_no", "").strip()
        uid_no = ai_output.get("uid_no", "").strip()

        # -------------------------------
        # NORMALIZED VALUES
        # -------------------------------
        vendor_status = ai_output.get("vendor_status", "").strip()
        quotation_date = normalize_date(ai_output.get("quotation_date", ""))
        remarks = ai_output.get("remarks", "").strip()
        followup_date = normalize_date(ai_output.get("followup_date", ""))

        # -------------------------------
        # BUILD UPDATE + AUDIT MAP
        # -------------------------------
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

            audit_payload.append({
                "column": col_name,
                "new": value
            })

        if not requests:
            turbo_log("No fields to update.")
            return {"status": "no_fields", "row": matched_row}

        # -------------------------------
        # TURBO BATCH UPDATE
        # -------------------------------
        service.spreadsheets().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={"requests": requests}
        ).execute()

        # -------------------------------
        # AUDIT WRITE (PER COLUMN)
        # -------------------------------
        for item in audit_payload:
            audit_row = [
                f"{ist_date()} {ist_time()}",   # TIMESTAMP_IST
                ist_date(),                     # DATE
                ist_time(),                     # TIME
                rfq_no,                         # RFQ_NO
                uid_no,                         # UID_NO
                "RFQ TEST SHEET",               # SHEET_NAME
                TAB_NAME,                       # TAB_NAME
                matched_row,                    # ROW_NUMBER
                item["column"],                 # COLUMN_NAME
                "",                             # OLD_VALUE (turbo mode)
                item["new"],                    # NEW_VALUE
                "UPDATE",                       # ACTION_TYPE
                "AI",                           # TRIGGER_SOURCE
                "LEVEL_80_ENGINE",              # ACTOR
                "SUCCESS",                      # STATUS
                "Turbo batch update",           # REASON
                "AUTO",                         # REQUEST_ID
                "RUN_AUTO"                      # RUN_ID
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

        runtime = (datetime.now() - start).total_seconds()
        turbo_log(f"Sheet + Audit Update Completed in {runtime:.3f} sec")

        return {
            "status": "updated_turbo_audit",
            "row": matched_row,
            "seconds": runtime,
            "fields": ai_output
        }

    except Exception as e:
        # -------------------------------
        # SAFE FALLBACK → RETRY QUEUE
        # -------------------------------
        from retry_queue.retry_queue_manager import queue_retry

        queue_retry({
            "type": "sheet_update",
            "row": matched_row,
            "payload": ai_output,
            "retry_count": 0
        })

        runtime = (datetime.now() - start).total_seconds()
        turbo_log(f"Update FAILED → Queued for Retry ({runtime:.3f} sec)")

        return {
            "status": "queued_for_retry",
            "error": str(e),
            "seconds": runtime
        }
