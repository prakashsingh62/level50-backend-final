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
    **kwargs,   # 🔒 FUTURE-PROOF GUARD (absorbs creds, anything)
):
    values = [[
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        request_id,
        run_id,
        audit_row[1],
        audit_row[2],
        audit_row[3],
        audit_row[4],
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


def update_audit_log_trace_id(
    *,
    sheets_service: Resource,
    spreadsheet_id: str,
    row_number: int,
    trace_id: str,
    **kwargs,   # 🔒 FUTURE-PROOF
):
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{AUDIT_TAB}!B{row_number}",
        valueInputOption="RAW",
        body={"values": [[trace_id]]},
    ).execute()


def update_audit_log_on_completion(
    *,
    sheets_service: Resource,
    spreadsheet_id: str,
    row_number: int,
    status: str,
    rfqs_processed: int,
    details_json: dict,
    **kwargs,   # 🔒 FUTURE-PROOF
):
    if not row_number:
        return

    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{AUDIT_TAB}!E{row_number}:G{row_number}",
        valueInputOption="RAW",
        body={"values": [[status, "", rfqs_processed]]},
    ).execute()
