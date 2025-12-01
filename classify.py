
from datetime import datetime

def classify_row(r):
    cp=(r.get("CONCERN PERSON","") or "").strip().upper()
    if cp=="NP": return "SKIP"

    try:
        due=datetime.strptime(r.get("DUE DATE",""),"%Y-%m-%d").date()
        today=datetime.now().date()
        days=(due-today).days
    except:
        return "UNKNOWN"

    if days<0: return "OVERDUE"
    if days<=2: return "HIGH"
    if days<=3: return "MEDIUM"
    if days<=4: return "LOW"
    return "NOACTION"
