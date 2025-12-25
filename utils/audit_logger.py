# ------------------------------------------------------------
# AUDIT LOGGER — FINAL, NULL SAFE, TAB SAFE
# ------------------------------------------------------------

from googleapiclient.discovery import Resource


# ------------------------------------------------------------
# INTERNAL HELPERS
# ------------------------------------------------------------

def _safe(value):
    return "" if value is None else value


def _sanitize_row(row):
    return [_safe(col) for col in row]


def _extract_row_number(updated_range: str):
    """
    Example updatedRange:
    LEVEL_80_AUDIT_LOG!A12:E12
    """
    try:
        return int(updated_range.split("!")[1].split(":")[0][1:])
    except Exception:
        return None


# ------------------------------------------------------------
# APPEND AUDIT ROW
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
    audit_row = _sanitize_row(audit_row)

    response = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [audit_row]},
    ).execute()

    updated_range = response.get("updates", {}).get("updatedRange", "")
    return _extract_row_number(updated_range)


# ------------------------------------------------------------
# UPDATE TRACE ID
# ------------------------------------------------------------

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

    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!B{row_number}",
        valueInputOption="RAW",
        body={"values": [[_safe(trace_id)]]},
    ).execute()


# ------------------------------------------------------------
# FINAL STATUS UPDATE
# ------------------------------------------------------------

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

    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!C{row_number}:E{row_number}",
        valueInputOption="RAW",
        body={
            "values": [[
                _safe(status),
                _safe(rfqs_processed),
                _safe(str(details_json)),
            ]]
        },
    ).execute()
