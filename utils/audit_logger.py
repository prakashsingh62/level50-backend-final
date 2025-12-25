# ------------------------------------------------------------
# LEVEL 80 – AUDIT LOGGER (FINAL, PROD-SAFE)
# ------------------------------------------------------------
# GUARANTEES:
# - Append audit row ONLY to C:G
# - Update ONLY TRACE_ID (B)
# - Update ONLY completion fields (E:F)
# - No clear(), no overwrite, no header touch
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
    Returns the 1-based row number inserted.
    """

    if not isinstance(audit_row, (list, tuple)):
        raise ValueError("AUDIT_ROW_INVALID_TYPE")

    if len(audit_row) != 5:
        raise ValueError("AUDIT_ROW_INVALID_LENGTH_EXPECTED_5")

    body = {
        "values": [[
            f"{ist_date()} {ist_time()}",  # C handled by sheet formula or ignored
            *audit_row
        ]]
    }

    try:
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{tab_name}!C:G",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [list(audit_row)]},
        ).execute()

        # Extract row number from response
        updated_range = result.get("updates", {}).get("updatedRange")
        # Example: audit_log!C7:G7
        row_number = int(updated_range.split("!")[1].split(":")[0][1:])

        return row_number

    except Exception as e:
        raise RuntimeError(f"AUDIT_WRITE_FAILED: {str(e)}")


def update_audit_log_trace_id(
    sheets_service,
    spreadsheet_id,
    row_number,
    trace_id
):
    """
    Updates ONLY TRACE_ID cell (Column B).
    """

    try:
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"audit_log!B{row_number}",
            valueInputOption="RAW",
            body={"values": [[trace_id]]}
        ).execute()

    except Exception as e:
        raise RuntimeError(f"AUDIT_TRACE_ID_UPDATE_FAILED: {str(e)}")


def update_audit_log_on_completion(
    sheets_service,
    spreadsheet_id,
    row_number,
    status,
    rfqs_processed,
    details_json
):
    """
    FINAL STATUS UPDATE:
    - Column E = STATUS
    - Column F = RFQS_PROCESSED
    """

    try:
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"audit_log!E{row_number}:F{row_number}",
            valueInputOption="RAW",
            body={
                "values": [[
                    status,
                    rfqs_processed
                ]]
            }
        ).execute()

    except Exception as e:
        raise RuntimeError(f"AUDIT_COMPLETION_UPDATE_FAILED: {str(e)}")
