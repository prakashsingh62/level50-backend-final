from utils.gmail_alert import send_audit_failure_email
from utils.time_ist import ist_date, ist_time

# anti-spam guard (one alert per RUN_ID)
_ALERTED_RUN_IDS = set()


def append_audit_row(
    sheets_service,
    spreadsheet_id: str,
    tab_name: str,
    audit_row: list
):
    """
    Appends a single audit row to audit sheet.
    Returns number of rows appended.
    """
    body = {"values": [audit_row]}

    result = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

    return result.get("updates", {}).get("updatedRows", 0)


def append_audit_with_alert(
    creds,
    sheets_service,
    spreadsheet_id: str,
    tab_name: str,
    audit_row: list,
    run_id: str,
    request_id: str
):
    """
    Appends audit row.
    Sends EMAIL alert via Gmail API if append fails.
    Rolls back by re-raising exception.
    """
    try:
        rows = append_audit_row(
            sheets_service,
            spreadsheet_id,
            tab_name,
            audit_row
        )

        if rows == 0:
            raise RuntimeError("Audit append returned 0 rows")

    except Exception as e:
        if run_id not in _ALERTED_RUN_IDS:
            _ALERTED_RUN_IDS.add(run_id)

            subject = f"🚨 LEVEL-80 AUDIT FAILURE | RUN_ID={run_id}"

            body = f"""
Audit write FAILED.

Date: {ist_date()}
Time: {ist_time()} IST
RUN_ID: {run_id}
REQUEST_ID: {request_id}

Error:
{str(e)}

Status:
Main RFQ write rolled back.
No data corruption.

Action required:
Check audit sheet access / quota.
""".strip()

            send_audit_failure_email(
                creds=creds,
                subject=subject,
                body=body
            )

        # keep rollback intact
        raise
