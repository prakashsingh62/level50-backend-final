# ------------------------------------------------------------
# PHASE 11 RUNNER — FINAL, AUDIT-AUTHORITATIVE
# ------------------------------------------------------------

import threading
from core.job_store import job_store
from pipeline_engine import pipeline
from utils.sheet_updater import get_sheets_service
from utils.audit_logger import (
    append_audit_with_alert,
    update_audit_log_trace_id,
    update_audit_log_on_completion,
)
from config import SHEET_ID, AUDIT_TAB


def _run(trace_id: str, payload: dict, audit_row_number: int):
    sheets_service = get_sheets_service()

    try:
        result = pipeline.run(payload)

        job_store.update_job(
            trace_id=trace_id,
            status="DONE",
            result=result,
            error=None,
        )

        update_audit_log_on_completion(
            sheets_service=sheets_service,
            spreadsheet_id=SHEET_ID,
            tab_name=AUDIT_TAB,
            row_number=audit_row_number,
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
            sheets_service=sheets_service,
            spreadsheet_id=SHEET_ID,
            tab_name=AUDIT_TAB,
            row_number=audit_row_number,
            status="FAILED",
            rfqs_processed=0,
            details_json={"error": str(e)},
        )


def run_phase11_background(trace_id: str, payload: dict):
    payload = payload or {}

    # -------------------------------
    # HARD PING ISOLATION
    # -------------------------------
    if payload.get("mode") == "ping":
        job_store.create_job(trace_id=trace_id, status="DONE", mode="ping")
        job_store.update_job(
            trace_id=trace_id,
            status="DONE",
            result={"status": "OK", "mode": "PING"},
            error=None,
        )
        return

    sheets_service = get_sheets_service()

    job_store.create_job(trace_id=trace_id, status="RUNNING", mode="async")

    audit_row_number = append_audit_with_alert(
        sheets_service=sheets_service,
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
        sheets_service=sheets_service,
        spreadsheet_id=SHEET_ID,
        tab_name=AUDIT_TAB,
        row_number=audit_row_number,
        trace_id=trace_id,
    )

    t = threading.Thread(
        target=_run,
        args=(trace_id, payload, audit_row_number),
        daemon=True,
    )
    t.start()
