# utils/anti_corruption.py

import traceback

# --- SAFE LOGGER IMPORT (NO utils.logger ANYWHERE) ---
try:
    from logger import logger
except Exception:
    import logging
    logger = logging.getLogger(__name__)


class AntiCorruptionGuard:
    """
    Prevents invalid / corrupted data from entering pipeline.
    MUST NEVER crash the system.
    """

    @staticmethod
    def validate(data):
        try:
            if data is None:
                raise ValueError("Data is None")

            if isinstance(data, dict) and not data:
                raise ValueError("Empty dict detected")

            if isinstance(data, list) and len(data) == 0:
                raise ValueError("Empty list detected")

            return True

        except Exception as e:
            try:
                logger.error(f"[ANTI_CORRUPTION] Validation failed: {e}")
                logger.debug(traceback.format_exc())
            except Exception:
                pass

            return False
