# logger.py
import logging
import sys
from utils.time_ist import get_ist_now as _get_ist_now

_LOGGERS = {}

def get_logger(name: str = "level80"):
    if name in _LOGGERS:
        return _LOGGERS[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    _LOGGERS[name] = logger
    return logger


def get_ist_now():
    return _get_ist_now()
