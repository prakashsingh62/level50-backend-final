from sheet_reader import read_rfqs
from sheet_writer import write_sheet
from strict_audit_logger import log_audit_event
from classify import classify_rfq

class Level70Pipeline:
    def run(self, payload=None):
        rfqs = read_rfqs(payload)

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
                rows_written=rows,
            )

        return {"status": "OK", "processed": len(rfqs)}

pipeline = Level70Pipeline()
