from core.audit_bus import emit_audit
from core.contracts import AuditEvent
from utils.json_safe import json_safe
from utils.time_ist import ist_now
import uuid

from pipeline_engine import pipeline

def run_phase11(payload):
    # 1️⃣ Run pipeline
    result = pipeline.run(payload)

    # 2️⃣ Emit audit (no datetime leakage)
    emit_audit(
        AuditEvent(
            event_id=str(uuid.uuid4()),
            phase="11",
            source=payload.get("source"),
            created_at=ist_now()
        )
    )

    # 3️⃣ SINGLE, SAFE RETURN (THIS IS THE FIX)
    return json_safe({
        "status": "SUCCESS",
        "phase": "11",
        "result": result
    })
