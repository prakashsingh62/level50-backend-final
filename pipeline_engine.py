from strict_audit_logger import log_audit_event
from sheet_writer import write_to_sheet
from sheet_reader import read_rfqs
from email_builder import send_vendor_email
from classify import classify_rfq
from logger import get_ist_now   # ✅ FIX: existing, stable IST helper


def run_pipeline():
    """
    Core Level-80 pipeline
    RFQ-by-RFQ execution with HARD audit trace
    """

    rfqs = read_rfqs()

    for rfq in rfqs:
        try:
            # -------------------------------
            # STEP 1: CLASSIFICATION
            # -------------------------------
            classify_rfq(rfq)

            # -------------------------------
            # STEP 2: SEND MAIL (if required)
            # -------------------------------
            if rfq.get("send_mail"):
                send_vendor_email(rfq)

            # -------------------------------
            # STEP 3: WRITE TO SHEET
            # -------------------------------
            rows_written = write_to_sheet(rfq)

            # -------------------------------
            # SUCCESS AUDIT (RFQ-LEVEL TRACE)
            # -------------------------------
            log_audit_event(
                timestamp=get_ist_now(),
                run_id="POST_UPDATE",
                status="OK",
                remarks="OK",
                rows_written=rows_written,

                rfq_no=rfq.get("rfq_no"),
                uid_no=rfq.get("uid"),
                customer=rfq.get("customer"),
                vendor=rfq.get("vendor"),
                step="COMPLETE"
            )

        except Exception as e:
            # -------------------------------
            # FAILURE — RFQ-LEVEL TRACE
            # -------------------------------
            log_audit_event(
                timestamp=get_ist_now(),
                run_id="POST_UPDATE",
                status="ERROR",
                error_type="SYSTEM",
                error_message=str(e),

                rfq_no=rfq.get("rfq_no"),
                uid_no=rfq.get("uid"),
                customer=rfq.get("customer"),
                vendor=rfq.get("vendor"),
                step="PIPELINE"
            )

    return {"status": "completed"}
