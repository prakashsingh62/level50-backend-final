# ------------------------------------------------------------
# LEVEL 70 – TURBO-INTEGRATED STEP-4 (Super-Optimized Updater)
# ------------------------------------------------------------
# SPEED FEATURES:
# - Global cached Google Sheets client (0 ms warmup)
# - No read-before-write (fastest possible)
# - Smart-delta engine (optional safety)
# - Turbo Engine logs for performance visibility
# - BatchUpdate API (single fast call)
#
# SAFETY:
# - NO change to Level-70 logic
# - NO effect on Step-3 / Step-5 / Step-6 / Step-7
# - NP skip still handled only at Step-3 / Step-7
# - Approval Gate unchanged
# - Retry Queue fully preserved
# ------------------------------------------------------------

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime

# TURBO ENGINE IMPORTS
from utils.turbo_engine import turbo_log, build_bulk_update_requests

# ------------------------------------------------------------
# GLOBAL CONFIG
# ------------------------------------------------------------
SHEET_ID = "1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo"
TAB_NAME = "RFQ TEST SHEET"

COL_VENDOR_STATUS = 33
COL_QUOTATION_DATE = 19
COL_REMARKS = 34
COL_FOLLOWUP_DATE = 35

# ------------------------------------------------------------
# GLOBAL GOOGLE SHEETS CLIENT (FASTEST)
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
# CELL WRITER (Turbo-Optimized)
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
# MAIN TURBO-INTEGRATED UPDATE FUNCTION
# ------------------------------------------------------------
def update_rfq_row(matched_row, ai_output):
    start = datetime.now()  # turbo timing

    try:
        row_index = matched_row - 1

        vendor_status = ai_output.get("vendor_status", "").strip()
        quotation_date = normalize_date(ai_output.get("quotation_date", ""))
        remarks = ai_output.get("remarks", "").strip()
        followup_date = normalize_date(ai_output.get("followup_date", ""))

        requests = []

        if vendor_status:
            requests.append(write_cell(row_index, COL_VENDOR_STATUS, vendor_status))

        if quotation_date:
            requests.append(write_cell(row_index, COL_QUOTATION_DATE, quotation_date))

        if remarks:
            requests.append(write_cell(row_index, COL_REMARKS, remarks))

        if followup_date:
            requests.append(write_cell(row_index, COL_FOLLOWUP_DATE, followup_date))

        if not requests:
            turbo_log("No fields to update.")
            return {"status": "no_fields", "row": matched_row}

        # TURBO BATCH UPDATE
        service.spreadsheets().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={"requests": requests}
        ).execute()

        runtime = (datetime.now() - start).total_seconds()
        turbo_log(f"Sheet Update Completed in {runtime:.3f} sec")

        return {
            "status": "updated_turbo",
            "row": matched_row,
            "seconds": runtime,
            "fields": ai_output
        }

    except Exception as e:
        # SAFE FALLBACK → RETRY QUEUE
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
