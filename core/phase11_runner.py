# core/phase11_runner.py

from core.contracts import TraceContext, PipelineResult, AuditEvent
from core.audit_bus import emit_audit
from pipeline_engine import Level70Pipeline


pipeline = Level70Pipeline()


def run_phase11(email_payload: dict) -> PipelineResult:
    ctx = TraceContext.create()

    emit_audit(AuditEvent(
        trace_id=ctx.trace_id,
        stage="PIPELINE_START",
        payload=email_payload,
        timestamp=ctx.timestamp
    ))

    result = pipeline.run(email_payload)

    emit_audit(AuditEvent(
        trace_id=ctx.trace_id,
        stage="PIPELINE_END",
        payload=result,
        timestamp=ctx.timestamp
    ))

    return PipelineResult(
        status=result.get("status"),
        trace_id=ctx.trace_id,
        data=result
    )
