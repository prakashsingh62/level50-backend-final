from core.job_store import JobStore
from core.level70_pipeline import Level70Pipeline
import traceback

job_store = JobStore()
pipeline = Level70Pipeline()


def run_phase11_background(trace_id: str, payload: dict):
    try:
        job_store.update_job(trace_id, status="RUNNING")

        result = pipeline.run(payload)

        job_store.update_job(
            trace_id,
            status="SUCCESS",
            result=result
        )

    except Exception as e:
        job_store.update_job(
            trace_id,
            status="FAILED",
            error=str(e),
            traceback=traceback.format_exc()
        )
