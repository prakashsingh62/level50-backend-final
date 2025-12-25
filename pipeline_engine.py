# ------------------------------------------------------------
# PIPELINE ENGINE — LEVEL 70 / PHASE 11
# FINAL, HANG-PROOF, PROD-SAFE
# ------------------------------------------------------------

from sheet_reader import read_rfqs
from classify import classify_rfq
from sheet_writer import write_sheet
from strict_audit_logger import log_audit_event


class Level70Pipeline:
    def run(self, payload=None):
        payload = payload or {}

        # --------------------------------------------------
        # PING / HEALTH MODE
        # --------------------------------------------------
        if payload.get("mode") == "ping":
            return {
                "status": "OK",
                "mode": "PING",
                "message": "Pipeline reachable"
            }

        # --------------------------------------------------
        # READ RFQs (FAIL-SAFE, NO HANG)
        # --------------------------------------------------
        try:
            rfqs = read_rfqs(payload)
        except Exception as e:
            # 🔴 CRITICAL: NEVER HANG HERE
            return {
                "status": "FAILED",
                "processed": 0,
                "error": f"read_rfqs_failed: {str(e)}"
            }

        if not rfqs:
            return {
                "status": "NO_OP",
                "processed": 0,
                "reason": "No RFQs resolved from payload"
            }

        if isinstance(rfqs, dict):
            rfqs = [rfqs]

        # --------------------------------------------------
        # PROCESS RFQs
        # --------------------------------------------------
        processed = 0

        for rfq in rfqs:
            try:
                classify_rfq(rfq)

                rows = write_sheet(rfq)

                log_audit_event(
                    run_id="PHASE11",
                    status="OK",
                    rfq_no=rfq.get("rfq_no"),
                    uid_no=rfq.get("uid"),
                    customer=rfq.get("customer"),
                    vendor=rfq.get("vendor"),
                    step="COMPLETE",
                    rows_written=rows
                )

                processed += 1

            except Exception as e:
                # 🔴 ONE RFQ FAIL SHOULD NOT HANG PIPELINE
                log_audit_event(
                    run_id="PHASE11",
                    status="FAILED",
                    rfq_no=rfq.get("rfq_no"),
                    uid_no=rfq.get("uid"),
                    customer=rfq.get("customer"),
                    vendor=rfq.get("vendor"),
                    step="ERROR",
                    rows_written=0
                )

        # --------------------------------------------------
        # FINAL RETURN (ALWAYS REACHED)
        # --------------------------------------------------
        return {
            "status": "OK",
            "processed": processed
        }


# ------------------------------------------------------------
# REQUIRED PIPELINE SINGLETON
# ------------------------------------------------------------
pipeline = Level70Pipeline()
