import logging
import os
from datetime import datetime, timedelta, timezone

# IST timezone object
IST = timezone(timedelta(hours=5, minutes=30))

class ISTFormatter(logging.Formatter):
    """Force timestamps to IST regardless of container timezone."""
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, IST)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_logger():
    logger = logging.getLogger("L50")

    # Prevent duplicate handlers
    if not logger.handlers:
        h = logging.StreamHandler()

        fmt = "%(asctime)s | %(levelname)s | %(message)s"
        formatter = ISTFormatter(fmt)
        h.setFormatter(formatter)

        logger.addHandler(h)
        logger.propagate = False   # avoid FastAPI duplicate logs

    # Allow dynamic log levels via env
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(level)

    return logger
