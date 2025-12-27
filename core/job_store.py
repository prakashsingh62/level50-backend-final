# ------------------------------------------------------------
# JOB STORE — IN-MEMORY
# ------------------------------------------------------------

class JobStore:
    def __init__(self):
        self._jobs = {}

    def create_job(self, trace_id, data):
        self._jobs[trace_id] = data

    def update_job(self, trace_id, updates):
        if trace_id in self._jobs:
            self._jobs[trace_id].update(updates)

    def get_job(self, trace_id):
        return self._jobs.get(trace_id)


job_store = JobStore()
