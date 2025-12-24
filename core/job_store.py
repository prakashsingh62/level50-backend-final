# core/job_store.py
from typing import Dict

JOB_STATUS: Dict[str, dict] = {}

def create_job(trace_id: str):
    JOB_STATUS[trace_id] = {
        "status": "QUEUED",
        "processed": 0,
        "total": 0
    }

def update_job(trace_id: str, **kwargs):
    JOB_STATUS[trace_id].update(kwargs)

def get_job(trace_id: str):
    return JOB_STATUS.get(trace_id)

