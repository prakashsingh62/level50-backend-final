# ------------------------------------------------------------
# PHASE 11 RUNNER — FINAL HARD-SAFETY VERSION
# ENSURES AUDIT LOG IS WRITTEN AFTER ASYNC COMPLETION
# ------------------------------------------------------------

from datetime import datetime, timezone

from pipeline_engine import pipeline
from utils.audit_logger import append_audit_row
from utils.job_store import update_job_status


def _now_ist():
    # Always write IST explicitly
    return datetime.now(timezone.utc).astimezone().strftime("%d/%m/%Y %H:%M:%S")


class Phase11Runner:
    def run(self, trace_id: str, payload: dict):
        """
        This method is called INSIDE async worker.
        If this returns without writing audit → BUG.
        """

        result = None
        error = None
        processed = 0

        try:
            # -----------------------------
            # RUN PIPELINE (SYNC, SAFE)
            # -----------------------------
            result = pipeline.run(payload)
            processed = result.get("processed", 0)

            status = "OK"

        except Exception as e:
            status = "FAILED"
            error = str(e)

        # -----------------------------
        # UPDATE JOB STORE (DONE)
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
        # 🔴 HARD GUARANTEE AUDIT WRITE
        # -----------------------------
        append_audit_row({
            "TIMESTAMP_IST": _now_ist(),
            "TRACE_ID": trace_id,
            "PHASE": "phase11",
            "MODE": payload,
            "STATUS": status,
            "RFQS_TOTAL": payload.get("rfqs_total", ""),
            "RFQS_PROCESSED": processed
        })

        # -----------------------------
        # ALWAYS RETURN
        # -----------------------------
        return {
            "status": status,
            "processed": processed,
            "trace_id": trace_id
        }
