# =========================================
# strict_audit_logger.py
# Level-80 Audit Trail (Append-Only)
# =========================================

import json
import os
import datetime

AUDIT_LOG_FILE = "level_80_audit_log.jsonl"


def _now_ist():
    return (datetime.datetime.utcnow() +
            datetime.timedelta(hours=5, minutes=30)) \
        .strftime("%d/%m/%Y %H:%M:%S IST")


def write_audit(event_type: str, payload: dict):
    record = {
        "timestamp": _now_ist(),
        "event": event_type,
        "payload": payload
    }

    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
