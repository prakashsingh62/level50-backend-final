from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime

# ---------------------------------------------------------------------
# LEVEL-70 RULE:
# NP rows are skipped in Step-3 and Step-7.
# Step-4 must NEVER block manual Google Sheet edits.
# Retry Queue handles failed sheet updates safely.
# ---------------------------------------------------------------------

SHEET_ID = "1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo"
TAB_NAME = "RFQ TEST SHEET"

COL_VENDOR_STATUS = 34
COL_QUOTATION_DATE = 20
COL_REMARKS = 35
COL_FOLLOWUP_DATE = 36


def get_service():
    creds = Credentials.from_service_account_file(
        "client_secret.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=creds)


def normalize_date(date_str):
    if not date_str:
        return ""
    date_str = date_str.replace("-", "/").strip()
    try:
        d = datetime.strptime(date_str, "%d/%m/%Y")
        return d.strftime("%d/%m/%Y")
    except:
        return ""


# ---------------------------------------------------------------------
# MAIN UPDATE FUNCTION WITH RETRY QUEUE SUPPORT
# ---------------------------------------------------------------------
def update_rfq_row(matched_row: int, ai_output: dict):
    service = get_service()
    range_to_fetch = f"{TAB_NAME}!A{matched_row}:AZ{matched_row}"

    try:
        # Fetch row
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=range_to_fetch
        ).execute()

        existing_row = result.get("values", [[]])[0]

        if len(existing_row) < 52:
            existing_row += [""] * (52 - len(existing_row))

        # Extract AI fields
        vendor_status = ai_output.get("vendor_status", "").strip()
        quotation_date = normalize_date(ai_output.get("quotation_date", ""))
        remarks = ai_output.get("remarks", "").strip()
        followup_date = normalize_date(ai_output.get("followup_date", ""))

        # Update cells
        if vendor_status:
            existing_row[COL_VENDOR_STATUS] = vendor_status
        if quotation_date:
            existing_row[COL_QUOTATION_DATE] = quotation_date
        if remarks:
            existing_row[COL_REMARKS] = remarks
        if followup_date:
            existing_row[COL_FOLLOWUP_DATE] = followup_date

        body = {"values": [existing_row]}

        service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=range_to_fetch,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

        return {
            "status": "updated",
            "row": matched_row,
            "updated_fields": {
                "vendor_status": vendor_status,
                "quotation_date": quotation_date,
                "remarks": remarks,
                "followup_date": followup_date
            }
        }

    except Exception as e:
        # Queue for retry if failure occurs
        from retry_queue.retry_queue_manager import queue_retry

        queue_retry({
            "type": "sheet_update",
            "row": matched_row,
            "payload": ai_output,
            "retry_count": 0
        })

        return {
            "status": "queued_for_retry",
            "error": str(e)
        }
