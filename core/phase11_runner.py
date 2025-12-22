from core.audit_bus import emit_audit
from core.contracts import AuditEvent
from utils.time_ist import ist_now
import uuid

def run_phase11(payload: dict):
    """
    TEMP SAFE MODE:
    - If manual-test → only audit
    - Skip RFQ pipeline completely
    """

    source = payload.get("source")

    # ✅ SAFE SHORT-CIRCUIT FOR AUDIT TEST
    if source == "manual-test":
        event = AuditEvent(
            trace_id=str(uuid.uuid4()),
            stage="PHASE-11-MANUAL-TEST",
            timestamp=ist_now(),
            payload=payload,
        )

        emit_audit(event)

        return {
            "status": "OK",
            "mode": "LEVEL-80",
            "audit": "LOGGED",
            "safe_mode": True
        }

    # ❌ REAL PIPELINE (unchanged)
    from pipeline_engine import pipeline
    return pipeline.run(payload)
