import os
from datetime import datetime

AUTOMATION_ENABLED = os.getenv("AUTOMATION_ENABLED", "false").lower() == "true"
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"


def guard_or_skip(action: str, payload: dict | None = None):
    """
    Central safety gate for ALL side-effects
    """
    timestamp = datetime.now().isoformat()

    if not AUTOMATION_ENABLED:
        return {
            "skipped": True,
            "reason": "AUTOMATION_DISABLED",
            "action": action,
            "payload": payload,
            "time": timestamp,
        }

    if DRY_RUN:
        return {
            "skipped": True,
            "reason": "DRY_RUN",
            "action": action,
            "payload": payload,
            "time": timestamp,
        }

    return {"skipped": False}
