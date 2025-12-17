# ------------------------------------------------------------
# AUTO RECOVERY ENGINE (FUTURE-PROOF)
# ------------------------------------------------------------

import traceback
from logger import get_logger

logger = get_logger("AUTO_RECOVERY")


class AutoRecoveryEngine:
    """
    Wraps any callable safely.
    - Never crashes server
    - Returns structured error
    - Central place for retries / alerts (future)
    """

    def safe_run(self, func, *args, **kwargs):
        try:
            logger.info(f"[AUTO_RECOVERY] Executing: {func.__name__}")
            return func(*args, **kwargs)

        except Exception as e:
            logger.error("[AUTO_RECOVERY] Exception captured")
            logger.error(str(e))
            logger.error(traceback.format_exc())

            return {
                "status": "error",
                "engine": "auto_recovery",
                "error": str(e),
                "trace": traceback.format_exc()
            }


# 🔒 SINGLETON INSTANCE (IMPORTANT)
auto_recovery = AutoRecoveryEngine()
