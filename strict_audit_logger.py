# strict_audit_logger.py
import json
import os
from utils.time_ist import ist_now

def log_audit_event(**event):
    event["timestamp"] = ist_now()

    # OPTIONAL: write to sheet / db / file later
    # For now just print to logs (Railway-safe)
    print(json.dumps(event, ensure_ascii=False))

    return True
