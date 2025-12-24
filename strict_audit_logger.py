import json
from datetime import datetime, date


def _json_safe(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj


def log_audit_event(event):
    safe_event = _json_safe(event)
    print(json.dumps(safe_event, ensure_ascii=False))
