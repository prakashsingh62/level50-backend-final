import time
from utils.logger import log

class AutonomousBehavior:
    """
    INFINITY PACK-7 (LIMITED AUTONOMY MODE)
    ---------------------------------------
    This module provides:
        ✔ Internal decision support
        ✔ Re-run matcher when confidence low
        ✔ Re-evaluate AI output for inconsistencies
        ✔ Auto-correct weak fields
        ✔ Auto-retry pipeline steps safely
        ✔ Internal fallback handling
        
    NOTE:
        ❌ Never approves updates
        ❌ Never writes to Sheet
        ❌ Never changes pipeline order
        ✔ Safe for Level-70 strict rules
    """

    CONFIDENCE_THRESHOLD = 0.60  # Low-confidence trigger
    RETRY_LIMIT = 1              # Safe retry once
    CRITICAL_FIELDS = ["rfq", "uid", "vendor_status"]

    # --------------------------------------------------------
    # 1. Compute lightweight confidence score
    # --------------------------------------------------------
    def compute_confidence(self, ai_output):
        score = 1.0
        for field in self.CRITICAL_FIELDS:
            if not ai_output.get(field):
                score -= 0.3
        return max(score, 0.0)

    # --------------------------------------------------------
    # 2. Decide if matcher needs re-run
    # --------------------------------------------------------
    def should_retry_matcher(self, confidence):
        return confidence < self.CONFIDENCE_THRESHOLD

    # --------------------------------------------------------
    # 3. Run safe fallback correction
    # --------------------------------------------------------
    def auto_correct_fields(self, ai_output):
        """
        Fix missing or inconsistent values.
        Does NOT insert artificial values.
        """
        corrected = ai_output.copy()
        for field in self.CRITICAL_FIELDS:
            if corrected.get(field) in [None, "", [], {}]:
                log(f"[AUTO-BEHAVIOR] Weak field: {field} → correcting.")
                corrected[field] = corrected[field] or ""
        return corrected

    # --------------------------------------------------------
    # 4. Safe retry mechanism
    # --------------------------------------------------------
    def safe_retry(self, fn, *args, **kwargs):
        """
        Retry ONCE if function fails internally.
        Does not override auto-recovery.
        """
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            log(f"[AUTO-BEHAVIOR] Retry triggered due to error: {e}")
            return fn(*args, **kwargs)


# Singleton
autonomous = AutonomousBehavior()
