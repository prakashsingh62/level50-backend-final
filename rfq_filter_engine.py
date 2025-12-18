from datetime import datetime, date
from typing import List, Dict, Any

DATE_FMT = "%d/%m/%Y"

# -------------------------
# Canonical Status Mapping
# -------------------------
CANONICAL_MAP = {
    "VENDOR PENDING": [
        "", "PENDING", "VENDOR PENDING", "AWAITING", "IN PROCESS"
    ],
    "QUOTATION RECEIVED": [
        "QUOTATION RECEIVED", "QUOTE RECEIVED", "RECEIVED"
    ],
    "CLARIFICATION": [
        "DETAILS REQUIRED", "DETAILKS REQUIRED", "CLARIFICATION",
        "TECHNICAL QUERY", "QUERY",
        "GAD REQUIRED", "FINAL DISCOUNTED PRICE", "DELIVERY TIME/PERIOD"
    ],
    "OFFER SUBMITTED": [
        "SUBMITTED", "SUBNMITTED", "OFFER SUBMITTED",
        "OFFER SENT", "QUOTATION SUBMITTED"
    ],
    "POST-OFFER QUERY": [
        "POST OFFER QUERY", "CLIENT QUERY",
        "DISCOUNT QUERY", "DELIVERY QUERY"
    ],
    "CLOSED": [
        "CLOSED", "REGRET", "LOST",
        "CANCELLED", "ORDER RECEIVED", "NOT REQUIRED"
    ],
}

# -------------------------
# Helpers
# -------------------------
def _norm(val: Any) -> str:
    return str(val).strip().upper() if val else ""

def _parse_date(val: Any):
    try:
        return datetime.strptime(str(val).strip(), DATE_FMT).date()
    except Exception:
        return None

def canonical_status(raw: Any) -> str:
    r = _norm(raw)
    for canon, raws in CANONICAL_MAP.items():
        if r in [x.upper() for x in raws]:
            return canon
    return "UNKNOWN"

# -------------------------
# Clarification Source
# -------------------------
def clarification_source(row: Dict[str, Any]) -> str:
    status = _norm(row.get("CURRENT STATUS"))

    has_client_signal = bool(
        row.get("POST OFFER QUERY")
        or row.get("POST QUERY DATE")
        or status in ["FINAL DISCOUNTED PRICE", "DELIVERY TIME/PERIOD"]
    )

    if status == "GAD REQUIRED":
        if has_client_signal:
            return "CLIENT"
        if row.get("UID NO") or row.get("VENDOR"):
            return "VENDOR"
        return "UNKNOWN"

    if has_client_signal:
        return "CLIENT"

    if status in [
        "DETAILS REQUIRED",
        "DETAILKS REQUIRED",
        "TECHNICAL QUERY",
        "QUERY",
    ]:
        return "VENDOR"

    return "UNKNOWN"

# -------------------------
# Core Filter Engine
# -------------------------
def filter_rfqs(
    rows: List[Dict[str, Any]],
    status: str | None = None,
    vendor_pending: bool | None = None,
    overdue: bool | None = None,
    last_n_days: int = 30,
    page: int = 1,
    page_size: int = 50,
) -> Dict[str, Any]:

    today = date.today()
    cutoff = today.toordinal() - last_n_days

    processed = []

    for row in rows:
        rfq_date = _parse_date(row.get("RFQ DATE"))
        due_date = _parse_date(row.get("DUE DATE"))
        uid_date = _parse_date(row.get("UID DATE"))

        canon = canonical_status(row.get("CURRENT STATUS"))

        # Date window
        if rfq_date and rfq_date.toordinal() < cutoff:
            continue

        # Vendor pending rule
        is_vendor_pending = (
            canon == "VENDOR PENDING"
            and (uid_date or rfq_date)
            and (today - (uid_date or rfq_date)).days >= 2
        )

        # Overdue rule
        is_overdue = bool(due_date and today > due_date)

        if vendor_pending is not None and is_vendor_pending != vendor_pending:
            continue

        if overdue is not None and is_overdue != overdue:
            continue

        if status and canon != status.upper():
            continue

        out = dict(row)
        out["canonical_status"] = canon

        if canon == "CLARIFICATION":
            out["clarification_source"] = clarification_source(row)

        processed.append(out)

    total = len(processed)

    start = (page - 1) * page_size
    end = start + page_size
    page_rows = processed[start:end]

    summary = {
        "VENDOR PENDING": 0,
        "QUOTATION RECEIVED": 0,
        "CLARIFICATION": 0,
        "OFFER SUBMITTED": 0,
        "POST-OFFER QUERY": 0,
        "CLOSED": 0,
        "UNKNOWN": 0,
    }

    for r in processed:
        summary[r["canonical_status"]] += 1

    return {
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        "summary": summary,
        "rows": page_rows,
    }
