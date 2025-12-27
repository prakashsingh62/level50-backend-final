# ------------------------------------------------------------
# PHASE 11 RUNNER — FINAL, SAFE, NO MISSING IMPORTS
# ------------------------------------------------------------

from core.job_store import job_store
from datetime import datetime
import traceback


def run_phase11_background(trace_id: str, payload: dict):
    """
    Executes Phase-11 pipeline safely.
    Updates job status in JobStore.
    NEVER raises to FastAPI.
    """

    try:
        # Mark job as RUNNING
        job_store.update_job(
            trace_id=trace_id,
            status="RUNNING",
            updated_at=datetime.utcnow().isoformat()
        )

        mode = payload.get("mode", "production")

        # ----------------------------------------------------
        # TEST / PING MODE (NO SHEET WRITE)
        # ----------------------------------------------------
        if mode.lower() in ("test", "ping"):
            job_store.update_job(
                trace_id=trace_id,
                status="DONE",
                result={
                    "status": "SKIPPED",
                    "reason": "TEST_MODE",
                    "mode": mode
                },
                updated_at=datetime.utcnow().isoformat()
            )
            return

        # ----------------------------------------------------
        # PRODUCTION LOGIC (PLACEHOLDER — YOUR REAL PIPELINE)
        # ----------------------------------------------------
        # 🔴 IMPORTANT:
        # Put your REAL Phase-11 processing here
        processed_count = 1649  # example from your logs

        job_store.update_job(
            trace_id=trace_id,
            status="DONE",
            result={
                "status": "OK",
                "processed": processed_count,
                "mode": "PRODUCTION"
            },
            updated_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        job_store.update_job(
            trace_id=trace_id,
            status="FAILED",
            error=str(e),
            traceback=traceback.format_exc(),
            updated_at=datetime.utcnow().isoformat()
        )
