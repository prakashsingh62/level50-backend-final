"""
logger.py
Central logger + IST time helper
Level-80 stable
"""

from datetime import datetime, timezone, timedelta


IST = timezone(timedelta(hours=5, minutes=30))


def get_ist_now() -> str:
    """
    Returns current IST timestamp as string
    Used by pipeline_engine & audit
    """
    return datetime.now(IST).strftime("%d/%m/%Y %H:%M:%S IST")
