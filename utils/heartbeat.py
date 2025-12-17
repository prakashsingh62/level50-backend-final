# utils/heartbeat.py

import time
import threading

try:
    from logger import logger
except Exception:
    import logging
    logger = logging.getLogger(__name__)


class HeartbeatMonitor(threading.Thread):
    """
    Simple background heartbeat.
    """

    def __init__(self, interval=30):
        super().__init__(daemon=True)
        self.interval = interval
        self.running = True

    def run(self):
        while self.running:
            try:
                logger.info("[HEARTBEAT] Backend alive")
            except Exception:
                pass
            time.sleep(self.interval)

    def stop(self):
        self.running = False
