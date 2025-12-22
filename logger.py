import logging
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

_logger = None

def get_logger():
    global _logger

    if _logger:
        return _logger

    logger = logging.getLogger("LEVEL80")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(message)s"
    )
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    _logger = logger
    return logger


def get_ist_now():
    return datetime.now(IST).strftime("%d/%m/%Y %H:%M:%S")
