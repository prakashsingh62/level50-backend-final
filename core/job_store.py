import threading
from datetime import datetime

_lock = threading.Lock()
_jobs = {}


class JobStore:
    def create_job(self, trace_id: str, status: str, mode: str):
        with _lock:
            _jobs[trace_id] = {
                "trace_id": trace_id,
                "status": status,
                "mode": mode,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "result": None,
                "error": None,
            }

    def update_job(self, trace_id: str, **fields):
        with _lock:
            if trace_id not in _jobs:
                return
            _jobs[trace_id].update(fields)
            _jobs[trace_id]["updated_at"] = datetime.utcnow().isoformat()

    def get_job(self, trace_id: str):
        with _lock:
            return _jobs.get(trace_id)
