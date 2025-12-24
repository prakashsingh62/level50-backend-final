import threading
from datetime import datetime, timezone
from typing import Optional, Dict, Any

_lock = threading.Lock()
_jobs: Dict[str, Dict[str, Any]] = {}


def _now_iso() -> str:
    # timezone-aware, stable
    return datetime.now(timezone.utc).isoformat()


class JobStore:
    def create_job(self, trace_id: str, status: str, mode: str) -> None:
        with _lock:
            _jobs[trace_id] = {
                "trace_id": trace_id,
                "status": status,
                "mode": mode,
                "created_at": _now_iso(),
                "updated_at": _now_iso(),
                "result": None,
                "error": None,
            }

    def update_job(self, trace_id: str, **fields) -> None:
        with _lock:
            job = _jobs.get(trace_id)
            if not job:
                return
            job.update(fields)
            job["updated_at"] = _now_iso()

    def get_job(self, trace_id: str) -> Optional[Dict[str, Any]]:
        with _lock:
            job = _jobs.get(trace_id)
            return dict(job) if job else None


# single shared instance (import-safe)
job_store = JobStore()
