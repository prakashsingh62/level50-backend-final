from typing import Dict

# In-memory job store (simple + safe)
JOB_STATUS: Dict[str, dict] = {}


def create_job(trace_id: str):
    JOB_STATUS[trace_id] = {
        "status": "QUEUED",
        "processed": 0
    }


def update_job(trace_id: str, **kwargs):
    if trace_id not in JOB_STATUS:
        return
    JOB_STATUS[trace_id].update(kwargs)


def get_job(trace_id: str):
    return JOB_STATUS.get(trace_id)
