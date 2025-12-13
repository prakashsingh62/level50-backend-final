import time
import threading

# ------------------------------------------------------------
# SMART THROTTLE ENGINE  (Infinity Pack-3)
# ------------------------------------------------------------
# Prevents overload, API choke, and concurrent sheet updates.
# ------------------------------------------------------------

class SmartThrottle:
    MAX_REQUESTS_PER_SECOND = 5
    ADAPTIVE_DELAY = 0.05   # 50 ms micro delay
    SHEET_LOCK = threading.Lock()

    def __init__(self):
        self.request_count = 0
        self.last_reset = time.time()

        # Lock for counting safe requests
        self.counter_lock = threading.Lock()

    # --------------------------------------------------------
    # Rate Limit Controller
    # --------------------------------------------------------
    def limit_rate(self):
        with self.counter_lock:
            now = time.time()

            # Reset count every second
            if now - self.last_reset >= 1:
                self.request_count = 0
                self.last_reset = now

            # If too many requests → delay
            if self.request_count >= self.MAX_REQUESTS_PER_SECOND:
                time.sleep(self.ADAPTIVE_DELAY)

            self.request_count += 1

    # --------------------------------------------------------
    # Sheet-Safe Lock (Critical)
    # --------------------------------------------------------
    def acquire_sheet_lock(self):
        """
        Ensures ONLY ONE Google Sheet update is running at any time.
        Prevents corruption and API choking.
        """
        self.SHEET_LOCK.acquire()

    def release_sheet_lock(self):
        self.SHEET_LOCK.release()

    # --------------------------------------------------------
    # Adaptive Delay (Load Balancing)
    # --------------------------------------------------------
    def adaptive_delay(self):
        """
        Auto-adjust delay under high system load.
        """
        time.sleep(self.ADAPTIVE_DELAY)


smart_throttle = SmartThrottle()
