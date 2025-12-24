# core/run_audit_logger.py

import json
from datetime import datetime, timezone, timedelta

from sheet_writer import append_row
from config import AUDIT_SHEET_ID

IST = timezone(timedelta(hours=5, minutes=30))


def _now_ist():
    return datetime.now(IST).isoformat()


def log_run_start(trace_id: str, phase: str, mode: str):
    row = [
        _now_ist(),
        trace_id,
        phase,
        mode,
        "RUNNING",
        "",
        "",
        "",
        json.dumps({"event": "START"}, ensure_ascii=False),
    ]
    append_row(AUDIT_SHEET_ID, "audit_log", row)


def log_run_success(
    trace_id: str,
    phase: str,
    mode: str,
    rfqs_total: int,
    rfqs_processed: int,
):
    row = [
        _now_ist(),
        trace_id,
        phase,
        mode,
        "SUCCESS",
        rfqs_total,
        rfqs_processed,
        "",
        json.dumps(
            {
                "result": {
                    "status": "OK",
                    "processed": rfqs_processed,
                }
            },
            ensure_ascii=False,
        ),
    ]
    append_row(AUDIT_SHEET_ID, "audit_log", row)


def log_run_failure(trace_id: str, phase: str, mode: str, error: Exception):
    row = [
        _now_ist(),
        trace_id,
        phase,
        mode,
        "FAILED",
        "",
        "",
        str(error),
        json.dumps(
            {
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
            ensure_ascii=False,
        ),
    ]
    append_row(AUDIT_SHEET_ID, "audit_log", row)
