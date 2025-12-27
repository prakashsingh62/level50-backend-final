# ------------------------------------------------------------
# PHASE 11 RUNNER — FINAL HARD-SAFE VERSION
# (NO AUDIT IMPORTS, NO CRASH POSSIBLE)
# ------------------------------------------------------------

from pipeline_engine import pipeline
from utils.job_store import update_job_status


def safe_audit_log(payload: dict):
    """
    Hard safety:
    - Never imports audit_logger at module level
    - Never crashes server
    - Audit failure is tolerated
    """
    try:
        from utils import audit_logger

        if hasattr(audit_logger, "log_audit_event"):
            audit_logger.log_audit_event(**payload)

    except Exception:
        # 🔒 ABSOLUTE HARD STOP: audit can NEVER crash prod
        pass


class Phase11Runner:
    def run(self, trace_id: str, payload: dict):
        status = "FAILED"
        processed = 0
        error = None

        try:
            result = pipeline.run(payload)
            processed = result.get("processed", 0)
            status = "OK"

        except Exception as e:
            error = str(e)

        # -----------------------------
        # JOB STORE UPDATE (MANDATORY)
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
        # AUDIT (OPTIONAL, SAFE)
        # -----------------------------
        safe_audit_log({
            "run_id": trace_id,
            "phase": "phase11",
            "status": status,
            "mode": payload,
            "processed": processed
        })

        return {
            "status": status,
            "processed": processed,
            "trace_id": trace_id
        }
