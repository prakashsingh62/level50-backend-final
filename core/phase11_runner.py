# ------------------------------------------------------------
# PHASE 11 RUNNER (FINAL, AUDIT-RUNNING + DONE FIXED)
# ------------------------------------------------------------

import threading

from core.job_store import job_store
from pipeline_engine import pipeline

from utils.audit_logger import (
    append_audit_with_alert,
    update_audit_log_trace_id,
    update_audit_log_on_completion,
)

from utils.sheet_updater import get_sheets_service
from config import SHEET_ID


def _run(trace_id: str, payload: dict, audit_row_number: int):
    sheets_service = get_sheets_service()

    try:
        # ---- ACTUAL PIPELINE RUN ----
        result = pipeline.run(payload)

        # ---- JOB STORE UPDATE ----
        job_store.update_job(
            trace_id=trace_id,
            status="DONE",
            result=result,
            error=None,
        )

        # ---- AUDIT FINAL UPDATE (DONE) ----
        update_audit_log_on_completion(
            sheets_service=sheets_service,
            spreadsheet_id=SHEET_ID,
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
            row_number=audit_row_number,
            status="FAILED",
            rfqs_processed=0,
            details_json={"error": str(e)},
        )


def run_phase11_background(trace_id: str, payload: dict):
    sheets_service = get_sheets_service()

    # ---- JOB CREATED ----
    job_store.create_job(
        trace_id=trace_id,
        status="RUNNING",
        mode="async",
    )

    # ---- AUDIT ROW APPEND (INITIAL) ----
    audit_row_number = append_audit_with_alert(
        creds=None,
        sheets_service=sheets_service,
        spreadsheet_id=SHEET_ID,
        tab_name="audit_log",
        audit_row=[
            "phase11",          # PHASE
            payload,            # MODE / PAYLOAD JSON
            "RUNNING",          # STATUS
            None,               # RFQS_TOTAL
            None,               # RFQS_PROCESSED
        ],
        run_id="PHASE11",
        request_id=trace_id,
    )

    # ---- TRACE ID WRITE ----
    update_audit_log_trace_id(
        sheets_service=sheets_service,
        spreadsheet_id=SHEET_ID,
        row_number=audit_row_number,
        trace_id=trace_id,
    )

    # ---- FORCE RUNNING STATUS IN SHEET (CRITICAL FIX) ----
    sheets_service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f"audit_log!E{audit_row_number}",
        valueInputOption="RAW",
        body={"values": [["RUNNING"]]},
    ).execute()

    # ---- BACKGROUND THREAD ----
    t = threading.Thread(
        target=_run,
        args=(trace_id, payload, audit_row_number),
        daemon=True,
    )
    t.start()
