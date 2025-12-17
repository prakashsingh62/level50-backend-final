# core/audit_bus.py

from core.contracts import AuditEvent
from logger import get_logger
from datetime import datetime

log = get_logger(__name__)

def emit_audit(event: AuditEvent):
    log.info({
        "trace_id": event.trace_id,
        "stage": event.stage,
        "timestamp": event.timestamp,
        "payload": event.payload
    })
