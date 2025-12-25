# ------------------------------------------------------------
# PHASE 11 RUNNER (FINAL, GUARANTEED, PROD-SAFE)
# ------------------------------------------------------------
# - Starts async pipeline
# - Writes audit row at START
# - Updates SAME audit row on DONE / FAILED
# ------------------------------------------------------------

import threading

from core.job_store import job_store
from core.pipeline import pipeline

from utils.audit_logger import (
    append_audit_with_alert,
    update_audit_log_trace_id,
    update_audit_log_on_completion,
)

from config import SHEET_ID
from utils.sheets import get_sheets_service


def _run(trace_id: str, payload: dict, audit_row_number: int):
    sheets_service = get_sheets_service()

    try:
        # ---- ACTUAL PIPELINE RUN ----
        result = pipeline.run(payload)

        # ---- JOB STORE UPDATE ----
        job_store.update_job(
            trace_id,
            status="DONE",
            result=result
        )

        # ---- AUDIT UPDATE (SUCCESS) ----
        update_audit_log_on_completion(
            sheets_service=sheets_service,
            spreadsheet_id=SHEET_ID,
            row_number=audit_row_number,
            status="DONE",
            rfqs_processed=result.get("processed"),
            details_json=result
        )

    except Exception as e:
        # ---- JOB STORE UPDATE ----
        job_store.update_job(
            trace_id,
            status="FAILED",
            error=str(e)
        )

        # ---- AUDIT UPDATE (FAILED) ----
        update_audit_log_on_completion(
            sheets_service=sheets_service,
            spreadsheet_id=SHEET_ID,
            row_number=audit_row_number,
            status="FAILED",
            rfqs_processed=0,
            details_json={"error": str(e)}
        )


def run_phase11_background(trace_id: str, payload: dict):
    """
    Public API — USED BY main_server.py
    DO NOT RENAME
    """

    sheets_service = get_sheets_service()

    # ---- JOB STORE CREATE ----
    job_store.create_job(
        trace_id=trace_id,
        status="RUNNING",
        mode="async"
    )

    # ---- AUDIT START ROW (C:G) ----
    audit_row_number = append_audit_with_alert(
        creds=None,
        sheets_service=sheets_service,
        spreadsheet_id=SHEET_ID,
        tab_name="audit_log",
        audit_row=[
            "phase11",
            payload,
            "RUNNING",
            None,
            None
        ],
        run_id="PHASE11",
        request_id=trace_id
    )

    # ---- TRACE_ID UPDATE (B{row}) ----
    update_audit_log_trace_id(
        sheets_service=sheets_service,
        spreadsheet_id=SHEET_ID,
        row_number=audit_row_number,
        trace_id=trace_id
    )

    # ---- BACKGROUND THREAD ----
    t = threading.Thread(
        target=_run,
        args=(trace_id, payload, audit_row_number),
        daemon=True
    )
    t.start()
