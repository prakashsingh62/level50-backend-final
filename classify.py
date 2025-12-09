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

    # Skip rows where FINAL STATUS is closed/completed/etc
    final = (r.get("FINAL STATUS", "") or "").strip().lower()
    if final in ("closed", "completed", "regret", "submitted", "done"):
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


# NEW FUNCTION — Required by logic_engine.py
def classify_rows(rows):
    """
    logic_engine.py expects this function.
    It must return:
        summary, sections_dict
    """

    summary = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
        "OVERDUE": 0,
        "UNKNOWN": 0,
        "NOACTION": 0,
        "SKIP": 0
    }

    sections = {
        "HIGH": [],
        "MEDIUM": [],
        "LOW": [],
        "OVERDUE": [],
        "UNKNOWN": [],
        "NOACTION": []
    }

    for r in rows:
        category = classify_row(r)

        # Count all
        if category in summary:
            summary[category] += 1

        # Store rows only if actionable
        if category in sections:
            sections[category].append(r)

    return summary, sections
