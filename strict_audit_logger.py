# strict_audit_logger.py
import json
from utils.time_ist import ist_now

def log_audit_event(**event):
    ts = ist_now()

    # 🔒 FORCE SAFE STRING
    event["timestamp"] = ts.isoformat()

    # Railway-safe log
    print(json.dumps(event, ensure_ascii=False))

    return True
