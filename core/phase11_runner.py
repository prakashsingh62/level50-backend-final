# core/phase11_runner.py

from pipeline_engine import pipeline
from core.job_store import create_job, update_job


def run_phase11_async(payload: dict):
    trace_id = payload["trace_id"]

    # Create job entry
    create_job(trace_id)

    try:
        # Run existing pipeline (UNCHANGED)
        pipeline(payload)

        # Mark job success
        update_job(trace_id, "SUCCESS")

    except Exception as e:
        # Mark job failure
        update_job(trace_id, "FAILED", error=str(e))
        raise
