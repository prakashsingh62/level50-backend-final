# ------------------------------------------------------------
# PHASE 11 RUNNER — FINAL (SAFE, NO CRASH)
# ------------------------------------------------------------

from core.job_store import job_store
import threading
import time


def run_phase11_background(trace_id: str, payload: dict):
    """
    Runs Phase-11 logic in background thread.
    """

    # create job
    job_store.create_job(trace_id, {
        "status": "RUNNING",
        "mode": payload.get("mode"),
        "result": None,
        "error": None,
    })

    def runner():
        try:
            # ---- SIMULATED PHASE 11 WORK ----
            time.sleep(2)  # simulate processing

            # mark done
            job_store.update_job(trace_id, {
                "status": "DONE",
                "result": {
                    "message": "Phase 11 completed successfully"
                }
            })

        except Exception as e:
            job_store.update_job(trace_id, {
                "status": "FAILED",
                "error": str(e)
            })

    threading.Thread(target=runner, daemon=True).start()
