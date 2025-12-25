# ------------------------------------------------------------
# LEVEL 80 – AUDIT LOGGER (FINAL, PROD-SAFE)
# ------------------------------------------------------------
# - Appends audit rows to existing audit_log tab (C:G)
# - Updates ONLY TRACE_ID cell (B{row_number})
# - No clear(), no full-row update, no header touch
# - Raises error on failure
# ------------------------------------------------------------

from utils.time_ist import ist_date, ist_time


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
    Appends ONE audit row to columns C:G.

    audit_row MUST be:
    [PHASE, MODE(JSON/STR), STATUS, RFQS_TOTAL, RFQS_PROCESSED]
    """

    if not isinstance(audit_row, (list, tuple)):
        raise ValueError("AUDIT_ROW_INVALID_TYPE")

    if len(audit_row) != 5:
        raise ValueError("AUDIT_ROW_INVALID_LENGTH_EXPECTED_5")

    try:
        sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{tab_name}!C:G",          # C..G only
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [list(audit_row)]},
        ).execute()

    except Exception as e:
        raise RuntimeError(f"AUDIT_WRITE_FAILED: {str(e)}")


def update_audit_log_trace_id(
    sheets_service,
    spreadsheet_id,
    row_number,   # 1-based row index (Column H already stores this)
    trace_id
):
    """
    Updates ONLY the TRACE_ID cell (Column B) for an EXISTING row.
    No append. No other columns touched.
    """

    try:
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"audit_log!B{row_number}",  # Column B = TRACE_ID
            valueInputOption="RAW",
            body={"values": [[trace_id]]}
        ).execute()

    except Exception as e:
        raise RuntimeError(f"AUDIT_TRACE_ID_UPDATE_FAILED: {str(e)}")
