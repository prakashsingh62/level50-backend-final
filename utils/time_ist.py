# ------------------------------------------------------------
# IST TIME HELPERS (FINAL, SINGLE SOURCE)
# ------------------------------------------------------------

from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

def ist_now():
    """
    Returns timezone-aware IST datetime object
    """
    return datetime.now(IST)

def ist_timestamp():
    """
    Returns IST timestamp string (DD/MM/YYYY HH:MM:SS)
    """
    return ist_now().strftime("%d/%m/%Y %H:%M:%S")
