# ------------------------------------------------------------
# LEVEL 80 – AUDIT LOGGER (FINAL, FIXED, PROD-SAFE)
# ------------------------------------------------------------
# Columns (FIXED):
# A TIMESTAMP_IST
# B TRACE_ID
# C PHASE
# D MODE
# E STATUS
# F RFQS_TOTAL
# G RFQS_PROCESSED
# H ROW_NUMBER
# I ERROR_SUMMARY
# J DETAILS_JSON
# ------------------------------------------------------------

from utils.time_ist import ist_timestamp


def append_audit_with_alert(
    creds,
    sheets_service,
    spreadsheet_id,
    tab_name,
    audit_row,
    run_id,
    request_id,
):
    """
    Appends ONE audit row.
    audit_row = [PHASE, MODE, STATUS, RFQS_TOTAL, RFQS_PROCESSED]
    Returns row_number.
    """

    if not isinstance(audit_row, (list, tuple)) or len(audit_row) != 5:
        raise ValueError("AUDIT_ROW_MUST_BE_LEN_5")

    timestamp = ist_timestamp()

    # Exact column alignment A:J
    values = [[
        timestamp,          # A TIMESTAMP_IST
        "",                 # B TRACE_ID (updated later)
        audit_row[0],       # C PHASE
        audit_row[1],       # D MODE
        audit_row[2],       # E STATUS
        audit_row[3],       # F RFQS_TOTAL
        audit_row[4],       # G RFQS_PROCESSED
        "",                 # H ROW_NUMBER (written below)
        "",                 # I ERROR_SUMMARY
        "",                 # J DETAILS_JSON
    ]]

    resp = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!A:J",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": values},
    ).execute()

    updated_range = resp["updates"]["updatedRange"]  # audit_log!A12:J12
    row_number = int(updated_range.split("!")[1].split(":")[0][1:])

    # Write ROW_NUMBER (H)
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!H{row_number}",
        valueInputOption="RAW",
        body={"values": [[row_number]]},
    ).execute()

    return row_number


def update_audit_log_trace_id(
    sheets_service,
    spreadsheet_id,
    row_number,
    trace_id,
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
    details_json,
):
    """
    Updates completion fields only.
    """

    error_summary = ""
    if status == "FAILED":
        error_summary = str(details_json)[:300]

    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"audit_log!E{row_number}:J{row_number}",
        valueInputOption="RAW",
        body={"values": [[
            status,            # E STATUS
            None,              # F RFQS_TOTAL (unchanged)
            rfqs_processed,    # G RFQS_PROCESSED
            row_number,        # H ROW_NUMBER (idempotent)
            error_summary,     # I ERROR_SUMMARY
            str(details_json), # J DETAILS_JSON
        ]]},
    ).execute()
