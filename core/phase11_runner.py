from core.audit_bus import emit_audit
from core.contracts import AuditEvent
from utils.time_ist import ist_now
from utils.json_safe import json_safe
import uuid

def run_phase11(payload: dict):
    normalized = payload
    result = pipeline.run(normalized)

    # 🔥 CRITICAL FIX — sanitize datetime
    return json_safe(result)
    source = payload.get("source")

    # ✅ SAFE SHORT-CIRCUIT
    if source == "manual-test":
        now = ist_now()

        event = AuditEvent(
            trace_id=str(uuid.uuid4()),
            stage="PHASE-11-MANUAL-TEST",
            timestamp=now,          # datetime OK for Sheets
            payload=payload,
        )

        emit_audit(event)

        # ⚠️ API RESPONSE MUST BE JSON SAFE
        return {
            "status": "OK",
            "mode": "LEVEL-80",
            "audit": "LOGGED",
            "safe_mode": True,
            "timestamp": now.isoformat()   # ✅ FIX
        }

    # REAL PIPELINE (unchanged)
    from pipeline_engine import pipeline
    return pipeline.run(payload)
