# utils/time_ist.py
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

def ist_now():
    return datetime.now(IST)

def ist_date():
    return ist_now().strftime("%d/%m/%Y")

def ist_time():
    return ist_now().strftime("%H:%M:%S")
