# ------------------------------------------------------------
# AUDIT LOGGER — LEVEL 80
# FINAL, NULL-SAFE, PROD-SAFE
# ------------------------------------------------------------

from datetime import datetime
from googleapiclient.discovery import Resource
from config import AUDIT_TAB


def append_audit_with_alert(
    *,
    sheets_service: Resource,
    spreadsheet_id: str,
    tab_name: str,
    audit_row: list,
    run_id: str,
    request_id: str,
):
    """
    Appends a new audit row.
    MUST NEVER RAISE.
    Returns row_number or None.
    """
    try:
        values = [[
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),  # TIMESTAMP_IST
            request_id,                                  # TRACE_ID
            run_id,                                      # PHASE
            audit_row[1],                                # MODE / PAYLOAD
            audit_row[2],                                # STATUS
            audit_row[3] or "",                          # RFQS_TOTAL
            audit_row[4] or "",                          # RFQS_PROCESSED
        ]]

        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=tab_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": values},
        ).execute()

        updated_range = result["updates"]["updatedRange"]
        # Example: LEVEL_80_AUDIT_LOG!A12:G12
        row_number = int(updated_range.split("!")[1].split(":")[0][1:])
        return row_number

    except Exception:
        # 🔒 HARD SAFETY — audit must never break prod
        return None


def update_audit_log_trace_id(
    *,
    sheets_service: Resource,
    spreadsheet_id: str,
    tab_name: str,
    row_number: int,
    trace_id: str,
):
    if not row_number:
        return

    try:
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{tab_name}!B{row_number}",
            valueInputOption="RAW",
            body={"values": [[trace_id]]},
        ).execute()
    except Exception:
        return


def update_audit_log_on_completion(
    *,
    sheets_service: Resource,
    spreadsheet_id: str,
    tab_name: str,
    row_number: int,
    status: str,
    rfqs_processed: int,
    details_json: dict,
):
    if not row_number:
        return

    try:
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{tab_name}!E{row_number}:G{row_number}",
            valueInputOption="RAW",
            body={"values": [[status, "", rfqs_processed]]},
        ).execute()
    except Exception:
        return
