import json
import re
from datetime import datetime
from fastapi import APIRouter, Query

router = APIRouter()

# ---------------------------------------
# Load JSON cache once at startup
# ---------------------------------------
def load_cache():
    with open("data_cache.json", "r", encoding="utf-8") as f:
        return json.load(f)

RFQ_CACHE = load_cache()


# ---------------------------------------
# Priority Calculate (Based on DUE DATE)
# ---------------------------------------
def calculate_priority(row):
    due = row.get("DUE DATE")
    if not due:
        return None

    try:
        # DD/MM/YYYY format
        due_date = datetime.strptime(due, "%d/%m/%Y")
    except:
        return None

    today = datetime.today()
    days_left = (due_date - today).days

    if days_left <= 2:
        return "HIGH"
    elif 3 <= days_left <= 4:
        return "MEDIUM"
    else:
        return "LOW"


# ---------------------------------------
# Utility: Case-insensitive contains
# ---------------------------------------
def ci_contains(value, keyword):
    if value is None:
        return False
    return keyword.lower() in str(value).lower()


# ---------------------------------------
# Search + Filter + Pagination endpoint
# ---------------------------------------
@router.get("/search-rfq")
def search_rfq(
    q: str | None = Query(None),
    customer: str | None = Query(None),
    vendor: str | None = Query(None),
    priority: str | None = Query(None),
    status: str | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    page: int = 1,
    page_size: int = 50,
):
    results = RFQ_CACHE.copy()

    # -------------------------------
    # 1) Keyword Search
    # -------------------------------
    if q:
        results = [
            row for row in results
            if (
                ci_contains(row.get("CUSTOMER NAME"), q)
                or ci_contains(row.get("VENDOR"), q)
                or ci_contains(row.get("PRODUCT"), q)
                or ci_contains(row.get("RFQ NO"), q)
                or ci_contains(row.get("UID NO"), q)
            )
        ]

    # -------------------------------
    # 2) Filters
    # -------------------------------
    if customer:
        results = [r for r in results if ci_contains(r.get("CUSTOMER NAME"), customer)]

    if vendor:
        results = [r for r in results if ci_contains(r.get("VENDOR"), vendor)]

    # Priority filter (CALCULATED)
    if priority:
        results = [
            r for r in results
            if calculate_priority(r)
            and calculate_priority(r).lower() == priority.lower()
        ]

    if status:
        results = [r for r in results if ci_contains(r.get("STATUS"), status)]

    # Date Range Filter (RFQ DATE)
    if start_date and end_date:
        results = [
            r for r in results
            if start_date <= str(r.get("RFQ DATE", "")) <= end_date
        ]

    # -------------------------------
    # 3) Pagination
    # -------------------------------
    total = len(results)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated = results[start_idx:end_idx]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": paginated,
    }
