import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional

_lock = threading.Lock()
_jobs: Dict[str, Dict[str, Any]] = {}


def _now():
    return datetime.now(timezone.utc).isoformat()


class JobStore:
    def create_job(self, trace_id: str, status: str, mode: str):
        with _lock:
            _jobs[trace_id] = {
                "trace_id": trace_id,
                "status": status,
                "mode": mode,
                "created_at": _now(),
                "updated_at": _now(),
                "result": None,
                "error": None,
            }

    def update_job(self, trace_id: str, **fields):
        with _lock:
            job = _jobs.get(trace_id)
            if not job:
                return
            job.update(fields)
            job["updated_at"] = _now()

    def get_job(self, trace_id: str) -> Optional[Dict[str, Any]]:
        with _lock:
            job = _jobs.get(trace_id)
            return dict(job) if job else None


# 🔒 SINGLETON (IMPORTANT)
job_store = JobStore()


# ✅ FUNCTION EXPORTS (FOR OLD IMPORTS)
def create_job(trace_id: str, status: str, mode: str):
    job_store.create_job(trace_id, status, mode)


def update_job(trace_id: str, **fields):
    job_store.update_job(trace_id, **fields)


def get_job(trace_id: str):
    return job_store.get_job(trace_id)
