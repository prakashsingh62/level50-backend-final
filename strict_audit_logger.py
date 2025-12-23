# strict_audit_logger.py
import json
from utils.time_ist import ist_now

def log_audit_event(**event):
    event["timestamp"] = ist_now().isoformat()  # ← KEY FIX
    print(json.dumps(event, ensure_ascii=False))
    return True
