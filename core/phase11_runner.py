# ------------------------------------------------------------
# PHASE 11 RUNNER — FINAL SAFE VERSION
# ------------------------------------------------------------

from core.job_store import job_store
import threading
import time


def run_phase11_background(trace_id: str, payload: dict):
    """
    Entry point for Phase-11 background execution.
    Handles PING safely.
    """

    mode = payload.get("mode", "production")

    # ----------------------------
    # PING MODE — HARD EXIT
    # ----------------------------
    if mode == "ping":
        job_store.create_job(
            trace_id=trace_id,
            status="DONE",
            mode="ping",
            result={"status": "OK", "message": "Ping successful"},
        )
        return

    # ----------------------------
    # PRODUCTION MODE — ASYNC
    # ----------------------------
    job_store.create_job(
        trace_id=trace_id,
        status="RUNNING",
        mode="production",
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
        # 🔴 PLACEHOLDER: real pipeline yahan aayega
        time.sleep(2)

        job_store.update_job(
            trace_id=trace_id,
            status="DONE",
            result={"status": "OK"},
        )

    except Exception as e:
        job_store.update_job(
            trace_id=trace_id,
            status="FAILED",
            error=str(e),
        )
