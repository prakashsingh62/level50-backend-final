import json
import re
from datetime import datetime
from fastapi import APIRouter, Query

router = APIRouter()

# ---------------------------------------
# Load JSON CACHE SAFELY (Optional)
# ---------------------------------------
try:
    with open("data_cache.json", "r", encoding="utf-8") as f:
        RFQ_CACHE = json.load(f)
except:
    RFQ_CACHE = []   # 🚀 अब error कभी नहीं आएगा


# ---------------------------------------
# Priority Calculation
# ---------------------------------------
def calc_priority(due_date_str):
    if not due_date_str:
        return "LOW"

    try:
        due = datetime.strptime(due_date_str, "%d/%m/%Y").date()
        today = datetime.today().date()
        diff = (due - today).days

        if diff <= 2:
            return "HIGH"
        elif diff <= 4:
            return "MEDIUM"
        else:
            return "LOW"

    except:
        return "LOW"


# Case-insensitive contains
def ci_contains(value, keyword):
    if value is None:
        return False
    return keyword.lower() in str(value).lower()


# ---------------------------------------
# Search + Filter + Pagination
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
    results = []

    # Add computed PRIORITY field
    for row in RFQ_CACHE:
        row_copy = row.copy()
        row_copy["PRIORITY"] = calc_priority(row_copy.get("DUE DATE"))
        results.append(row_copy)

    # Keyword Search
    if q:
        results = [
            r for r in results
            if (
                ci_contains(r.get("CUSTOMER NAME"), q)
                or ci_contains(r.get("VENDOR"), q)
                or ci_contains(r.get("PRODUCT"), q)
                or ci_contains(r.get("RFQ NO"), q)
                or ci_contains(r.get("UID NO"), q)
            )
        ]

    # Filters
    if customer:
        results = [r for r in results if ci_contains(r.get("CUSTOMER NAME"), customer)]

    if vendor:
        results = [r for r in results if ci_contains(r.get("VENDOR"), vendor)]

    if priority:
        results = [r for r in results if r.get("PRIORITY") == priority.upper()]

    if status:
        results = [r for r in results if ci_contains(r.get("STATUS"), status)]

    # Pagination
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
