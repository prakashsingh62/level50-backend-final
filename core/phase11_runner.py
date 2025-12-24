from core.audit_bus import emit_audit
from core.contracts import AuditEvent, TraceContext
from utils.json_safe import json_safe
from utils.time_ist import ist_now

from pipeline_engine import pipeline


def run_phase11(payload):
    # 1️⃣ run pipeline
    result = pipeline.run(payload)

    # 2️⃣ create trace (as per contract)
    trace = TraceContext.create()

    # 3️⃣ emit audit (MATCHES CONTRACT EXACTLY)
    emit_audit(
        AuditEvent(
            trace_id=trace.trace_id,
            stage="phase11",
            payload={
                "input": payload,
                "result_status": result.get("status") if isinstance(result, dict) else "OK"
            },
            timestamp=trace.timestamp
        )
    )

    # 4️⃣ single safe return
    return json_safe({
        "status": "SUCCESS",
        "phase": "11",
        "trace_id": trace.trace_id,
        "result": result
    })
