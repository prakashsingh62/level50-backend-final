from sheet_reader import read_rfqs
from classify import classify_rfq
from sheet_writer import write_sheet
from strict_audit_logger import log_audit_event


class Level70Pipeline:
    def run(self, payload=None):
        payload = payload or {}

        # 🔹 Ping mode (health / monitoring)
        if payload.get("mode") == "ping":
            return {
                "status": "OK",
                "mode": "PING",
                "message": "Pipeline reachable"
            }

        # 🔹 Read RFQs (ALWAYS normalize to list)
        rfqs = read_rfqs(payload)

        if not rfqs:
            return {
                "status": "NO_OP",
                "processed": 0,
                "reason": "No RFQs resolved from payload"
            }

        if isinstance(rfqs, dict):
            rfqs = [rfqs]

        processed = 0

        for rfq in rfqs:
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

        return {
            "status": "OK",
            "processed": processed
        }


# 🔴 REQUIRED: pipeline singleton
pipeline = Level70Pipeline()
