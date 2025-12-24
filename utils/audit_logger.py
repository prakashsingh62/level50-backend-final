# ------------------------------------------------------------
# LEVEL 80 – AUDIT LOGGER (FINAL, PROD-SAFE)
# ------------------------------------------------------------
# - Appends audit rows to existing audit_log tab
# - Uses values().append ONLY (no clear, no update)
# - Correct column alignment (C:G)
# - Raises error on failure (no silent swallow)
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
    Appends ONE audit row.
    Hard rules:
    - append only
    - correct column range (C:G)
    - never swallow failures
    """

    # Expect audit_row to match columns C:G exactly
    # [PHASE, MODE(JSON/STR), STATUS, RFQS_TOTAL, RFQS_PROCESSED]
    if not isinstance(audit_row, (list, tuple)):
        raise ValueError("AUDIT_ROW_INVALID_TYPE")

    if len(audit_row) != 5:
        raise ValueError("AUDIT_ROW_INVALID_LENGTH_EXPECTED_5")

    try:
        sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{tab_name}!C:G",  # ✅ FIXED: correct columns
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [list(audit_row)]},
        ).execute()

    except Exception as e:
        # ❌ DO NOT SWALLOW AUDIT FAILURE
        raise RuntimeError(f"AUDIT_WRITE_FAILED: {str(e)}")
