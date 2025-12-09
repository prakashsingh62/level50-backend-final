from fastapi import APIRouter
from logic_engine import run_level50   # same folder import

router = APIRouter()

@router.post("/run")
async def run_api(debug: bool = False):
    """
    Main trigger for Level-50 Automation
    """
    result = run_level50(debug=debug)
    return result
