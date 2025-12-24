# ------------------------------------------------------------
# PHASE 11 RUNNER (FINAL, STABLE)
# ------------------------------------------------------------
# Exports: run_phase11_background
# ------------------------------------------------------------

import threading
from core.job_store import job_store
from core.pipeline import pipeline  # apna actual pipeline import

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

def run_phase11_background(trace_id: str, payload: dict):
    """
    Public API — DO NOT RENAME.
    Used by main_server.py
    """
    job_store.create_job(
        trace_id=trace_id,
        status="RUNNING",
        mode="async"
    )

    t = threading.Thread(
        target=_run,
        args=(trace_id, payload),
        daemon=True
    )
    t.start()
