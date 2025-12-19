"""
rfq_filter_engine.py
Level-80 RFQ Filter Engine (FINAL)

✔ Status Canonicalization
✔ Safe date parsing
✔ Edge-case guards (NO CRASH)
✔ Pagination
✔ Summary counts
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional


# -------------------------------------------------
# STATUS CANONICALIZATION (SINGLE SOURCE OF TRUTH)
# -------------------------------------------------
STATUS_MAP = {
    "VENDOR PENDING": "VENDOR PENDING",
    "PENDING": "VENDOR PENDING",

    "RECEIVED": "QUOTATION RECEIVED",
    "QUOTATION RECEIVED": "QUOTATION RECEIVED",

    "OFFER SUBMITTED": "OFFER SUBMITTED",
    "SUBMITTED": "OFFER SUBMITTED",

    "POST OFFER QUERY": "POST-OFFER QUERY",
    "POST-OFFER QUERY": "POST-OFFER QUERY",

    "CLARIFICATION": "CLARIFICATION",

    "CLOSED": "CLOSED",
}


# -------------------------------------------------
# SAFE HELPERS (NO EXCEPTIONS EVER)
# -------------------------------------------------
def safe_str(v) -> str:
    if v is None:
        return ""
    return str(v).strip()


def safe_int(v, default=0):
    try:
        return int(float(v))
    except Exception:
        return default


def safe_date(v) -> Optional[datetime]:
    """
    Accepts: DD/MM/YYYY, D/M/YYYY, YYYY-MM-DD
    Returns: datetime or None
    """
    if not v:
        return None

    v = str(v).strip()

    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(v, fmt)
        except Exception:
            continue

    return None


def canonical_status(row: Dict) -> str:
    """
    Derives final canonical status safely
    """
    raw = safe_str(
        row.get("FINAL STATUS")
        or row.get("CURRENT STATUS")
        or row.get("VENDOR QUOTATION STATUS")
    ).upper()

    return STATUS_MAP.get(raw, "UNKNOWN")


# -------------------------------------------------
# MAIN FILTER FUNCTION (THIS IS WHAT main.py IMPORTS)
# -------------------------------------------------
def filter_rfqs(
    rows: List[Dict],
    status: Optional[str] = None,
    vendor_pending: Optional[bool] = None,
    overdue: Optional[bool] = None,
    last_n_days: int = 30,
    page: int = 1,
    page_size: int = 50,
):
    """
    FINAL public API used by main.py
    NEVER throws, NEVER crashes
    """

    if not rows:
        return {
            "meta": {
                "total": 0,
                "page": page,
                "page_size": page_size,
            },
            "summary": {},
            "rows": [],
        }

    now = datetime.now()
    cutoff = now - timedelta(days=last_n_days)

    filtered = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        row = dict(row)  # defensive copy

        # --- canonical status ---
        row["canonical_status"] = canonical_status(row)

        # --- RFQ date filter ---
        rfq_date = safe_date(row.get("RFQ DATE"))
        if rfq_date and rfq_date < cutoff:
            continue

        # --- status filter ---
        if status and row["canonical_status"] != status:
            continue

        # --- vendor pending filter ---
        if vendor_pending is True and row["canonical_status"] != "VENDOR PENDING":
            continue

        # --- overdue filter ---
        if overdue is True:
            due = safe_date(row.get("DUE DATE"))
            if not due or due >= now:
                continue

        filtered.append(row)

    # -------------------------------------------------
    # SUMMARY COUNTS
    # -------------------------------------------------
    summary = {
        "VENDOR PENDING": 0,
        "QUOTATION RECEIVED": 0,
        "CLARIFICATION": 0,
        "OFFER SUBMITTED": 0,
        "POST-OFFER QUERY": 0,
        "CLOSED": 0,
        "UNKNOWN": 0,
    }

    for r in filtered:
        s = r.get("canonical_status", "UNKNOWN")
        summary[s] = summary.get(s, 0) + 1

    # -------------------------------------------------
    # PAGINATION
    # -------------------------------------------------
    total = len(filtered)
    start = max((page - 1) * page_size, 0)
    end = start + page_size

    page_rows = filtered[start:end]

    return {
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        "summary": summary,
        "rows": page_rows,
    }


# -------------------------------------------------
# BACKWARD / FUTURE SAFETY ALIAS
# (so imports NEVER break again)
# -------------------------------------------------
apply_filters = filter_rfqs
