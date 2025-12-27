# ------------------------------------------------------------
# PHASE 11 RUNNER — FINAL SAFE VERSION (NO CRASH)
# ------------------------------------------------------------

from datetime import datetime, timezone

from pipeline_engine import pipeline
from utils.audit_logger import log_audit_event
from utils.job_store import update_job_status


def _now_ist():
    return datetime.now(timezone.utc).astimezone().strftime("%d/%m/%Y %H:%M:%S")


class Phase11Runner:
    def run(self, trace_id: str, payload: dict):
        result = None
        error = None
        processed = 0
        status = "FAILED"

        try:
            result = pipeline.run(payload)
            processed = result.get("processed", 0)
            status = "OK"

        except Exception as e:
            error = str(e)

        # -----------------------------
        # UPDATE JOB STATUS (DONE)
        # -----------------------------
        update_job_status(
            trace_id=trace_id,
            status="DONE",
            result={
                "status": status,
                "processed": processed
            },
            error=error
        )

        # -----------------------------
        # 🔒 GUARANTEED AUDIT LOG
        # -----------------------------
        log_audit_event(
            run_id=trace_id,
            phase="phase11",
            status=status,
            mode=payload,
            processed=processed,
            timestamp_ist=_now_ist()
        )

        return {
            "status": status,
            "processed": processed,
            "trace_id": trace_id
        }
