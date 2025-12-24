# core/run_audit_logger.py

import json
from datetime import datetime, timezone, timedelta

from utils.sheet_updater import append_row_safe as append_row
from config import AUDIT_SHEET_ID

# IST timezone
IST = timezone(timedelta(hours=5, minutes=30))


def _now_ist():
    return datetime.now(IST).isoformat()


def log_run_start(trace_id: str, phase: str, mode: str):
    """
    Logs Phase run START event
    """
    row = [
        _now_ist(),          # TIMESTAMP_IST
        trace_id,            # TRACE_ID
        phase,               # PHASE
        mode,                # MODE
        "RUNNING",           # STATUS
        None,                # RFQS_TOTAL
        None,                # RFQS_PROCESSED
        None,                # ERROR_SUMMARY
        json.dumps(
            {"event": "START"},
            ensure_ascii=False
        ),                   # DETAILS_JSON
    ]

    append_row(AUDIT_SHEET_ID, "LEVEL_80_RUN_AUDIT", row)


def log_run_success(
    trace_id: str,
    phase: str,
    mode: str,
    rfqs_total: int,
    rfqs_processed: int,
):
    """
    Logs Phase run SUCCESS event
    """
    row = [
        _now_ist(),          # TIMESTAMP_IST
        trace_id,            # TRACE_ID
        phase,               # PHASE
        mode,                # MODE
        "SUCCESS",           # STATUS
        rfqs_total,          # RFQS_TOTAL
        rfqs_processed,      # RFQS_PROCESSED
        None,                # ERROR_SUMMARY
        json.dumps(
            {
                "result": {
                    "status": "OK",
                    "processed": rfqs_processed,
                }
            },
            ensure_ascii=False
        ),                   # DETAILS_JSON
    ]

    append_row(AUDIT_SHEET_ID, "LEVEL_80_RUN_AUDIT", row)


def log_run_failure(
    trace_id: str,
    phase: str,
    mode: str,
    error: Exception,
):
    """
    Logs Phase run FAILURE event
    """
    row = [
        _now_ist(),          # TIMESTAMP_IST
        trace_id,            # TRACE_ID
        phase,               # PHASE
        mode,                # MODE
        "FAILED",            # STATUS
        None,                # RFQS_TOTAL
        None,                # RFQS_PROCESSED
        str(error),          # ERROR_SUMMARY
        json.dumps(
            {
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
            ensure_ascii=False
        ),                   # DETAILS_JSON
    ]

    append_row(AUDIT_SHEET_ID, "LEVEL_80_RUN_AUDIT", row)
