# ------------------------------------------------------------
# CENTRAL LOGGER — SINGLE SOURCE OF TRUTH
# Path: utils/logger.py
# ------------------------------------------------------------

import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"

# Create main logger
log = logging.getLogger("LEVEL50")
log.setLevel(logging.INFO)

# Prevent duplicate handlers (important for uvicorn reload)
if not log.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    log.addHandler(handler)

# ------------------------------------------------------------
# BACKWARD COMPATIBILITY (DO NOT REMOVE)
# ------------------------------------------------------------
# Some files may still do:
#   from utils.logger import logger
#   from logger import logger
# This keeps everything working safely.

logger = log
