from core.contracts import TraceContext, PipelineResult, AuditEvent
from core.audit_bus import emit_audit
from pipeline_engine import Level70Pipeline

pipeline = Level70Pipeline()

def run_phase11(payload: dict) -> PipelineResult:
    ctx = TraceContext.create()

    emit_audit(AuditEvent(
        trace_id=ctx.trace_id,
        stage="PHASE11_START",
        payload=payload,
        timestamp=ctx.timestamp
    ))

    # 🔥 NORMALIZE EMAIL → PIPELINE PAYLOAD
    email = payload.get("email", {})

    normalized = {
        "rfq_no": email.get("rfq_no"),
        "uid": email.get("uid"),
        "customer": email.get("customer", ""),
        "vendor": email.get("vendor", ""),
        "source": payload.get("source", "phase11"),
        "trigger": payload.get("trigger", "manual")
    }

    result = pipeline.run(normalized)

    emit_audit(AuditEvent(
        trace_id=ctx.trace_id,
        stage="PHASE11_END",
        payload=result,
        timestamp=ctx.timestamp
    ))

    return PipelineResult(
        status="ok",
        trace_id=ctx.trace_id,
        data=result
    )
