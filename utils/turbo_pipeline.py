# ------------------------------------------------------------
# TURBO UPGRADE 3 – Pipeline Timer + Parallel Tasks + Hooks
# ------------------------------------------------------------

import time
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=5)


# ------------------------------------------------------------
# TURBO LOGGING FUNCTION
# ------------------------------------------------------------
def turbo_event(message):
    print(f"[TURBO] {message}")


# ------------------------------------------------------------
# PARALLEL ASYNC TASK RUNNER
# ------------------------------------------------------------
def run_async(fn, *args, **kwargs):
    """
    Runs a function asynchronously.
    Does NOT affect pipeline logic.
    Used only for non-critical side tasks.
    """
    executor.submit(fn, *args, **kwargs)


# ------------------------------------------------------------
# PIPELINE TIMER CONTEXT MANAGER
# ------------------------------------------------------------
class turbo_pipeline:
    def __enter__(self):
        self.start = time.time()
        turbo_event("Pipeline START")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start
        turbo_event(f"Pipeline END  → {duration:.4f} sec")
        if exc_type:
            turbo_event(f"Pipeline ERROR: {exc_val}")
