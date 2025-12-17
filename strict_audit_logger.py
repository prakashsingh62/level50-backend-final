# ------------------------------------------------------------
# STRICT AUDIT LOGGER — LEVEL-80 COMPATIBLE
# ------------------------------------------------------------

import json
import datetime
import threading

_AUDIT_LOCK = threading.Lock()
_AUDIT_LOG_FILE = "strict_audit.log"


def _write_log(entry: dict):
    with _AUDIT_LOCK:
        with open(_AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def write_audit(
    actor: str,
    action: str,
    entity_type: str,
    entity_id: str,
    before=None,
    after=None,
):
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "actor": actor,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "before": before,
        "after": after,
    }
    _write_log(entry)


# ------------------------------------------------------------
# 🔒 REQUIRED BY pipeline_engine.py
# ------------------------------------------------------------
def log_post_update_snapshot(
    rows_written: int,
    affected_rows: list,
    updater: str,
):
    """
    Level-80 Strict Mode post-update snapshot.
    REQUIRED function — do not remove.
    """
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "type": "POST_UPDATE_SNAPSHOT",
        "rows_written": rows_written,
        "affected_rows": affected_rows,
        "updater": updater,
    }
    _write_log(entry)
