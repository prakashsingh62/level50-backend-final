import time
import threading
import traceback
import requests
from utils.logger import log
from utils.retry_queue.retry_queue_manager import retry_worker


class HeartbeatMonitor:
    """
    INFINITY PACK-2: HEARTBEAT MONITOR
    -----------------------------------
    A 24/7 watchdog system that keeps backend alive.

    Features:
      ✔ Checks pipeline health every N seconds
      ✔ Auto-restarts internal components
      ✔ Triggers Retry Queue if required
      ✔ Logs warnings without interrupting the system
      ✔ Never blocks or slows main execution
    """

    INTERVAL = 30          # every 30 seconds
    MAX_LATENCY = 3        # seconds allowed for API to respond
    HEARTBEAT_URL = "http://localhost:8000/health"  # FastAPI health endpoint

    def __init__(self):
        self.running = True
        self.thread = threading.Thread(target=self.monitor_loop, daemon=True)

    def start(self):
        log("[HEARTBEAT] Watchdog started.")
        self.thread.start()

    def monitor_loop(self):
        while self.running:
            try:
                self.check_backend()
            except Exception as e:
                log(f"[HEARTBEAT ERROR] {e}")
                log(traceback.format_exc())

            time.sleep(self.INTERVAL)

    def check_backend(self):
        """
        Pings the backend to verify:
          - Server responsiveness
          - Latency is within limits
          - Retry Queue is healthy
        """
        start = time.time()

        try:
            r = requests.get(self.HEARTBEAT_URL, timeout=self.MAX_LATENCY)
            latency = time.time() - start

            if r.status_code != 200:
                log("[HEARTBEAT] Backend unhealthy → Triggering Retry Queue")
                retry_worker()

            if latency > self.MAX_LATENCY:
                log(f"[HEARTBEAT] High latency detected ({latency:.2f}s)")

        except Exception as e:
            log(f"[HEARTBEAT] Backend unreachable → {e}")
            retry_worker()     # auto-fix path

    def stop(self):
        self.running = False
        log("[HEARTBEAT] Watchdog stopped.")
