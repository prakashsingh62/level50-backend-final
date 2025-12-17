# utils/ai_failover.py

import traceback

# --- SAFE LOGGER IMPORT ---
try:
    from logger import logger
except Exception:
    import logging
    logger = logging.getLogger(__name__)


def ai_failover(primary_func, fallback_func, *args, **kwargs):
    """
    Execute primary function, fallback if it fails.
    Must NEVER crash pipeline.
    """
    try:
        return primary_func(*args, **kwargs)

    except Exception as e:
        try:
            logger.error(f"[AI_FAILOVER] Primary failed: {e}")
            logger.debug(traceback.format_exc())
        except Exception:
            pass

        try:
            logger.warning("[AI_FAILOVER] Running fallback")
            return fallback_func(*args, **kwargs)
        except Exception as e2:
            try:
                logger.critical(f"[AI_FAILOVER] Fallback failed: {e2}")
                logger.debug(traceback.format_exc())
            except Exception:
                pass

            return None
