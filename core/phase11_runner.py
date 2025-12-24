from typing import Dict
from core.level70_pipeline import pipeline
import traceback

# SIMPLE IN-MEMORY STORE
JOB_STORE: Dict[str, Dict] = {}

def run_phase11_background(trace_id: str):
    job = JOB_STORE.get(trace_id)

    if not job:
        return

    payload = job.get("payload", {})

    try:
        result = pipeline.run(payload)

        job["status"] = "DONE"
        job["processed"] = result.get("processed", 0)
    except Exception as e:
        job["status"] = "FAILED"
        job["error"] = str(e)
        job["traceback"] = traceback.format_exc()
