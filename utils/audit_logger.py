# ------------------------------------------------------------
# AUDIT LOGGER — NULL SAFE, PROD SAFE (FINAL)
# ------------------------------------------------------------

from googleapiclient.discovery import Resource


# ------------------------------------------------------------
# INTERNAL HELPERS
# ------------------------------------------------------------

def _safe(value):
    """
    Google Sheets DOES NOT accept NULL.
    Convert None → empty string.
    """
    if value is None:
        return ""
    return value


def _sanitize_row(row):
    return [_safe(col) for col in row]


# ------------------------------------------------------------
# APPEND AUDIT ROW (INITIAL)
# ------------------------------------------------------------

def append_audit_with_alert(
    *,
    creds,
    sheets_service: Resource,
    spreadsheet_id: str,
    tab_name: str,
    audit_row: list,
    run_id: str,
    request_id: str,
):
    """
    Appends a new audit row and returns the row number.
    """

    # 🔒 NULL SAFE
    audit_row = _sanitize_row(audit_row)

    response = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={
            "values": [audit_row]
        },
    ).execute()

    # Extract appended row number safely
    updates = response.get("updates", {})
    updated_range = updates.get("updatedRange", "")

    # Example: LEVEL_80_AUDIT_LOG!A12:E12
    try:
        row_number = int(updated_range.split("!")[1].split(":")[0][1:])
    except Exception:
        # Absolute fallback (should not happen)
        row_number = None

    return row_number


# ------------------------------------------------------------
# UPDATE TRACE ID IN AUDIT ROW
# ------------------------------------------------------------

def update_audit_log_trace_id(
    *,
    sheets_service: Resource,
    spreadsheet_id: str,
    row_number: int,
    trace_id: str,
):
    """
    Writes trace_id into column B (or wherever required).
    """

    if not row_number:
        return

    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"AUDIT!B{row_number}",
        valueInputOption="RAW",
        body={
            "values": [[_safe(trace_id)]]
        },
    ).execute()


# ------------------------------------------------------------
# FINAL STATUS UPDATE (DONE / FAILED)
# ------------------------------------------------------------

def update_audit_log_on_completion(
    *,
    sheets_service: Resource,
    spreadsheet_id: str,
    row_number: int,
    status: str,
    rfqs_processed: int,
    details_json: dict,
):
    """
    Final audit update after pipeline completion.
    """

    if not row_number:
        return

    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"AUDIT!C{row_number}:E{row_number}",
        valueInputOption="RAW",
        body={
            "values": [[
                _safe(status),
                _safe(rfqs_processed),
                _safe(str(details_json)),
            ]]
        },
    ).execute()
