from datetime import datetime
from googleapiclient.discovery import Resource

# ============================================================
# AUDIT LOGGER — HARD-SAFE, BACKWARD-COMPATIBLE
# ============================================================


def append_audit_with_alert(
    *,
    sheets_service: Resource,
    spreadsheet_id: str,
    tab_name: str,
    audit_row: list,
    run_id: str,
    request_id: str,
    **_ignored,  # 🔒 absorbs legacy args like creds
):
    try:
        values = [[
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            request_id,
            run_id,
            audit_row[0],   # PHASE
            audit_row[1],   # MODE / PAYLOAD
            audit_row[2],   # STATUS
            audit_row[3],   # RFQS_TOTAL
            audit_row[4],   # RFQS_PROCESSED
        ]]

        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=tab_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": values},
        ).execute()

        updated_range = result["updates"]["updatedRange"]
        row_number = int(updated_range.split("!")[1].split(":")[0][1:])
        return row_number

    except Exception:
        # 🔒 audit must NEVER break pipeline
        return None


def update_audit_log_trace_id(
    *,
    sheets_service: Resource,
    spreadsheet_id: str,
    tab_name: str,
    row_number: int,
    trace_id: str,
    **_ignored,
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
        pass


def update_audit_log_on_completion(
    *,
    sheets_service: Resource,
    spreadsheet_id: str,
    tab_name: str,
    row_number: int,
    status: str,
    rfqs_processed: int,
    details_json: dict,
    **_ignored,
):
    if not row_number:
        return

    try:
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{tab_name}!F{row_number}:G{row_number}",
            valueInputOption="RAW",
            body={"values": [[status, rfqs_processed]]},
        ).execute()
    except Exception:
        pass
