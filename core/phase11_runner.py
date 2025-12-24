# core/phase11_runner.py

import uuid

from core.level70_pipeline import pipeline
from core.run_audit_logger import (
    log_run_start,
    log_run_success,
    log_run_failure,
)


def run_phase11(payload: dict):
    trace_id = str(uuid.uuid4())
    mode = payload.get("mode", "production")
    phase = "PHASE11"

    log_run_start(
        trace_id=trace_id,
        phase=phase,
        mode=mode,
    )

    try:
        result = pipeline.run(payload)

        rfqs_processed = result.get("processed", 0)
        rfqs_total = rfqs_processed  # phase-14 has no per-RFQ visibility yet

        log_run_success(
            trace_id=trace_id,
            phase=phase,
            mode=mode,
            rfqs_total=rfqs_total,
            rfqs_processed=rfqs_processed,
        )

        return {
            "trace_id": trace_id,
            "status": "SUCCESS",
            "result": result,
        }

    except Exception as e:
        log_run_failure(
            trace_id=trace_id,
            phase=phase,
            mode=mode,
            error=e,
        )
        raise
