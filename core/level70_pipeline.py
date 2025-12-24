from sheet_reader import read_rfqs
from sheet_writer import write_sheet
from strict_audit_logger import log_audit_event
from classify import classify_rfq
from core.contracts import AuditEvent
from datetime import datetime


class Level70Pipeline:
    def run(self, payload=None):
        trace_id = payload.get("trace_id") if payload else None

        rfqs = read_rfqs(payload)

        for rfq in rfqs:
            classify_rfq(rfq)
            rows = write_sheet(rfq)

            event = AuditEvent(
                trace_id=trace_id,
                stage="PHASE11_COMPLETE",
                timestamp=datetime.utcnow().isoformat(),
                payload={
                    "rfq_no": rfq.get("rfq_no"),
                    "uid_no": rfq.get("uid"),
                    "customer": rfq.get("customer"),
                    "vendor": rfq.get("vendor"),
                    "rows_written": rows,
                },
            )

            log_audit_event(event)

        return {
            "status": "OK",
            "processed": len(rfqs),
        }


pipeline = Level70Pipeline()
