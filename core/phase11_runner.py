# ------------------------------------------------------------
# PHASE 11 RUNNER (FINAL, STABLE)
# ------------------------------------------------------------
# Exports: run_phase11_background
# ------------------------------------------------------------

import threading
from core.job_store import job_store
from pipeline_engine import pipeline

# OPTIONAL audit imports (safe)
try:
    from utils.audit_logger import (
        append_audit_with_alert,
        update_audit_log_trace_id,
    )
except Exception:
    append_audit_with_alert = None
    update_audit_log_trace_id = None


def _run(trace_id: str, payload: dict):
    try:
        result = pipeline.run(payload)
        job_store.update_job(
            trace_id,
            status="DONE",
            result=result
        )
    except Exception as e:
        job_store.update_job(
            trace_id,
            status="FAILED",
            error=str(e)
        )


def run_phase11_background(
    trace_id: str,
    payload: dict,
    *,
    # ---- OPTIONAL AUDIT CONTEXT (PASS ONLY IF AVAILABLE) ----
    creds=None,
    sheets_service=None,
    spreadsheet_id=None,
    audit_row=None,          # [PHASE, MODE, STATUS, RFQS_TOTAL, RFQS_PROCESSED]
    audit_row_number=None,   # 1-based row index (Column H)
    run_id=None,
    request_id=None,
):
    """
    Public API — DO NOT RENAME.
    Used by main_server.py

    Audit behavior:
    - If audit params are provided, will:
      1) append audit row (C:G)
      2) update TRACE_ID in SAME row (B{row_number})
    - If not provided, runs safely without audit.
    """

    # ---- JOB STORE (UNCHANGED) ----
    job_store.create_job(
        trace_id=trace_id,
        status="RUNNING",
        mode="async"
    )

    # ---- AUDIT: APPEND + TRACE_ID UPDATE (SAFE, OPTIONAL) ----
    if (
        append_audit_with_alert
        and update_audit_log_trace_id
        and sheets_service
        and spreadsheet_id
        and audit_row
        and audit_row_number
    ):
        # 1) Append audit row (C:G)
        append_audit_with_alert(
            creds=creds,
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            tab_name="audit_log",
            audit_row=audit_row,
            run_id=run_id,
            request_id=request_id,
        )

        # 2) Update TRACE_ID in SAME row (B{row})
        update_audit_log_trace_id(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            row_number=audit_row_number,
            trace_id=trace_id,
        )

    # ---- BACKGROUND THREAD (UNCHANGED) ----
    t = threading.Thread(
        target=_run,
        args=(trace_id, payload),
        daemon=True
    )
    t.start()
