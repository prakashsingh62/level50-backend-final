from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

def ist_date():
    return datetime.now(IST).strftime("%d/%m/%Y")

def ist_time():
    return datetime.now(IST).strftime("%H:%M:%S")
