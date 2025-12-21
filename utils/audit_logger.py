# ------------------------------------------------------------
# LEVEL 80 – AUDIT LOGGER (FINAL, PROD-SAFE)
# ------------------------------------------------------------
# - Appends audit rows to LEVEL_80_AUDIT_LOG
# - Uses values().append (NOT batchUpdate)
# - Header-safe (starts from A2)
# - Raises error on failure (NO silent swallow)
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
    Any failure here MUST raise error (no swallow).
    """

    try:
        sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{tab_name}!A2",   # 🔥 IMPORTANT: NOT A1
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={
                "values": [audit_row]
            }
        ).execute()

    except Exception as e:
        # ❌ DO NOT SWALLOW AUDIT FAILURE
        # This guarantees visibility
        raise RuntimeError(f"AUDIT_WRITE_FAILED: {str(e)}")
