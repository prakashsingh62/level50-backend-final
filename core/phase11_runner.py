from core.audit_bus import emit_audit
from core.contracts import AuditEvent, TraceContext
from utils.json_safe import json_safe
from pipeline_engine import pipeline


def run_phase11(payload: dict | None):
    payload = payload or {}
    trace = TraceContext.create()

    # 🔐 Test guard (future-proof, explicit)
    is_test = payload.get("test") is True

    if is_test:
        result = {
            "status": "SKIPPED",
            "reason": "TEST_MODE"
        }
    else:
        # ✅ REAL PRODUCTION EXECUTION
        result = pipeline.run(payload)

    # ✅ Audit always emitted (prod-safe)
    emit_audit(
        AuditEvent(
            trace_id=trace.trace_id,
            stage="phase11",
            payload={
                "input": payload,
                "result": result,
                "mode": "TEST" if is_test else "PRODUCTION"
            },
            timestamp=trace.timestamp
        )
    )

    # ✅ Single safe return
    return json_safe({
        "status": "SUCCESS",
        "phase": "11",
        "trace_id": trace.trace_id,
        "mode": "TEST" if is_test else "PRODUCTION",
        "result": result
    })
