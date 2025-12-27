# core/phase11_runner.py

import uuid
import threading
from utils.job_store import create_job, update_job_status

def _run_phase11(trace_id: str, payload: dict):
    try:
        # mark running
        update_job_status(trace_id, status="RUNNING")

        # >>> YOUR EXISTING PHASE-11 LOGIC HERE <<<
        # do NOT change business logic
        result = run_phase11_internal(payload)

        update_job_status(
            trace_id,
            status="DONE",
            result=result
        )
    except Exception as e:
        update_job_status(
            trace_id,
            status="FAILED",
            error=str(e)
        )

def run_phase11_background(payload: dict) -> str:
    trace_id = str(uuid.uuid4())

    create_job(
        trace_id=trace_id,
        status="QUEUED",
        mode=payload.get("mode"),
        source=payload.get("source")
    )

    t = threading.Thread(
        target=_run_phase11,
        args=(trace_id, payload),
        daemon=True
    )
    t.start()

    return trace_id
