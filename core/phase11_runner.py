from core.audit_bus import emit_audit
from core.contracts import AuditEvent, TraceContext
from utils.json_safe import json_safe
from pipeline_engine import pipeline


def run_phase11(payload: dict | None):
    payload = payload or {}
    trace = TraceContext.create()

    is_test = payload.get("test") is True

    # 🔐 PROD SAFETY GUARD
    if not is_test:
        rfq_no = payload.get("rfq_no")
        customer = payload.get("customer")

        if not rfq_no or not customer:
            return json_safe({
                "status": "REJECTED",
                "reason": "Missing rfq_no or customer",
                "mode": "PRODUCTION_GUARD",
                "trace_id": trace.trace_id
            })

        if rfq_no.upper().startswith(("TEST", "DUMMY", "SAMPLE")):
            return json_safe({
                "status": "REJECTED",
                "reason": "Test RFQ blocked in production",
                "mode": "PRODUCTION_GUARD",
                "trace_id": trace.trace_id
            })

        # ✅ SAFE TO EXECUTE REAL PIPELINE
        result = pipeline.run(payload)
        mode = "PRODUCTION"

    else:
        result = {"status": "SKIPPED", "reason": "TEST_MODE"}
        mode = "TEST"

    emit_audit(
        AuditEvent(
            trace_id=trace.trace_id,
            stage="phase11",
            payload={"input": payload, "result": result, "mode": mode},
            timestamp=trace.timestamp
        )
    )

    return json_safe({
        "status": "SUCCESS",
        "phase": "11",
        "mode": mode,
        "trace_id": trace.trace_id,
        "result": result
    })
