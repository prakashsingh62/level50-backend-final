from fastapi import APIRouter, Query
from logic_engine import run_level50

router = APIRouter()

@router.post("/run")
def run_api(debug: bool = Query(False)):
    result = run_level50(debug_mode=debug)
    return result
