def log_audit_event(
    timestamp,
    run_id,
    status,
    remarks="",
    error_type="",
    error_message="",
    retry_count="",
    updater="",
    rows_written=None,

    # 🔥 RFQ TRACE (OPTIONAL)
    rfq_no=None,
    uid_no=None,
    customer=None,
    vendor=None,
    step=None
):
    record = {
        "timestamp": timestamp,
        "run_id": run_id,
        "status": status,
        "remarks": remarks,
        "error_type": error_type,
        "error_message": error_message,
        "retry_count": retry_count,
        "updater": updater,
        "rows_written": rows_written or [],

        # 🔍 RFQ CONTEXT
        "rfq_no": rfq_no,
        "uid_no": uid_no,
        "customer": customer,
        "vendor": vendor,
        "step": step,
    }

    from logger import write_audit_log
    write_audit_log(record)
