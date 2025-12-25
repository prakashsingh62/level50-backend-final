# ------------------------------------------------------------
# TIME UTIL — IST (FINAL, PROD-SAFE)
# ------------------------------------------------------------

from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

def ist_timestamp() -> str:
    """
    Returns current IST timestamp as ISO string.
    Example: 25/12/2025 15:10:02
    """
    return datetime.now(IST).strftime("%d/%m/%Y %H:%M:%S")
