from datetime import datetime
from typing import List, Dict, Any

# ----------------------------
# STATUS CANONICALIZATION
# ----------------------------

STATUS_MAP = {
    "RECEIVED": "QUOTATION_RECEIVED",
    "ON WHATSAPP": "QUOTATION_RECEIVED",
    "WHATSAPP": "QUOTATION_RECEIVED",

    "SUBMITTED": "OFFER_SUBMITTED",
    "OFFER SUBMITTED": "OFFER_SUBMITTED",

    "POST OFFER QUERY": "POST_OFFER_QUERY",
    "POST-OFFER QUERY": "POST_OFFER_QUERY",

    "CLOSED": "CLOSED",
}

CANONICAL_STATUSES = {
    "VENDOR_PENDING",
    "QUOTATION_RECEIVED",
    "OFFER_SUBMITTED",
    "POST_OFFER_QUERY",
    "CLOSED",
    "UNKNOWN",
}

def canonical_status(raw):
    if not raw:
        return "UNKNOWN"

    s = str(raw).strip().upper()
    return STATUS_MAP.get(s, s if s in CANONICAL_STATUSES else "UNKNOWN")


# ----------------------------
# EDGE-CASE SAFE HELPERS
# ----------------------------

def safe_date(val):
    if not val:
        return None
    try:
        return datetime.strptime(str(val).strip(), "%d/%m/%Y")
    except Exception:
        return None


def is_vendor_pending(row: Dict[str, Any]) -> bool:
    return (
        not row.get("VENDOR QUOTATION STATUS")
        and bool(row.get("INQUIRY SENT ON"))
    )


def is_overdue(row: Dict[str, Any]) -> bool:
    due = safe_date(row.get("DUE DATE"))
    if not due:
        return False
    return due < datetime.now()


# ----------------------------
# MAIN FILTER ENGINE
# ----------------------------

def apply_filters(
    rows: List[Dict[str, Any]],
    status: str = None,
    vendor_pending: bool = False,
    overdue: bool = False,
):
    filtered = []

    for row in rows:
        row["canonical_status"] = canonical_status(
            row.get("FINAL STATUS") or row.get("CURRENT STATUS")
        )

        if status and row["canonical_status"] != status:
            continue

        if vendor_pending and not is_vendor_pending(row):
            continue

        if overdue and not is_overdue(row):
            continue

        filtered.append(row)

    return filtered


# ----------------------------
# SUMMARY BUILDER
# ----------------------------

def build_summary(rows: List[Dict[str, Any]]):
    summary = {k: 0 for k in CANONICAL_STATUSES}

    for r in rows:
        s = r.get("canonical_status", "UNKNOWN")
        summary[s] = summary.get(s, 0) + 1

    return summary
