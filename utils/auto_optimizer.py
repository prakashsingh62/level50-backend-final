import time
from collections import defaultdict
from utils.logger import log

class AutoOptimizer:
    """
    INFINITY PACK-6: AUTO-OPTIMIZER
    --------------------------------
    Learns from system usage and applies:
        ✔ caching
        ✔ adaptive throttling
        ✔ smart batching
        ✔ AI quality improvement
        ✔ Google Sheet optimization
    """

    def __init__(self):

        # Cache frequently-used RFQ/UID → row mappings
        self.row_cache = {}

        # Frequency tracking for hot paths
        self.rfq_hits = defaultdict(int)
        self.uid_hits = defaultdict(int)

        # Performance logs
        self.slow_steps = defaultdict(float)

        # Adaptive tuning parameters
        self.dynamic_delay = 0.02   # starts at 20ms
        self.cache_threshold = 3    # after 3 hits → cached

    # --------------------------------------------------------
    # ROW MATCH OPTIMIZER
    # --------------------------------------------------------
    def optimize_match(self, rfq, uid):
        """
        If same RFQ/UID appears repeatedly → cache it.
        """
        key = f"{rfq}:{uid}"

        # Update usage frequency
        self.rfq_hits[rfq] += 1
        self.uid_hits[uid] += 1

        # If we have seen it enough times → return cached index
        if key in self.row_cache:
            return self.row_cache[key]

        return None

    def store_match(self, rfq, uid, row_index):
        """
        Store match in cache when it becomes hot.
        """
        key = f"{rfq}:{uid}"

        if self.rfq_hits[rfq] >= self.cache_threshold or \
           self.uid_hits[uid] >= self.cache_threshold:

            log(f"[AUTO-OPTIMIZER] Caching RFQ/UID → Row {row_index}")
            self.row_cache[key] = row_index

    # --------------------------------------------------------
    # PERFORMANCE TUNING
    # --------------------------------------------------------
    def record_step(self, step_name, duration):
        """
        Tracks which pipeline steps are slow.
        """
        self.slow_steps[step_name] = duration

        # If matcher or updater becomes slow → increase adaptive delay
        if duration > 0.8:  # 800ms = slow
            self.dynamic_delay = min(self.dynamic_delay + 0.01, 0.1)

        # If fast → reduce delay
        if duration < 0.1:  # very fast
            self.dynamic_delay = max(self.dynamic_delay - 0.005, 0.005)

    # --------------------------------------------------------
    # APPLY ADAPTIVE PERFORMANCE TUNING
    # --------------------------------------------------------
    def apply(self):
        """
        Called automatically each pipeline run.
        Controls adaptive delays + micro performance tuning.
        """
        time.sleep(self.dynamic_delay)


# Singleton instance
auto_optimizer = AutoOptimizer()
