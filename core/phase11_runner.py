# ------------------------------------------------------------
# PHASE 11 RUNNER — FINAL, PROD-SAFE, AUDIT-GUARANTEED
# ------------------------------------------------------------

import threading

from pipeline_engine import pipeline
from core.job_store import job_store

from utils.audit_logger import (
    append_audit_with_alert,
    update_audit_log_trace_id,
    update_audit_log_on_completion,
)

from utils.sheet_updater import get_sheets_service
from config import SHEET_ID, AUDIT_TAB


def _run(trace_id: str, payload: dict, audit_row: int):
    sheets = get_sheets_service()

    try:
        result = pipeline.run(payload)

        job_store.update_job(
            trace_id=trace_id,
            status="DONE",
            result=result,
            error=None,
        )

        update_audit_log_on_completion(
            sheets_service=sheets,
            spreadsheet_id=SHEET_ID,
            tab_name=AUDIT_TAB,
            row_number=audit_row,
            status="DONE",
            rfqs_processed=result.get("processed", 0),
            details_json=result,
        )

    except Exception as e:
        job_store.update_job(
            trace_id=trace_id,
            status="FAILED",
            result=None,
            error=str(e),
        )

        update_audit_log_on_completion(
            sheets_service=sheets,
            spreadsheet_id=SHEET_ID,
            tab_name=AUDIT_TAB,
            row_number=audit_row,
            status="FAILED",
            rfqs_processed=0,
            details_json={"error": str(e)},
        )


def run_phase11_background(trace_id: str, payload: dict):
    payload = payload or {}

    # -------------------------------
    # PING MODE (NO SHEETS)
    # -------------------------------
    if payload.get("mode") == "ping":
        job_store.create_job(trace_id, "DONE", mode="ping")
        job_store.update_job(trace_id, "DONE", {"status": "OK"}, None)
        return

    sheets = get_sheets_service()

    job_store.create_job(trace_id, "RUNNING", mode="async")

    audit_row = append_audit_with_alert(
        sheets_service=sheets,
        spreadsheet_id=SHEET_ID,
        tab_name=AUDIT_TAB,
        audit_row=[
            "phase11",
            payload,
            "RUNNING",
            "",
            "",
        ],
        run_id="PHASE11",
        request_id=trace_id,
    )

    update_audit_log_trace_id(
        sheets_service=sheets,
        spreadsheet_id=SHEET_ID,
        tab_name=AUDIT_TAB,
        row_number=audit_row,
        trace_id=trace_id,
    )

    t = threading.Thread(
        target=_run,
        args=(trace_id, payload, audit_row),
        daemon=True,
    )
    t.start()
