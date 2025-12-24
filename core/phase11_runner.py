# core/phase11_runner.py

import traceback

from core.level70_pipeline import pipeline
from core.run_audit_logger import (
    log_run_start,
    log_run_success,
    log_run_failure,
)
from core.job_store import update_job_status


def run_phase11_background(trace_id: str, mode: str):
    phase = "PHASE11"

    try:
        log_run_start(trace_id, phase, mode)
        update_job_status(trace_id, "RUNNING")

        result = pipeline.run({"mode": mode})
        processed = result.get("processed", 0)

        log_run_success(trace_id, phase, mode, processed)
        update_job_status(trace_id, "SUCCESS", result=result)

    except Exception as e:
        log_run_failure(trace_id, phase, mode, e)
        update_job_status(
            trace_id,
            "FAILED",
            error=str(e),
            traceback=traceback.format_exc(),
        )
