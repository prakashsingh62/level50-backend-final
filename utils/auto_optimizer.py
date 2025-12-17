# utils/auto_optimizer.py

try:
    from logger import logger
except Exception:
    import logging
    logger = logging.getLogger(__name__)


def auto_optimizer(func, *args, **kwargs):
    """
    Auto optimizer wrapper.
    This function MUST exist for pipeline_engine import.
    """
    try:
        logger.info("[AUTO_OPTIMIZER] Optimizer started")
        return func(*args, **kwargs)
    except Exception as e:
        try:
            logger.error(f"[AUTO_OPTIMIZER] Failed: {e}")
        except Exception:
            pass
        return None
