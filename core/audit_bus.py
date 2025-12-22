# core/audit_bus.py
import os
from core.contracts import AuditEvent
from logger import get_logger
from utils.sheet_updater import write_audit_row

log = get_logger(__name__)

def emit_audit(event: AuditEvent):
    payload = {
        "trace_id": event.trace_id,
        "stage": event.stage,
        "timestamp": event.timestamp,
        "payload": event.payload,
    }

    # 1️⃣ Console log
    log.info(payload)

    # 2️⃣ ✅ WRITE TO GOOGLE SHEET
    write_audit_row(
    spreadsheet_id=os.environ["AUDIT_SHEET_ID"],
    tab_name=os.environ["AUDIT_TAB"],
    audit_row=[
        payload["trace_id"],
        payload["stage"],
        payload["timestamp"],
        json.dumps(payload["payload"])
    ]
)

