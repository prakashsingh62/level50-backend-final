from strict_audit_logger import log_audit_event
from sheet_writer import write_sheet
from sheet_reader import read_rfqs
from email_builder import send_vendor_email
from classify import classify_rfq
from utils.time_ist import ist_now

class Level70Pipeline:

    def run(self, payload: dict):
        rfqs = read_rfqs(payload)

        for rfq in rfqs:
            try:
                classify_rfq(rfq)

                if rfq.get("send_mail"):
                    send_vendor_email(rfq)

                rows = write_sheet(rfq)

                log_audit_event(
                    timestamp=ist_now(),
                    run_id="PHASE11",
                    status="OK",
                    rfq_no=rfq.get("rfq_no"),
                    uid_no=rfq.get("uid"),
                    customer=rfq.get("customer"),
                    vendor=rfq.get("vendor"),
                    step="COMPLETE",
                    rows_written=rows
                )

            except Exception as e:
                log_audit_event(
                    timestamp=ist_now(),
                    run_id="PHASE11",
                    status="ERROR",
                    rfq_no=rfq.get("rfq_no"),
                    uid_no=rfq.get("uid"),
                    customer=rfq.get("customer"),
                    vendor=rfq.get("vendor"),
                    step="PIPELINE",
                    error_type="SYSTEM",
                    error_message=str(e)
                )
                raise

        return {"status": "OK", "processed": len(rfqs)}

pipeline = Level70Pipeline()

def apply_approved_update(row, ai_output):
    return {"status": "SKIPPED"}
