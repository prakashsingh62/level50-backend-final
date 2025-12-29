# ------------------------------------------------------------
# PHASE 11 RUNNER — FIXED VERSION (Matches JobStore)
# ------------------------------------------------------------

from core.job_store import job_store
import threading
import time


def run_phase11_background(trace_id: str, payload: dict):
    """
    Entry point for Phase-11 background execution.
    Fixed variable names to match job_store.py logic.
    """

    mode = payload.get("mode", "production")

    # ----------------------------
    # PING MODE — HARD EXIT
    # ----------------------------
    if mode == "ping":
        # Note: Changed trace_id to job_id to match JobStore
        job_store.create_job(
            job_id=trace_id
        )
        job_store.update_job(
            job_id=trace_id,
            status="DONE",
            result={"status": "OK", "message": "Ping successful"}
        )
        return

    # ----------------------------
    # PRODUCTION MODE — ASYNC
    # ----------------------------
    job_store.create_job(
        job_id=trace_id
    )

    thread = threading.Thread(
        target=_run_phase11_pipeline,
        args=(trace_id,),
        daemon=True,
    )
    thread.start()


def _run_phase11_pipeline(trace_id: str):
    """
    Actual Phase-11 pipeline logic (simplified safe stub).
    """

    try:
        # Real pipeline logic simulation
        time.sleep(2)

        job_store.update_job(
            job_id=trace_id,
            status="DONE",
            result={"status": "OK"},
        )

    except Exception as e:
        job_store.update_job(
            job_id=trace_id,
            status="FAILED",
            error=str(e),
        )
