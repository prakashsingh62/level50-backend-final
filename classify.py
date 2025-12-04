from datetime import datetime, timedelta

def parse_date(value):
    if not value:
        return None

    # Already a datetime?
    if isinstance(value, datetime):
        return value.date()

    # Google Sheets serial number (float/int)
    if isinstance(value, (int, float)):
        base = datetime(1899, 12, 30)
        return (base + timedelta(days=float(value))).date()

    s = str(value).strip()

    # Try common date formats
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except:
            pass

    return None


def classify_row(r):
    """Return category: HIGH, MEDIUM, LOW, OVERDUE, NOACTION, SKIP."""

    # Skip if NP
    cp = (r.get("CONCERN PERSON", "") or "").strip().upper()
    if cp == "NP":
        return "SKIP"

    # Skip if final status indicates closed/completed/etc
    final = (r.get("FINAL STATUS", "") or "").strip().lower()
    if final in ("closed", "completed", "regret", "submitted", "done"):
        return "SKIP"

    # Parse due date
    due = parse_date(r.get("DUE DATE", ""))
    if not due:
        # Previously UNKNOWN → now SKIP
        return "SKIP"

    today = datetime.now().date()
    diff = (today - due).days  # positive if overdue

    # ----------------------------------------------
    # NEW LEVEL-51 OVERDUE LOGIC
    # ----------------------------------------------
    if diff > 0:  # overdue
        if diff <= 10:
            return "OVERDUE"        # recent overdue
        else:
            return "SKIP"           # older overdue → hide

    # Not overdue — classify normally
    days = (due - today).days

    if days <= 2:
        return "HIGH"
    if days <= 3:
        return "MEDIUM"
    if days <= 4:
        return "LOW"

    return "NOACTION"


def classify_rows(rows):
    """
    Returns: summary, sections_dict
    """
    summary = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
        "OVERDUE": 0,
        "NOACTION": 0,
        "SKIP": 0
    }

    # Removed UNKNOWN entirely
    sections = {
        "HIGH": [],
        "MEDIUM": [],
        "LOW": [],
        "OVERDUE": [],
        "NOACTION": []
        # SKIP not collected (as per your Level-50 design)
    }

    for r in rows:
        category = classify_row(r)

        # count occurrences
        if category in summary:
            summary[category] += 1

        # store actionable rows only
        if category in sections:
            sections[category].append(r)

    return summary, sections
