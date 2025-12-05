from fastapi import APIRouter
from logic_engine import process_sheet

router = APIRouter()

@router.post("/run-level50")
def run_level50_api(payload: dict):
    rows = payload.get("rows", [])
    result = process_sheet(rows)
    return {
        "status": "success",
        "result": result,
    }
