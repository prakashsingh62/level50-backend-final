
import logging

def get_logger():
    logger = logging.getLogger("L50")
    if not logger.handlers:
        h = logging.StreamHandler()
        f = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        h.setFormatter(f)
        logger.addHandler(h)
    logger.setLevel(logging.INFO)
    return logger
