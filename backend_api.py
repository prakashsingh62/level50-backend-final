from fastapi import APIRouter
from sheet_reader import read_sheet

router = APIRouter()


# ============================
# AUTO-SUGGEST API HELPERS
# ============================

def unique_values(rows, column):
    """Return sorted unique non-empty values for auto-suggest."""
    values = set()

    for r in rows:
        value = r.get(column, "")
        if value and isinstance(value, str):
            values.add(value.strip())

    return sorted(values)


# ============================
# MAIN SUGGEST API GROUP
# ============================

@router.get("/api/suggest/customers")
async def suggest_customers(q: str = ""):
    rows, _ = read_sheet()   # <-- FIXED
    all_values = unique_values(rows, "CUSTOMER NAME")

    if not q:
        return {"suggestions": all_values[:20]}

    q = q.lower()
    matches = [c for c in all_values if q in c.lower()]

    return {"suggestions": matches[:20]}


@router.get("/api/suggest/vendors")
async def suggest_vendors(q: str = ""):
    rows, _ = read_sheet()   # <-- FIXED
    all_values = unique_values(rows, "VENDOR")

    if not q:
        return {"suggestions": all_values[:20]}

    q = q.lower()
    matches = [v for v in all_values if q in v.lower()]

    return {"suggestions": matches[:20]}


@router.get("/api/suggest/status")
async def suggest_status(q: str = ""):
    rows, _ = read_sheet()   # <-- FIXED
    all_values = unique_values(rows, "FINAL STATUS")

    if not q:
        return {"suggestions": all_values[:20]}

    q = q.lower()
    matches = [s for s in all_values if q in s.lower()]

    return {"suggestions": matches[:20]}
