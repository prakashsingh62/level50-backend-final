import os
import json
from datetime import datetime, date
from core.contracts import AuditEvent
from logger import get_logger
from utils.sheet_updater import write_audit_row

log = get_logger(__name__)


def _json_safe(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj


def emit_audit(event: AuditEvent):
    payload = {
        "trace_id": event.trace_id,
        "stage": event.stage,
        "timestamp": event.timestamp,   # already string
        "payload": _json_safe(event.payload),  # 🔴 FIX HERE
    }

    log.info(payload)

    write_audit_row(
        spreadsheet_id=os.environ["AUDIT_SHEET_ID"],
        tab_name=os.environ["AUDIT_TAB"],
        audit_row=[
            payload["trace_id"],
            payload["stage"],
            payload["timestamp"],
            json.dumps(payload["payload"], ensure_ascii=False),
        ],
    )
