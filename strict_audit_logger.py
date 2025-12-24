import json
from datetime import datetime, date
from dataclasses import asdict


def _json_safe(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj


def log_audit_event(event=None, **kwargs):
    """
    Supports BOTH:
    - log_audit_event(event=AuditEvent)
    - log_audit_event(run_id=..., status=..., ...)
    """

    if event is not None:
        # dataclass → dict
        if hasattr(event, "__dataclass_fields__"):
            event = asdict(event)
        data = event
    else:
        # kwargs path (pipeline_engine)
        data = kwargs

    safe_data = _json_safe(data)
    print(json.dumps(safe_data, ensure_ascii=False))
