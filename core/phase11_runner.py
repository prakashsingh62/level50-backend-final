# core/phase11_runner.py

import threading
import uuid

from core.level70_pipeline import pipeline
from core.job_store import create_job, update_job_status
from core.run_audit_logger import (
    log_run_start,
    log_run_success,
    log_run_failure,
)


def run_phase11_background(payload: dict):
    trace_id = str(uuid.uuid4())
    mode = payload.get("mode", "production")

    create_job(trace_id, mode)

    def _runner():
        try:
            log_run_start(trace_id, "PHASE11", mode)

            result = pipeline.run(payload)

            log_run_success(
                trace_id=trace_id,
                phase="PHASE11",
                mode=mode,
                rfqs_total=result.get("processed", 0),
                rfqs_processed=result.get("processed", 0),
            )

            update_job_status(trace_id, "SUCCESS", result)

        except Exception as e:
            log_run_failure(trace_id, "PHASE11", mode, e)
            update_job_status(trace_id, "FAILED", {"error": str(e)})

    threading.Thread(target=_runner, daemon=True).start()

    return {
        "status": "ACCEPTED",
        "trace_id": trace_id,
    }
