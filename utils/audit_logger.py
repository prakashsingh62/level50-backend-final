# utils/audit_logger.py
import datetime
from googleapiclient.discovery import Resource

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def _now_ist():
    return datetime.datetime.utcnow().isoformat()

def _safe(val):
    if val is None:
        return ""
    return str(val)

def _extract_row_number(updated_range: str) -> int:
    # Example: LEVEL_80_AUDIT_LOG!A12:E12
    return int(updated_range.split("!")[1].split(":")[0][1:])


# ------------------------------------------------------------
# APPEND AUDIT (INITIAL)
# ------------------------------------------------------------

def append_audit_with_alert(
    *,
    sheets_service: Resource,
    spreadsheet_id: str,
    tab_name: str,
    audit_row: list,
    run_id: str,
    request_id: str,
    creds=None,  # kept for compatibility
):
    values = [[
        _now_ist(),            # TIMESTAMP_IST
        request_id,            # TRACE_ID
        run_id,                # PHASE
        _safe(audit_row[1]),   # MODE / PAYLOAD
        "RUNNING",             # STATUS
        "",                    # RFQS_TOTAL
        "",                    # RFQS_PROCESSED
    ]]

    result = (
        sheets_service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=f"{tab_name}!A:G",   # ✅ IMPORTANT FIX
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": values},
        )
        .execute()
    )

    return _extract_row_number(result["updates"]["updatedRange"])


# ------------------------------------------------------------
# UPDATE TRACE ID
# ------------------------------------------------------------

def update_audit_log_trace_id(
    *,
    sheets_service: Resource,
    spreadsheet_id: str,
    row_number: int,
    trace_id: str,
):
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"AUDIT_80_AUDIT_LOG!B{row_number}",
        valueInputOption="RAW",
        body={"values": [[trace_id]]},
    ).execute()


# ------------------------------------------------------------
# FINAL STATUS UPDATE
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
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"LEVEL_80_AUDIT_LOG!E{row_number}:G{row_number}",
        valueInputOption="RAW",
        body={
            "values": [[
                status,
                _safe(details_json.get("processed", "")),
                _safe(rfqs_processed),
            ]]
        },
    ).execute()
