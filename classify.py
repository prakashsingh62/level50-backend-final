from datetime import datetime, timedelta

def parse_date(value):
    if not value:
        return None

    # Already date object?
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, (int, float)):
        # Google Sheets serial date
        base = datetime(1899, 12, 30)
        return (base + timedelta(days=float(value))).date()

    s = str(value).strip()

    # Try multiple formats
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except:
            pass

    return None


def classify_row(r):
    # Skip rows where CONCERN PERSON = NP
    cp = (r.get("CONCERN PERSON", "") or "").strip().upper()
    if cp == "NP":
        return "SKIP"

    due = parse_date(r.get("DUE DATE", ""))
    if not due:
        return "UNKNOWN"

    today = datetime.now().date()
    days = (due - today).days

    if days < 0:
        return "OVERDUE"
    if days <= 2:
        return "HIGH"
    if days <= 3:
        return "MEDIUM"
    if days <= 4:
        return "LOW"

    return "NOACTION"
