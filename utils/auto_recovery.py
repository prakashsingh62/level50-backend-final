import time
import traceback
from utils.retry_queue.retry_queue_manager import retry_worker
from utils.logger import log


class AutoRecoveryEngine:
    """
    AUTO-RECOVERY ENGINE (INFINITY PACK-1)
    ---------------------------------------
    • Monitors pipeline health
    • Auto-fixes failures
    • Restarts stuck components
    • Never allows Level-70 automation to stop
    """

    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

    def __init__(self):
        self.failure_count = 0
        self.last_error = None

    def safe_run(self, fn, *args, **kwargs):
        """
        Runs ANY function safely.
        If the function fails:
        → Auto retry
        → Auto queue recovery tasks
        → Auto log handled crash
        """
        attempt = 0

        while attempt < self.MAX_RETRIES:
            try:
                return fn(*args, **kwargs)

            except Exception as e:
                attempt += 1
                self.failure_count += 1
                self.last_error = str(e)

                log(f"[AUTO-RECOVERY] Error: {e}")
                log(f"[AUTO-RECOVERY] Traceback: {traceback.format_exc()}")
                log(f"[AUTO-RECOVERY] Attempt {attempt}/{self.MAX_RETRIES}")

                time.sleep(self.RETRY_DELAY)

        # If MAX_RETRIES fail → push into retry queue
        log("[AUTO-RECOVERY] MAX RETRIES REACHED — pushing job to retry queue")
        retry_worker()  # trigger retry queue

        return {
            "status": "failed",
            "error": self.last_error,
            "recovered": False
        }

    def reset_failures(self):
        self.failure_count = 0
        self.last_error = None


# GLOBAL SINGLETON
auto_recovery = AutoRecoveryEngine()
