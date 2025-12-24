# core/run_audit_logger.py

import json
from datetime import datetime, timezone, timedelta

from utils.sheet_updater import write_audit_row
from config import AUDIT_SHEET_ID

# IST timezone
IST = timezone(timedelta(hours=5, minutes=30))


def _now_ist():
    return datetime.now(IST)


def log_run_start(trace_id: str, phase: str, mode: str):
    row = [
        _now_ist().isoformat(),   # TIMESTAMP_IST
        trace_id,                 # TRACE_ID
        phase,                    # PHASE
        mode,                     # MODE
        "RUNNING",                # STATUS
        "",                        # RFQS_TOTAL
        "",                        # RFQS_PROCESSED
        "",                        # ERROR_SUMMARY
        json.dumps({"event": "START"}, ensure_ascii=False),  # DETAILS_JSON
    ]

    write_audit_row(
        spreadsheet_id=AUDIT_SHEET_ID,
        tab_name="audit_log",
        audit_row=row,
    )


def log_run_success(
    trace_id: str,
    phase: str,
    mode: str,
    rfqs_total: int,
    rfqs_processed: int,
):
    row = [
        _now_ist().isoformat(),   # TIMESTAMP_IST
        trace_id,                 # TRACE_ID
        phase,                    # PHASE
        mode,                     # MODE
        "SUCCESS",                # STATUS
        rfqs_total,               # RFQS_TOTAL
        rfqs_processed,           # RFQS_PROCESSED
        "",                        # ERROR_SUMMARY
        json.dumps(
            {
                "result": {
                    "status": "OK",
                    "processed": rfqs_processed,
                }
            },
            ensure_ascii=False,
        ),                         # DETAILS_JSON
    ]

    write_audit_row(
        spreadsheet_id=AUDIT_SHEET_ID,
        tab_name="audit_log",
        audit_row=row,
    )


def log_run_failure(
    trace_id: str,
    phase: str,
    mode: str,
    error: Exception,
):
    row = [
        _now_ist().isoformat(),   # TIMESTAMP_IST
        trace_id,                 # TRACE_ID
        phase,                    # PHASE
        mode,                     # MODE
        "FAILED",                 # STATUS
        "",                        # RFQS_TOTAL
        "",                        # RFQS_PROCESSED
        str(error),               # ERROR_SUMMARY
        json.dumps(
            {
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
            ensure_ascii=False,
        ),                         # DETAILS_JSON
    ]

    write_audit_row(
        spreadsheet_id=AUDIT_SHEET_ID,
        tab_name="audit_log",
        audit_row=row,
    )
