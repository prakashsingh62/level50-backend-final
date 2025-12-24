# core/phase11_runner.py

from pipeline_engine import pipeline
from core.job_store import update_job


def run_phase11_async(payload: dict):
    trace_id = payload["trace_id"]

    try:
        # Run existing pipeline (UNCHANGED)
        pipeline(payload)

        # Mark job success
        update_job(trace_id, status="SUCCESS")

    except Exception as e:
        # Mark job failure
        update_job(trace_id, status="FAILED", error=str(e))
        raise
