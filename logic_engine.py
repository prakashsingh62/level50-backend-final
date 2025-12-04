import datetime
from sheet_reader import read_sheet


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def parse_date(value):
    """Parse date safely from sheet values."""
    if not value:
        return None
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.datetime.strptime(value, "%d-%b-%Y").date()
    except:
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d").date()
        except:
            return None


def days_between(date_obj):
    """Return days between today and the given date."""
    if not date_obj:
        return None
    today = datetime.date.today()
    return (today - date_obj).days


def compute_next_step(row):
    """Compute recommended next step for reminder email."""
    status = (row.get("VENDOR QUOTATION STATUS") or "").strip().lower()
    final = (row.get("FINAL STATUS") or "").strip().lower()
    post_query = (row.get("POST OFFER QUERY") or "").strip()

    if final in ["closed", "completed", "submitted", "regret", "done"]:
        return None  # skip

    if status == "" and row.get("INQUIRY SENT ON"):
        return "Vendor follow-up now"

    if status not in ["", None]:
        return "Prepare immediate offer"

    if post_query:
        return "Respond to client query"

    return "Follow-up now"


# ---------------------------------------------------------
# Classification Engine
# ---------------------------------------------------------

def classify_rows(rows):
    """
    Apply Level-50 rules and produce:
    - Summary counts
    - Section-wise grouped rows
    """

    today = datetime.date.today()
    summary = {
        "high": 0,
        "medium": 0,
        "low": 0,
        "vendor_pending": 0,
        "client_clarifications": 0,
        "post_offer": 0,
        "overdue": 0,
    }

    sections = {
        "high": [],
        "medium": [],
        "low": [],
        "vendor_pending": [],
        "client_clarifications": [],
        "post_offer": [],
        "overdue": [],
    }

    for row in rows:
        final_status = (row.get("FINAL STATUS") or "").strip().lower()
        due_date_str = row.get("DUE DATE")
        due_date = parse_date(due_date_str)
        inquiry_sent = parse_date(row.get("INQUIRY SENT ON"))
        vendor_status = (row.get("VENDOR QUOTATION STATUS") or "").strip()
        post_query = (row.get("POST OFFER QUERY") or "").strip()

        # Skip invalid rows
        if final_status in ["closed", "completed", "submitted", "regret", "done"]:
            continue
        if not due_date:
            continue  # user requested: skip rows without due date

        # Compute fields
        overdue_days = days_between(due_date)
        aging = days_between(due_date)

        next_step = compute_next_step(row)

        row_block = {
            "RFQ": row.get("RFQ NO"),
            "UID": row.get("UID NO"),
            "Customer": row.get("CUSTOMER NAME"),
            "Due": due_date_str,
            "Value": row.get("VEPL OFFER VALUE"),
            "Aging": aging,
            "NextStep": next_step,
        }

        # Priority logic
        days_to_due = (due_date - today).days
        if days_to_due <= 2:
            summary["high"] += 1
            sections["high"].append(row_block)
            continue
        if days_to_due <= 3:
            summary["medium"] += 1
            sections["medium"].append(row_block)
            continue
        if days_to_due <= 4:
            summary["low"] += 1
            sections["low"].append(row_block)
            continue

        # Vendor pending section
        if vendor_status == "" and inquiry_sent:
            if days_between(inquiry_sent) >= 2:
                summary["vendor_pending"] += 1
                sections["vendor_pending"].append(row_block)
                continue

        # Post-offer query
        if post_query:
            summary["post_offer"] += 1
            sections["post_offer"].append(row_block)
            continue

        # Overdue
        if overdue_days is not None and overdue_days > 0:
            summary["overdue"] += 1
            sections["overdue"].append(row_block)
            continue

    return summary, sections


# ---------------------------------------------------------
# PUBLIC FUNCTIONS (Required by routers)
# ---------------------------------------------------------

def prepare_rows_for_email(rows):
    """Used by /email router & debug preview."""
    summary, sections = classify_rows(rows)
    return summary, sections


def run_level50():
    """
    MAIN ENGINE — called by:
    - /run (production)
    - daily cron (Railway)
    - /email preview testing
    """
    rows = read_sheet()
    summary, sections = classify_rows(rows)
    return {
        "summary": summary,
        "sections": sections,
    }
