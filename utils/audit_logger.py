# ------------------------------------------------------------
# LEVEL 80 – AUDIT LOGGER (FINAL, STABLE)
# ------------------------------------------------------------

from googleapiclient.discovery import build


def append_audit_with_alert(
    creds,
    sheets_service,
    spreadsheet_id,
    tab_name,
    audit_row,
    run_id,
    request_id
):
    """
    Appends audit row to C:G
    Returns row_number (int)
    """

    result = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!C:G",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [audit_row]},
    ).execute()

    updates = result.get("updates", {})
    updated_range = updates.get("updatedRange")  # audit_log!C8:G8
    row_number = int(updated_range.split("!")[1][1:].split(":")[0])

    return row_number


def update_audit_log_trace_id(
    sheets_service,
    spreadsheet_id,
    row_number,
    trace_id
):
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"audit_log!B{row_number}",
        valueInputOption="RAW",
        body={"values": [[trace_id]]},
    ).execute()


def update_audit_log_on_completion(
    sheets_service,
    spreadsheet_id,
    row_number,
    status,
    rfqs_processed,
    details_json
):
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"audit_log!E{row_number}:G{row_number}",
        valueInputOption="RAW",
        body={
            "values": [[
                status,
                rfqs_processed,
                str(details_json)
            ]]
        },
    ).execute()
