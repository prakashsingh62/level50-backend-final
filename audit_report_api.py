from fastapi import APIRouter, Query
from sheet_reader import read_audit_report_sheet

router = APIRouter()

@router.get("/api/audit/report")
def get_audit_report(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=200)
):
    """
    Server-side pagination enabled.
    Pagination is OPTIONAL (backward compatible).
    """

    # Existing logic — DO NOT CHANGE SOURCE
    rows = read_audit_report_sheet()  # must return list[dict]

    if not isinstance(rows, list):
        rows = []

    total = len(rows)

    start = (page - 1) * limit
    end = start + limit

    return {
        "rows": rows[start:end],
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit
    }
