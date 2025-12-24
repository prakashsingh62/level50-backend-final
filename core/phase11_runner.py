from core.pipeline_engine import pipeline
from core.job_store import create_job, update_job


def run_phase11_async(payload: dict):
    trace_id = payload["trace_id"]

    # Create job
    create_job(trace_id)

    try:
        update_job(trace_id, status="RUNNING")

        result = pipeline.run(payload)

        update_job(
            trace_id,
            status="DONE",
            processed=result.get("processed", 0)
        )

    except Exception as e:
        update_job(
            trace_id,
            status="FAILED",
            error=str(e)
        )
